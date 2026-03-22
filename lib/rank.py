#!/usr/bin/env python3
"""
Compute skill rankings from GitHub signals and local analysis.

Usage:
    python3 lib/rank.py                          # Rank with defaults
    python3 lib/rank.py --signals signals.json    # Use pre-fetched signals
    python3 lib/rank.py --json                    # Output JSON to stdout

Reads: skills-manifest.json
Writes: skills-manifest.json (updated rankings), RANKINGS.md
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJ_ROOT / "skills-manifest.json"
RANKINGS_PATH = PROJ_ROOT / "RANKINGS.md"

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


def update_manifest(manifest: dict, scores: dict, repo_signals: dict) -> None:
    """Write scores back into the manifest."""
    for name, skill_data in manifest.get("skills", {}).items():
        if name in scores:
            skill_data["ranking"] = {
                "score": scores[name]["score"],
                "tier": scores[name]["tier"],
                "signals": {
                    "depth": scores[name]["depth"],
                    "mentions": scores[name]["mentions"],
                    "desc_quality": scores[name]["desc_score"],
                },
            }

    manifest.setdefault("ranking", {})
    manifest["ranking"]["last_ranked"] = datetime.now(timezone.utc).isoformat()
    manifest["ranking"]["repo_signals"] = repo_signals

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def generate_rankings_md(scores: dict, repo_signals: dict) -> None:
    """Generate RANKINGS.md leaderboard."""
    ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "# Skill Rankings",
        "",
        f"Last updated: {now}",
        "",
        f"**Repo signals**: {repo_signals.get('stars', 0)} stars, "
        f"{repo_signals.get('forks', 0)} forks, "
        f"{repo_signals.get('contributors', 0)} contributors, "
        f"{repo_signals.get('discussions', 0)} discussions",
        "",
        "## Ranking Method",
        "",
        "Each skill is scored 0-100 based on:",
        "- **Depth** (40%): file count and content size as a proxy for comprehensiveness",
        "- **Community** (20%): issue/discussion mentions on GitHub",
        "- **Documentation** (10%): quality of skill description",
        "- **Repo health** (30%): stars, forks, contributors, discussions",
        "- **Phase weight**: build/ship/acquire skills get a slight boost",
        "",
        "## Tiers",
        "",
        "| Tier | Score | Meaning |",
        "|------|-------|---------|",
    ]
    for _, tier in TIER_THRESHOLDS:
        label, emoji = TIER_LABELS[tier]
        lo = [t for t, _ in TIER_THRESHOLDS if _ == tier][0]
        hi_idx = TIER_THRESHOLDS.index((lo, tier))
        hi = TIER_THRESHOLDS[hi_idx - 1][0] - 1 if hi_idx > 0 else 100
        lines.append(f"| {emoji} {tier} | {lo}-{hi} | {label} |")

    lines += [
        "",
        "## Leaderboard",
        "",
        "| Rank | Skill | Phase | Score | Tier |",
        "|------|-------|-------|-------|------|",
    ]
    for i, (name, data) in enumerate(ranked, 1):
        _, emoji = TIER_LABELS.get(data["tier"], ("", ""))
        lines.append(
            f"| {i} | `{name}` | {data['category']} | {data['score']} | {emoji} {data['tier']} |"
        )

    # Per-category breakdown
    lines += ["", "## By Phase", ""]
    cats: dict[str, list] = {}
    for name, data in ranked:
        cats.setdefault(data["category"], []).append((name, data))

    for cat in sorted(cats):
        skills = cats[cat]
        lines.append(f"### {cat}")
        lines.append("")
        lines.append("| Skill | Score | Tier |")
        lines.append("|-------|-------|------|")
        for name, data in skills:
            _, emoji = TIER_LABELS.get(data["tier"], ("", ""))
            lines.append(f"| `{name}` | {data['score']} | {emoji} {data['tier']} |")
        lines.append("")

    with open(RANKINGS_PATH, "w") as f:
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
    update_manifest(manifest, scores, repo_signals)
    generate_rankings_md(scores, repo_signals)

    ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

    if json_output:
        print(json.dumps({"ranked": [{**v, "name": k} for k, v in ranked]}, indent=2))
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
