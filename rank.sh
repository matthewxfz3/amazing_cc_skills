#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# amazing_cc_skills — Skill Ranking Engine
#
# Fetches GitHub signals (stars, forks, issues, discussions, contributors)
# and computes a composite quality score for the skill collection.
#
# Since all skills live in one repo, repo-level signals apply globally.
# Per-skill ranking uses: file size (proxy for depth), issue/discussion
# mentions, and community engagement via GitHub Discussions labels.
#
# Usage:
#   ./rank.sh                  # Full ranking with GitHub API
#   ./rank.sh --offline        # Rank using local signals only
#   ./rank.sh --json           # Output raw JSON
#   ./rank.sh --leaderboard    # Show top skills per category
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$SCRIPT_DIR/skills-manifest.json"
RANKINGS_FILE="$SCRIPT_DIR/RANKINGS.md"
REPO="matthewxfz3/amazing_cc_skills"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

OFFLINE=false
JSON_OUTPUT=false
LEADERBOARD=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --offline)   OFFLINE=true; shift ;;
        --json)      JSON_OUTPUT=true; shift ;;
        --leaderboard) LEADERBOARD=true; shift ;;
        -h|--help)
            echo "Usage: $(basename "$0") [--offline] [--json] [--leaderboard]"
            exit 0 ;;
        *) shift ;;
    esac
done

# ============================================================================
# Step 1: Fetch repo-level GitHub signals
# ============================================================================
STARS=0
FORKS=0
OPEN_ISSUES=0
CONTRIBUTORS=0
DISCUSSIONS=0

if [[ "$OFFLINE" == false ]] && command -v gh &>/dev/null; then
    echo -e "${CYAN}Fetching GitHub signals for ${REPO}...${NC}"

    # Repo stats
    REPO_JSON=$(gh api "repos/$REPO" 2>/dev/null || echo "{}")
    STARS=$(echo "$REPO_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('stargazers_count', 0))" 2>/dev/null || echo 0)
    FORKS=$(echo "$REPO_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('forks_count', 0))" 2>/dev/null || echo 0)
    OPEN_ISSUES=$(echo "$REPO_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('open_issues_count', 0))" 2>/dev/null || echo 0)

    # Contributors count
    CONTRIBUTORS=$(gh api "repos/$REPO/contributors" --paginate 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 1)

    # Discussions count (if enabled)
    DISCUSSIONS=$(gh api graphql -f query='{repository(owner:"matthewxfz3",name:"amazing_cc_skills"){discussions{totalCount}}}' 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['repository']['discussions']['totalCount'])" 2>/dev/null || echo 0)

    # Per-skill issue mentions
    echo -e "${CYAN}Scanning issues for skill mentions...${NC}"
    ISSUE_MENTIONS=$(gh api "repos/$REPO/issues?state=all&per_page=100" 2>/dev/null || echo "[]")
else
    echo -e "${YELLOW}Offline mode: using local signals only${NC}"
    ISSUE_MENTIONS="[]"
fi

# ============================================================================
# Step 2: Compute per-skill scores
# ============================================================================
echo -e "${CYAN}Computing skill rankings...${NC}"

python3 << 'PYEOF'
import json, os, sys, math

script_dir = os.environ.get("SCRIPT_DIR", ".")
manifest_path = os.path.join(script_dir, "skills-manifest.json")
rankings_path = os.path.join(script_dir, "RANKINGS.md")
skills_dir = os.path.join(script_dir, "skills")

# Load manifest
with open(manifest_path) as f:
    manifest = json.load(f)

# GitHub signals (from env)
repo_signals = {
    "stars": int(os.environ.get("STARS", 0)),
    "forks": int(os.environ.get("FORKS", 0)),
    "open_issues": int(os.environ.get("OPEN_ISSUES", 0)),
    "contributors": int(os.environ.get("CONTRIBUTORS", 1)),
    "discussions": int(os.environ.get("DISCUSSIONS", 0)),
}

# Parse issue mentions
try:
    issue_data = json.loads(os.environ.get("ISSUE_MENTIONS", "[]"))
except:
    issue_data = []

skill_mentions = {}
for issue in issue_data:
    title = (issue.get("title", "") + " " + (issue.get("body") or "")).lower()
    for skill_name in manifest.get("skills", {}):
        if skill_name.replace("-", " ") in title or skill_name in title:
            skill_mentions[skill_name] = skill_mentions.get(skill_name, 0) + 1

# Scoring criteria and weights
# - depth_score: file_count * log(size_bytes) — proxy for skill richness
# - mention_score: how often this skill is mentioned in issues/discussions
# - category_boost: some categories have higher baseline value
# - recency_score: recently updated skills get a small boost

category_weights = {
    "engineering": 1.2,
    "shipping": 1.3,
    "qa-testing": 1.2,
    "safety": 1.1,
    "design": 1.1,
    "marketing": 1.0,
    "email-outreach": 1.0,
    "seo": 1.0,
    "cro": 1.1,
    "growth": 1.0,
    "sales": 1.0,
    "documents": 1.0,
    "factories": 1.3,
    "security": 1.2,
    "integrations": 1.1,
}

scores = {}
max_size = max(s.get("size_bytes", 1) for s in manifest["skills"].values())
max_files = max(s.get("file_count", 1) for s in manifest["skills"].values())

