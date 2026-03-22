#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# amazing_cc_skills uninstaller
# ============================================================================

source "$(dirname "$0")/lib/common.sh"

DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)   DRY_RUN=true; shift ;;
        --version)   echo "amazing_cc_skills uninstaller v$VERSION"; exit 0 ;;
        -h|--help)
            echo "Usage: $(basename "$0") [--dry-run] [--version]"
            exit 0 ;;
        *) shift ;;
    esac
done

banner "amazing_cc_skills uninstaller"

if [[ ! -d "$SKILLS_TARGET" ]]; then
    warn "No skills directory found at $SKILLS_TARGET"
    exit 0
fi

# Only remove skills that came from this repo
REMOVED=0
FAILED=0
for skill_dir in "$SKILLS_SOURCE"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill=$(basename "$skill_dir")
    target="$SKILLS_TARGET/$skill"

    if [[ -e "$target" ]] || [[ -L "$target" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            log "Would remove: $skill"
        else
            if rm -rf "$target" 2>/dev/null; then
                success "Removed $skill"
                REMOVED=$((REMOVED + 1))
            else
                fail "Could not remove $skill"
                FAILED=$((FAILED + 1))
            fi
        fi
    fi
done

echo ""
log "Removed $REMOVED skills"
[[ "$FAILED" -gt 0 ]] && warn "Failed to remove $FAILED skills"

# Check for backup to restore
LATEST_BACKUP=$(ls -dt "$HOME/.claude/skills.backup."* 2>/dev/null | head -1 || true)
if [[ -n "$LATEST_BACKUP" ]] && [[ "$DRY_RUN" == false ]]; then
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
