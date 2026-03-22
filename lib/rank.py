#!/usr/bin/env python3
"""
Compute skill rankings from GitHub signals and local analysis.

Usage:
    python3 lib/rank.py                          # Rank with defaults
    python3 lib/rank.py --signals signals.json    # Use pre-fetched signals
    python3 lib/rank.py --json                    # Output JSON to stdout

Reads: skills-manifest.json
Writes: skills-manifest.json (updated rankings), rankings.json, RANKINGS.md
"""

import json
import os
from scenarios import get_all_scenarios
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJ_ROOT / "skills-manifest.json"
RANKINGS_JSON_PATH = PROJ_ROOT / "rankings.json"
RANKINGS_MD_PATH = PROJ_ROOT / "RANKINGS.md"

# Category weights for the journey-based taxonomy
CATEGORY_WEIGHTS = {
    "1-validate": 1.2,
    "2-build": 1.2,
    "3-ship": 1.3,
    "4-get-found": 1.0,
    "5-acquire": 1.1,
    "6-convert": 1.1,
    "7-retain": 1.0,
    "8-power-tools": 1.1,
}

TIER_THRESHOLDS = [
    (80, "S"),
    (60, "A"),
    (40, "B"),
    (20, "C"),
    (0, "D"),
]

TIER_LABELS = {
    "S": ("Best-in-class, comprehensive, well-documented", "🏆"),
    "A": ("High quality, feature-rich", "⭐"),
    "B": ("Solid, does the job well", "✅"),
    "C": ("Good baseline", "📋"),
    "D": ("Minimal, could use improvement", "📝"),
}


def load_manifest() -> dict:
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def compute_scores(
    manifest: dict,
    repo_signals: dict,
    skill_mentions: dict[str, int],
) -> dict[str, dict]:
    """Compute normalized scores for all skills."""
    skills = manifest.get("skills", {})
    if not skills:
        return {}

    max_size = max((s.get("size_bytes", 1) for s in skills.values()), default=1)
    max_files = max((s.get("file_count", 1) for s in skills.values()), default=1)

    scores = {}
    for name, info in skills.items():
        size = info.get("size_bytes", 0)
        files = info.get("file_count", 0)
        category = info.get("category", "8-power-tools")

        # Depth score (0-40)
        depth = 0.0
        if size > 0 and files > 0:
            norm_size = size / max_size
            norm_files = files / max_files
            depth = (norm_size * 0.6 + norm_files * 0.4) * 40

        # Mention score (0-20)
        mentions = skill_mentions.get(name, 0)
        mention_score = min(mentions * 5, 20)

        # Description quality (0-10)
        desc_score = 10 if info.get("description") else 3

        # Repo-level signal bonus (0-30)
        repo_bonus = min(
            repo_signals.get("stars", 0) * 0.5
            + repo_signals.get("forks", 0) * 1.0
            + repo_signals.get("contributors", 1) * 2.0
            + repo_signals.get("discussions", 0) * 0.3,
            30,
        )

        cat_weight = CATEGORY_WEIGHTS.get(category, 1.0)
        raw_score = (depth + mention_score + desc_score + repo_bonus) * cat_weight

        scores[name] = {
            "raw_score": round(raw_score, 1),
            "depth": round(depth, 1),
            "mentions": mentions,
            "mention_score": round(mention_score, 1),
            "desc_score": desc_score,
            "repo_bonus": round(repo_bonus, 1),
            "category_weight": cat_weight,
            "category": category,
        }

    # Normalize to 0-100
    max_score = max((s["raw_score"] for s in scores.values()), default=1)
    if max_score == 0:
        max_score = 1
    for s in scores.values():
        s["score"] = round(s["raw_score"] / max_score * 100, 1)

    # Assign tiers
    for s in scores.values():
        for threshold, tier in TIER_THRESHOLDS:
            if s["score"] >= threshold:
                s["tier"] = tier
                break

    return scores


def load_rankings() -> dict:
    """Load existing rankings.json if it exists."""
    if RANKINGS_JSON_PATH.exists():
        with open(RANKINGS_JSON_PATH) as f:
            return json.load(f)
    return {}