for name, info in manifest["skills"].items():
    size = info.get("size_bytes", 0)
    files = info.get("file_count", 0)
    category = info.get("category", "uncategorized")

    # Depth score (0-40): how rich/comprehensive is this skill
    depth = 0
    if size > 0 and files > 0:
        norm_size = size / max_size
        norm_files = files / max_files
        depth = (norm_size * 0.6 + norm_files * 0.4) * 40

    # Mention score (0-20): community interest
    mentions = skill_mentions.get(name, 0)
    mention_score = min(mentions * 5, 20)

    # Category weight (multiplier)
    cat_weight = category_weights.get(category, 1.0)

    # Base score for having a description (0-10)
    desc_score = 10 if info.get("description") else 3

    # Repo-level signal bonus (shared across all skills, 0-30)
    repo_bonus = min(
        repo_signals["stars"] * 0.5 +
        repo_signals["forks"] * 1.0 +
        repo_signals["contributors"] * 2.0 +
        repo_signals["discussions"] * 0.3,
        30
    )

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
max_score = max(s["raw_score"] for s in scores.values()) if scores else 1
for name in scores:
    scores[name]["score"] = round(scores[name]["raw_score"] / max_score * 100, 1)

# Assign tiers
for name in scores:
    s = scores[name]["score"]
    if s >= 80: scores[name]["tier"] = "S"
    elif s >= 60: scores[name]["tier"] = "A"
    elif s >= 40: scores[name]["tier"] = "B"
    elif s >= 20: scores[name]["tier"] = "C"
    else: scores[name]["tier"] = "D"

# Update manifest
for name in manifest["skills"]:
    if name in scores:
        manifest["skills"][name]["ranking"] = {
            "score": scores[name]["score"],
            "tier": scores[name]["tier"],
            "signals": {
                "depth": scores[name]["depth"],
                "mentions": scores[name]["mentions"],
                "desc_quality": scores[name]["desc_score"],
            }
        }

manifest["ranking"]["last_ranked"] = __import__("datetime").datetime.now(
    __import__("datetime").timezone.utc
).isoformat()
manifest["ranking"]["repo_signals"] = repo_signals

with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)

# Sort by score
ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

# Generate RANKINGS.md
tier_emoji = {"S": "🏆", "A": "⭐", "B": "✅", "C": "📋", "D": "📝"}

lines = [
    "# Skill Rankings",
    "",
    f"Last updated: {manifest['ranking']['last_ranked'][:10]}",
    "",
    f"**Repo signals**: {repo_signals['stars']} stars, {repo_signals['forks']} forks, {repo_signals['contributors']} contributors, {repo_signals['discussions']} discussions",
    "",
    "## Ranking Method",
    "",
    "Each skill is scored 0-100 based on:",
    "- **Depth** (40%): file count and content size as a proxy for comprehensiveness",
    "- **Community** (20%): issue/discussion mentions on GitHub",
    "- **Documentation** (10%): quality of skill description",
    "- **Repo health** (30%): stars, forks, contributors, discussions",
    "- **Category weight**: engineering/shipping/factory skills get a slight boost",
    "",
    "## Tiers",
    "",
    "| Tier | Score | Meaning |",
    "|------|-------|---------|",
    "| S | 80-100 | Best-in-class, comprehensive, well-documented |",
    "| A | 60-79 | High quality, feature-rich |",
    "| B | 40-59 | Solid, does the job well |",
    "| C | 20-39 | Basic but functional |",
    "| D | 0-19 | Minimal, could use improvement |",
    "",
    "## Leaderboard",
    "",
    "| Rank | Skill | Category | Score | Tier |",
    "|------|-------|----------|-------|------|",
]

for i, (name, data) in enumerate(ranked, 1):
    tier = data["tier"]
    emoji = tier_emoji.get(tier, "")
    lines.append(f"| {i} | `{name}` | {data['category']} | {data['score']} | {emoji} {tier} |")

# Per-category leaderboard
lines += ["", "## By Category", ""]
categories = {}
for name, data in ranked:
    cat = data["category"]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append((name, data))

for cat in sorted(categories.keys()):
    skills = categories[cat]
    lines.append(f"### {cat.replace('-', ' ').title()}")
    lines.append("")
    lines.append("| Skill | Score | Tier |")
    lines.append("|-------|-------|------|")
    for name, data in skills:
        emoji = tier_emoji.get(data["tier"], "")
        lines.append(f"| `{name}` | {data['score']} | {emoji} {data['tier']} |")
    lines.append("")

with open(rankings_path, "w") as f:
    f.write("\n".join(lines))

# Print summary
print(f"\nSkills ranked: {len(ranked)}")
print(f"  S-tier: {sum(1 for _,d in ranked if d['tier']=='S')}")
print(f"  A-tier: {sum(1 for _,d in ranked if d['tier']=='A')}")
print(f"  B-tier: {sum(1 for _,d in ranked if d['tier']=='B')}")
print(f"  C-tier: {sum(1 for _,d in ranked if d['tier']=='C')}")
print(f"  D-tier: {sum(1 for _,d in ranked if d['tier']=='D')}")
print(f"\nTop 10:")
for i, (name, data) in enumerate(ranked[:10], 1):
    print(f"  {i}. {name} ({data['category']}) — {data['score']} [{data['tier']}]")

json_out = os.environ.get("JSON_OUTPUT", "false")
if json_out == "true":
    print("\n" + json.dumps({"ranked": [{**v, "name": k} for k, v in ranked]}, indent=2))

PYEOF
