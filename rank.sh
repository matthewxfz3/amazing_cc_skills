#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# amazing_cc_skills — Skill Ranking Engine
#
# Thin shell wrapper that fetches GitHub signals, then delegates to
# lib/rank.py for computation. All scoring logic lives in Python.
#
# Usage:
#   ./rank.sh                  # Full ranking with GitHub API
#   ./rank.sh --offline        # Rank using local signals only
#   ./rank.sh --json           # Output raw JSON
# ============================================================================

source "$(dirname "$0")/lib/common.sh"

require_python3 || exit 1

OFFLINE=false
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --offline)   OFFLINE=true; shift ;;
        --json)      EXTRA_ARGS+=("--json"); shift ;;
        --version)   echo "amazing_cc_skills rank v$VERSION"; exit 0 ;;
        -h|--help)
            echo "Usage: $(basename "$0") [--offline] [--json] [--version]"
            exit 0 ;;
        *) shift ;;
    esac
done

# ---- Fetch GitHub signals ----
export STARS=0 FORKS=0 OPEN_ISSUES=0 CONTRIBUTORS=1 DISCUSSIONS=0
SIGNALS_FILE=$(mktemp)
trap "rm -f '$SIGNALS_FILE'" EXIT INT TERM

if [[ "$OFFLINE" == false ]] && command -v gh &>/dev/null; then
    log "Fetching GitHub signals for $REPO_SLUG..."

    REPO_JSON=$(gh api "repos/$REPO_SLUG" 2>/dev/null || echo "{}")

    STARS=$(echo "$REPO_JSON" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('stargazers_count', 0))
" 2>/dev/null || echo 0)

    FORKS=$(echo "$REPO_JSON" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('forks_count', 0))
" 2>/dev/null || echo 0)

    OPEN_ISSUES=$(echo "$REPO_JSON" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('open_issues_count', 0))
" 2>/dev/null || echo 0)

    CONTRIBUTORS=$(gh api "repos/$REPO_SLUG/contributors?per_page=1" 2>/dev/null \
        | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 1)

    DISCUSSIONS=$(gh api graphql -f query="{
        repository(owner:\"matthewxfz3\",name:\"amazing_cc_skills\"){
            discussions{totalCount}
        }
    }" 2>/dev/null | python3 -c "
import sys, json
print(json.load(sys.stdin)['data']['repository']['discussions']['totalCount'])
" 2>/dev/null || echo 0)

    # Scan issues for per-skill mentions
    log "Scanning issues for skill mentions..."
    SKILL_MENTIONS="{}"
    ISSUES_JSON=$(gh api "repos/$REPO_SLUG/issues?state=all&per_page=100" 2>/dev/null || echo "[]")
    SKILL_MENTIONS=$(python3 -c "
import json, sys, os

issues = json.loads(sys.argv[1])
manifest_path = os.path.join(sys.argv[2], 'skills-manifest.json')
with open(manifest_path) as f:
    manifest = json.load(f)

mentions = {}
for issue in issues:
    text = ((issue.get('title') or '') + ' ' + (issue.get('body') or '')).lower()
    for skill_name in manifest.get('skills', {}):
        if skill_name.replace('-', ' ') in text or skill_name in text:
            mentions[skill_name] = mentions.get(skill_name, 0) + 1

print(json.dumps(mentions))
" "$ISSUES_JSON" "$PROJ_ROOT" 2>/dev/null || echo "{}")

    # Write signals to temp file for Python
    python3 -c "
import json, sys
signals = {
    'repo_signals': {
        'stars': int(sys.argv[1]),
        'forks': int(sys.argv[2]),
        'open_issues': int(sys.argv[3]),
        'contributors': int(sys.argv[4]),
        'discussions': int(sys.argv[5]),
    },
    'skill_mentions': json.loads(sys.argv[6]),
}
with open(sys.argv[7], 'w') as f:
    json.dump(signals, f)
" "$STARS" "$FORKS" "$OPEN_ISSUES" "$CONTRIBUTORS" "$DISCUSSIONS" \
  "$SKILL_MENTIONS" "$SIGNALS_FILE"

    success "GitHub signals fetched"
    EXTRA_ARGS+=("--signals" "$SIGNALS_FILE")
else
    if [[ "$OFFLINE" == true ]]; then
        log "Offline mode: using local signals only"
    else
        warn "gh CLI not found, using local signals only"
    fi
fi

# ---- Run ranking ----
log "Computing skill rankings..."
python3 "$PROJ_ROOT/lib/rank.py" ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}
success "Rankings updated: RANKINGS.md + skills-manifest.json"