def save_rankings(rankings: dict) -> None:
    """Write rankings.json — the source of truth for all ranking data."""
    with open(RANKINGS_JSON_PATH, "w") as f:
        json.dump(rankings, f, indent=2)
        f.write("\n")


def build_rankings_config(
    scores: dict,
    repo_signals: dict,
    manifest: dict,
) -> dict:
    """
    Build the rankings.json config — structured for both scripts and LLMs.

    Schema:
      meta:           when/how rankings were computed
      repo_signals:   GitHub-level signals (stars, forks, etc.)
      scoring:        weights and tier thresholds (so LLMs understand the formula)
      leaderboard:    ordered list of {name, score, tier, phase, ...}
      by_phase:       skills grouped by startup journey phase
      by_tier:        skills grouped by quality tier
      skills:         per-skill detail (score, tier, signals breakdown)
    """
    ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    now = datetime.now(timezone.utc).isoformat()

    # Load previous rankings to preserve manual overrides or user ratings
    previous = load_rankings()
    user_overrides = previous.get("user_overrides", {})

    # Per-skill detail
    skills_detail = {}
    for name, data in scores.items():
        desc = manifest.get("skills", {}).get(name, {}).get("description", "")
        phases = manifest.get("skills", {}).get(name, {}).get("phases", [data["category"]])
        entry = {
            "score": data["score"],
            "tier": data["tier"],
            "phase": data["category"],
            "all_phases": phases,
            "description": desc,
            "signals": {
                "depth": data["depth"],
                "mentions": data["mentions"],
                "mention_score": data["mention_score"],
                "desc_quality": data["desc_score"],
                "repo_bonus": data["repo_bonus"],
                "category_weight": data["category_weight"],
                "raw_score": data["raw_score"],
            },
        }
        # Preserve user overrides
        if name in user_overrides:
            entry["user_override"] = user_overrides[name]
        skills_detail[name] = entry

    # Leaderboard (ordered)
    leaderboard = []
    for rank, (name, data) in enumerate(ranked, 1):
        leaderboard.append({
            "rank": rank,
            "name": name,
            "score": data["score"],
            "tier": data["tier"],
            "phase": data["category"],
        })

    # Group by phase
    by_phase: dict[str, list] = {}
    for name, data in ranked:
        phase = data["category"]
        by_phase.setdefault(phase, []).append({
            "name": name, "score": data["score"], "tier": data["tier"],
        })

    # Group by tier
    by_tier: dict[str, list] = {}
    for name, data in ranked:
        tier = data["tier"]
        by_tier.setdefault(tier, []).append({
            "name": name, "score": data["score"], "phase": data["category"],
        })

    # Build scenario index
    scenarios = get_all_scenarios()

    rankings = {
        "_comment": "Source of truth for skill rankings. Read/write by scripts and LLMs.",
        "_schema": {
            "meta": "{last_updated: ISO8601, total_skills: int, total_scenarios: int, version: str}",
            "repo_signals": "{stars: int, forks: int, open_issues: int, contributors: int, discussions: int}",
            "scoring.weights": "{depth: str, community: str, documentation: str, repo_health: str}",
            "scoring.category_weights": "{phase_id: float} — multiplier per phase",
            "scoring.tiers": "{tier_letter: {min_score: int, label: str}}",
            "leaderboard": "[{rank: int, name: str, score: float, tier: str, phase: str}] — ordered best first",
            "scenarios.<phase_id>": "{label: str, scenarios: {scenario_id: {trigger: str, problem: str, skills: [str]}}}",
            "by_phase.<phase_id>": "[{name: str, score: float, tier: str}]",
            "by_tier.<tier>": "[{name: str, score: float, phase: str}]",
            "skills.<name>": "{score: float, tier: str, phase: str, all_phases: [str], description: str, signals: {depth, mentions, mention_score, desc_quality, repo_bonus, category_weight, raw_score}}",
            "user_overrides.<name>": "{score: float?, tier: str?} — manual overrides preserved across re-ranks",
            "_writable_fields": ["user_overrides"],
            "_read_only_fields": ["meta", "repo_signals", "scoring", "leaderboard", "scenarios", "by_phase", "by_tier", "skills", "tier_summary"],
            "_query_examples": {
                "best_skill_for_problem": "scenarios['4-get-found']['scenarios']['not-ranking-in-google']['skills']",
                "top_5_overall": "leaderboard[:5]",
                "all_s_tier": "by_tier['S']",
                "skill_score": "skills['ship']['score']",
                "skills_in_phase": "by_phase['3-ship']",
                "search_by_keyword": "python3 lib/scenarios.py --search 'bug'",
            },
        },
        "meta": {
            "last_updated": now,
            "total_skills": len(scores),
            "total_scenarios": sum(len(p["scenarios"]) for p in scenarios.values()),
            "version": "2.0.0",
            "generated_by": "lib/rank.py",
        },
        "repo_signals": repo_signals,
        "scoring": {
            "weights": {
                "depth": "40% — file count and content size",
                "community": "20% — issue/discussion mentions",
                "documentation": "10% — description quality",
                "repo_health": "30% — stars, forks, contributors",
            },
            "category_weights": {k: v for k, v in CATEGORY_WEIGHTS.items()},
            "tiers": {
                tier: {"min_score": threshold, "label": TIER_LABELS[tier][0]}
                for threshold, tier in TIER_THRESHOLDS
            },
        },
        "tier_summary": {
            tier: len(entries) for tier, entries in by_tier.items()
        },
        "leaderboard": leaderboard,
        "scenarios": scenarios,
        "by_phase": by_phase,
        "by_tier": by_tier,
        "skills": skills_detail,
        "user_overrides": user_overrides,
    }

    return rankings


