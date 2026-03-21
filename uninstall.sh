#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# amazing_cc_skills uninstaller
# ============================================================================

SKILLS_TARGET="$HOME/.claude/skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SOURCE="$SCRIPT_DIR/skills"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${BLUE}[info]${NC} $*"; }
success() { echo -e "${GREEN}[ok]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  amazing_cc_skills uninstaller${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

if [[ ! -d "$SKILLS_TARGET" ]]; then
    warn "No skills directory found at $SKILLS_TARGET"
    exit 0
fi

# Only remove skills that came from this repo
REMOVED=0
for skill_dir in "$SKILLS_SOURCE"/*/; do
    skill=$(basename "$skill_dir")
    target="$SKILLS_TARGET/$skill"

    if [[ -e "$target" ]] || [[ -L "$target" ]]; then
        rm -rf "$target"
        success "Removed $skill"
        REMOVED=$((REMOVED + 1))
    fi
done

echo ""
log "Removed $REMOVED skills"

# Check for backup to restore
LATEST_BACKUP=$(ls -dt "$HOME/.claude/skills.backup."* 2>/dev/null | head -1 || true)
if [[ -n "$LATEST_BACKUP" ]]; then
    echo ""
    read -p "Restore backup from $LATEST_BACKUP? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp -r "$LATEST_BACKUP"/* "$SKILLS_TARGET/" 2>/dev/null || true
        success "Backup restored"
    fi
fi

echo ""
success "Uninstall complete."
