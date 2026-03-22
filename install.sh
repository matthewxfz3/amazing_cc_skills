#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# amazing_cc_skills installer
# Fault-tolerant, parallel, update-aware
#
# Fixes over v1:
#   - Race-safe counters using per-skill status files (no shared file writes)
#   - No export -f (works in zsh + bash)
#   - Batch checksum comparison via Python (one process, not one per skill)
#   - Proper cleanup on signals
# ============================================================================

source "$(dirname "$0")/lib/common.sh"

# Defaults
MODE="symlink"
MAX_JOBS=4
OFFLINE=false
UPDATE_ONLY=false
SELECTED_SKILLS=""
VERBOSE=false
DRY_RUN=false
ALLOW_DANGEROUS=false

# Skills marked as dangerous (access private data, require special permissions)
DANGEROUS_SKILLS="imessage"

# Temp dir for per-skill status tracking (race-safe: one file per skill)
STATUS_DIR=$(mktemp -d)
LOG_FILE="${TMPDIR:-/tmp}/amazing_cc_skills_install.log"
: > "$LOG_FILE"

cleanup() { rm -rf "$STATUS_DIR"; }
trap cleanup EXIT INT TERM

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install or update Claude Code skills from amazing_cc_skills.

Options:
  --copy              Copy skills instead of symlinking (default: symlink)
  --select LIST       Comma-separated list of skills to install
  --jobs N            Max parallel installs (default: 4)
  --offline           Skip git pull, use local skills/ folder only
  --update            Update mode: skip backup, only sync changed skills
  --allow-dangerous   Also install dangerous skills (e.g. imessage: local DB access)
  --verbose           Show detailed output
  --dry-run           Show what would be done without doing it
  --version           Show version
  -h, --help          Show this help

Dangerous skills are excluded by default. They access private data, require
special OS permissions, or are intended for debugging only. Use --allow-dangerous
to opt in. Currently dangerous: ${DANGEROUS_SKILLS}

Examples:
  ./install.sh                           # Install all safe skills (symlink)
  ./install.sh --copy                    # Install all safe skills (copy)
  ./install.sh --allow-dangerous         # Include dangerous skills too
  ./install.sh --select qa,ship,review   # Install specific skills
  ./install.sh --update                  # Update existing installation
  ./install.sh --offline --copy          # Offline install via copy
EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --copy)              MODE="copy"; shift ;;
        --select)            SELECTED_SKILLS="$2"; shift 2 ;;
        --jobs)              MAX_JOBS="$2"; shift 2 ;;
        --offline)           OFFLINE=true; shift ;;
        --update)            UPDATE_ONLY=true; shift ;;
        --allow-dangerous)   ALLOW_DANGEROUS=true; shift ;;
        --verbose)           VERBOSE=true; shift ;;
        --dry-run)           DRY_RUN=true; shift ;;
        --version)           echo "amazing_cc_skills installer v$VERSION"; exit 0 ;;
        -h|--help)           usage ;;
        *)                   fail "Unknown option: $1"; usage ;;
    esac
done

banner "amazing_cc_skills installer v$VERSION"

# ---- Step 1: Update from git ----
if [[ "$OFFLINE" == false ]]; then
    if try_git_pull "$PROJ_ROOT"; then
        success "Updated to latest version"
    else
        warn "Git pull unavailable, using local files"
    fi
else
    log "Offline mode: using local skills/ folder"
fi

# ---- Step 2: Validate source ----
if [[ ! -d "$SKILLS_SOURCE" ]]; then
    fail "Skills source directory not found: $SKILLS_SOURCE"
    exit 1
fi

