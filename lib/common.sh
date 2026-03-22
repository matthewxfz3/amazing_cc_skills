#!/usr/bin/env bash
# ============================================================================
# Shared functions for amazing_cc_skills scripts
# Source this file: source "$(dirname "$0")/lib/common.sh"
# ============================================================================

# Resolve project root (works from any script location)
PROJ_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SOURCE="$PROJ_ROOT/skills"
SKILLS_TARGET="${SKILLS_TARGET:-$HOME/.claude/skills}"
MANIFEST="$PROJ_ROOT/skills-manifest.json"
REPO_URL="https://github.com/matthewxfz3/amazing_cc_skills.git"
REPO_SLUG="matthewxfz3/amazing_cc_skills"
VERSION="3.0.0"

# ---- Colors (auto-disable if not a terminal) ----
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' NC=''
fi

# ---- Logging ----
log()     { echo -e "${BLUE}[info]${NC} $*"; }
success() { echo -e "${GREEN}[ok]${NC} $*"; }
warn()    { echo -e "${YELLOW}[warn]${NC} $*" >&2; }
fail()    { echo -e "${RED}[fail]${NC} $*" >&2; }

# ---- Dependency checks ----
require_cmd() {
    local cmd="$1"
    local msg="${2:-$cmd is required but not found}"
    if ! command -v "$cmd" &>/dev/null; then
        fail "$msg"
        return 1
    fi
}

require_python3() {
    require_cmd python3 "python3 is required for this operation"
}

# ---- Checksum ----
# Compute MD5 checksum of all files in a directory (sorted, deterministic)
dir_checksum() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        echo ""
        return
    fi
    python3 -c "
import hashlib, os, sys
h = hashlib.md5()
d = sys.argv[1]
for root, dirs, files in os.walk(d):
    dirs.sort()
    for f in sorted(files):
        fp = os.path.join(root, f)
        with open(fp, 'rb') as fh:
            for chunk in iter(lambda: fh.read(8192), b''):
                h.update(chunk)
print(h.hexdigest())
" "$dir" 2>/dev/null || echo ""
}

# ---- Git helpers ----
try_git_pull() {
    local dir="$1"
    if command -v git &>/dev/null && [[ -d "$dir/.git" ]]; then
        if git -C "$dir" pull --ff-only 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# ---- Banner ----
banner() {
    local title="$1"
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  ${title}${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}