def update_manifest(manifest: dict, scores: dict, repo_signals: dict) -> None:
    """Write ranking summary back into skills-manifest.json."""
    for name, skill_data in manifest.get("skills", {}).items():
        if name in scores:
            skill_data["ranking"] = {
                "score": scores[name]["score"],
                "tier": scores[name]["tier"],
            }

    manifest.setdefault("ranking", {})
    manifest["ranking"]["last_ranked"] = datetime.now(timezone.utc).isoformat()
    manifest["ranking"]["repo_signals"] = repo_signals

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def generate_rankings_md(rankings: dict) -> None:
    """Generate RANKINGS.md from rankings.json (human-readable view)."""
    meta = rankings.get("meta", {})
    repo = rankings.get("repo_signals", {})
    leaderboard = rankings.get("leaderboard", [])
    by_phase = rankings.get("by_phase", {})
    tier_summary = rankings.get("tier_summary", {})

    lines = [
        "# Skill Rankings",
        "",
        "<!-- Auto-generated from rankings.json — do not edit manually -->",
        "",
        f"Last updated: {meta.get('last_updated', 'unknown')[:10]}",
        "",
        f"**Repo signals**: {repo.get('stars', 0)} stars, "
        f"{repo.get('forks', 0)} forks, "
        f"{repo.get('contributors', 0)} contributors, "
        f"{repo.get('discussions', 0)} discussions",
        "",
        f"**Tier breakdown**: "
        + ", ".join(f"{TIER_LABELS[t][1]} {t}: {tier_summary.get(t, 0)}" for t in ["S", "A", "B", "C", "D"] if tier_summary.get(t, 0) > 0),
        "",
        "## Scoring",
        "",
        "| Signal | Weight |",
        "|--------|--------|",
        "| Depth (files + size) | 40% |",
        "| Community mentions | 20% |",
        "| Documentation quality | 10% |",
        "| Repo health (stars, forks) | 30% |",
        "",
        "## Leaderboard",
        "",
        "| Rank | Skill | Phase | Score | Tier |",
        "|------|-------|-------|-------|------|",
    ]
    for entry in leaderboard:
        _, emoji = TIER_LABELS.get(entry["tier"], ("", ""))
        lines.append(
            f"| {entry['rank']} | `{entry['name']}` | {entry['phase']} "
            f"| {entry['score']} | {emoji} {entry['tier']} |"
        )

    lines += ["", "## By Phase", ""]
    for phase in sorted(by_phase):
        skills = by_phase[phase]
        lines.append(f"### {phase}")
        lines.append("")
        lines.append("| Skill | Score | Tier |")
        lines.append("|-------|-------|------|")
        for s in skills:
            _, emoji = TIER_LABELS.get(s["tier"], ("", ""))
            lines.append(f"| `{s['name']}` | {s['score']} | {emoji} {s['tier']} |")
        lines.append("")

    with open(RANKINGS_MD_PATH, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")


SCENARIOS_MD_PATH = PROJ_ROOT / "SCENARIOS.md"


def generate_scenarios_md(rankings: dict) -> None:
    """Generate SCENARIOS.md — decision-tree format for humans."""
    scenarios_data = rankings.get("scenarios", {})
    skills_data = rankings.get("skills", {})

    lines = [
        "# Find the Right Skill",
        "",
        "<!-- Auto-generated from rankings.json — do not edit manually -->",
        "",
        "Start with your situation. Find the phase you're in, then the problem you're facing.",
        "",
    ]

    # Table of contents
    lines.append("## Phases")
    lines.append("")
    for phase_id in sorted(scenarios_data):
        phase = scenarios_data[phase_id]
        count = len(phase["scenarios"])
        lines.append(f"- [{phase['label']}](#{phase_id}) ({count} scenarios)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Each phase as a table
    for phase_id in sorted(scenarios_data):
        phase = scenarios_data[phase_id]
        lines.append(f"## {phase['label']}")
        lines.append("")
        lines.append("| Situation | Problem | Skill |")
        lines.append("|-----------|---------|-------|")

        for scenario_id, scenario in phase["scenarios"].items():
            skill_badges = []
            for skill_name in scenario["skills"]:
                info = skills_data.get(skill_name, {})
                tier = info.get("tier", "?")
                _, emoji = TIER_LABELS.get(tier, ("", ""))
                skill_badges.append(f"`{skill_name}` {emoji}")

            trigger = scenario["trigger"]
            problem = scenario["problem"]
            skills_col = ", ".join(skill_badges)
            lines.append(f"| {trigger} | {problem} | {skills_col} |")

        lines.append("")

    with open(SCENARIOS_MD_PATH, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")


def main():
    json_output = "--json" in sys.argv

    # Load signals from file or env
    signals_file = None
    for i, arg in enumerate(sys.argv):
        if arg == "--signals" and i + 1 < len(sys.argv):
            signals_file = sys.argv[i + 1]

    if signals_file and os.path.exists(signals_file):
        with open(signals_file) as f:
            data = json.load(f)
        repo_signals = data.get("repo_signals", {})
        skill_mentions = data.get("skill_mentions", {})
    else:
        repo_signals = {
            "stars": int(os.environ.get("STARS", 0)),
            "forks": int(os.environ.get("FORKS", 0)),
            "open_issues": int(os.environ.get("OPEN_ISSUES", 0)),
            "contributors": int(os.environ.get("CONTRIBUTORS", 1)),
            "discussions": int(os.environ.get("DISCUSSIONS", 0)),
        }
        try:
            skill_mentions = json.loads(os.environ.get("SKILL_MENTIONS", "{}"))
        except (json.JSONDecodeError, TypeError):
            skill_mentions = {}

    manifest = load_manifest()
    scores = compute_scores(manifest, repo_signals, skill_mentions)

    # 1. Build rankings.json (source of truth)
    rankings = build_rankings_config(scores, repo_signals, manifest)
    save_rankings(rankings)

    # 2. Update manifest with ranking summary
    update_manifest(manifest, scores, repo_signals)

    # 3. Generate RANKINGS.md and SCENARIOS.md from rankings.json
    generate_rankings_md(rankings)
    generate_scenarios_md(rankings)

    ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

    if json_output:
        print(json.dumps(rankings, indent=2))
    else:
        tier_counts = {}
        for _, d in ranked:
            tier_counts[d["tier"]] = tier_counts.get(d["tier"], 0) + 1

        print(f"\nSkills ranked: {len(ranked)}")
        for tier in ["S", "A", "B", "C", "D"]:
            if tier in tier_counts:
                print(f"  {tier}-tier: {tier_counts[tier]}")

        print(f"\nTop 10:")
        for i, (name, data) in enumerate(ranked[:10], 1):
            print(f"  {i}. {name} ({data['category']}) — {data['score']} [{data['tier']}]")


if __name__ == "__main__":
    main()