# List available skills (portable: no xargs -I)
AVAILABLE_SKILLS=()
for d in "$SKILLS_SOURCE"/*/; do
    [[ -d "$d" ]] && AVAILABLE_SKILLS+=("$(basename "$d")")
done

if [[ ${#AVAILABLE_SKILLS[@]} -eq 0 ]]; then
    fail "No skills found in $SKILLS_SOURCE"
    exit 1
fi
log "Found ${#AVAILABLE_SKILLS[@]} skills available"

# ---- Step 3: Filter if --select ----
if [[ -n "$SELECTED_SKILLS" ]]; then
    IFS=',' read -ra SELECTED <<< "$SELECTED_SKILLS"
    INSTALL_SKILLS=()
    for s in "${SELECTED[@]}"; do
        s="${s## }"; s="${s%% }"  # trim whitespace (no xargs)
        if [[ -d "$SKILLS_SOURCE/$s" ]]; then
            INSTALL_SKILLS+=("$s")
        else
            warn "Skill not found: $s (skipping)"
            echo "skip" > "$STATUS_DIR/$s"
        fi
    done
else
    INSTALL_SKILLS=("${AVAILABLE_SKILLS[@]}")
fi

# ---- Step 3b: Filter out dangerous skills unless --allow-dangerous ----
is_dangerous() {
    local skill="$1"
    for d in $DANGEROUS_SKILLS; do
        [[ "$skill" == "$d" ]] && return 0
    done
    return 1
}

if [[ "$ALLOW_DANGEROUS" == false ]]; then
    SAFE_SKILLS=()
    SKIPPED_DANGEROUS=0
    for s in "${INSTALL_SKILLS[@]}"; do
        if is_dangerous "$s"; then
            SKIPPED_DANGEROUS=$((SKIPPED_DANGEROUS + 1))
            [[ "$VERBOSE" == true ]] && warn "Skipping dangerous skill: $s (use --allow-dangerous to include)"
            echo "skip" > "$STATUS_DIR/$s"
        else
            SAFE_SKILLS+=("$s")
        fi
    done
    INSTALL_SKILLS=("${SAFE_SKILLS[@]}")
    [[ $SKIPPED_DANGEROUS -gt 0 ]] && warn "Excluded $SKIPPED_DANGEROUS dangerous skill(s). Use --allow-dangerous to include."
fi

if [[ ${#INSTALL_SKILLS[@]} -eq 0 ]]; then
    fail "No valid skills to install"
    exit 1
fi

# ---- Step 4: Batch checksum comparison for --update mode ----
# Write unchanged skill names to a file (avoids bash associative arrays for macOS compat)
SKIP_FILE="$STATUS_DIR/_unchanged"
: > "$SKIP_FILE"

if [[ "$UPDATE_ONLY" == true ]] && [[ -f "$MANIFEST" ]]; then
    if command -v python3 &>/dev/null; then
        log "Comparing checksums..."
        # One Python call compares ALL skills at once (not one per skill)
        python3 -c "
import json, hashlib, os, sys

manifest_path = sys.argv[1]
skills_target = sys.argv[2]
out_path = sys.argv[3]

with open(manifest_path) as f:
    manifest = json.load(f)

unchanged = []
for name, info in manifest.get('skills', {}).items():
    src_checksum = info.get('checksum', '')
    dst = os.path.join(skills_target, name)
    if not os.path.isdir(dst) or not src_checksum:
        continue
    h = hashlib.md5()
    for root, dirs, files in os.walk(dst):
        dirs.sort()
        for f in sorted(files):
            fp = os.path.join(root, f)
            with open(fp, 'rb') as fh:
                for chunk in iter(lambda: fh.read(8192), b''):
                    h.update(chunk)
    if h.hexdigest() == src_checksum:
        unchanged.append(name)

with open(out_path, 'w') as f:
    f.write('\n'.join(unchanged))
" "$MANIFEST" "$SKILLS_TARGET" "$SKIP_FILE" 2>/dev/null || true

        SKIP_COUNT=$(wc -l < "$SKIP_FILE" | tr -d ' ')
        [[ "$SKIP_COUNT" -gt 0 ]] && log "Skipping $SKIP_COUNT unchanged skills"
    else
        warn "python3 not found, skipping checksum comparison"
    fi
fi

# Helper: check if a skill should be skipped
is_unchanged() {
    grep -qx "$1" "$SKIP_FILE" 2>/dev/null
}

log "Installing ${#INSTALL_SKILLS[@]} skills using $MODE mode (parallelism: $MAX_JOBS)"

# ---- Step 5: Backup (first install only) ----
mkdir -p "$SKILLS_TARGET"

if [[ "$UPDATE_ONLY" == false ]] && [[ "$DRY_RUN" == false ]]; then
    if [[ -n "$(ls -A "$SKILLS_TARGET" 2>/dev/null)" ]]; then
        BACKUP_DIR="$HOME/.claude/skills.backup.$(date +%Y%m%d%H%M%S)"
        log "Backing up existing skills to $BACKUP_DIR"
        cp -r "$SKILLS_TARGET" "$BACKUP_DIR" 2>/dev/null || true
        success "Backup created"
    fi
fi

# ---- Step 6: Install skills in parallel ----
# Each skill writes its own status file (no shared counter = no race condition)
install_one_skill() {
    local skill="$1"
    local src="$SKILLS_SOURCE/$skill"
    local dst="$SKILLS_TARGET/$skill"

    # Skip if unchanged (already computed in batch)
    if is_unchanged "$skill"; then
        [[ "$VERBOSE" == true ]] && echo -e "  ${YELLOW}skip${NC} $skill (unchanged)"
        echo "skip" > "$STATUS_DIR/$skill"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        echo -e "  ${BLUE}dry-run${NC} $skill ($MODE)"
        echo "ok" > "$STATUS_DIR/$skill"
        return 0
    fi

    # Remove existing
    rm -rf "$dst" 2>/dev/null || true

    local result=0
    if [[ "$MODE" == "symlink" ]]; then
        ln -sf "$src" "$dst" 2>>"$LOG_FILE" || result=$?
    else
        cp -r "$src" "$dst" 2>>"$LOG_FILE" || result=$?
    fi

    if [[ $result -eq 0 ]]; then
        success "  $skill"
        echo "ok" > "$STATUS_DIR/$skill"
    else
        fail "  $skill ($MODE failed)"
        echo "fail" > "$STATUS_DIR/$skill"
    fi
}

echo ""
active_jobs=0
for skill in "${INSTALL_SKILLS[@]}"; do
    install_one_skill "$skill" &
    active_jobs=$((active_jobs + 1))

    if [[ $active_jobs -ge $MAX_JOBS ]]; then
        wait -n 2>/dev/null || wait
        active_jobs=$((active_jobs - 1))
    fi
done
wait

# ---- Step 7: Summary (count from status files — no race condition) ----
S=0; F=0; K=0
for f in "$STATUS_DIR"/*; do
    [[ -f "$f" ]] || continue
    case "$(cat "$f")" in
        ok)   S=$((S + 1)) ;;
        fail) F=$((F + 1)) ;;
        skip) K=$((K + 1)) ;;
    esac
done

banner "Installation Summary"
echo -e "  ${GREEN}Installed:${NC} $S"
echo -e "  ${YELLOW}Skipped:${NC}   $K"
echo -e "  ${RED}Failed:${NC}    $F"
echo -e "  ${BLUE}Target:${NC}    $SKILLS_TARGET"
echo -e "  ${BLUE}Mode:${NC}      $MODE"
echo ""

if [[ "$F" -gt 0 ]]; then
    warn "Some skills failed to install. Check $LOG_FILE for details."
fi

if [[ "$S" -eq 0 ]] && [[ "$K" -eq 0 ]]; then
    fail "All installations failed!"
    exit 1
fi

success "Done! Skills are ready to use in Claude Code."
echo ""
