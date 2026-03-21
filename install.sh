#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# amazing_cc_skills installer
# Fault-tolerant, parallel, update-aware
# ============================================================================

REPO_URL="https://github.com/matthewxfz3/amazing_cc_skills.git"
SKILLS_TARGET="$HOME/.claude/skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SOURCE="$SCRIPT_DIR/skills"
MANIFEST="$SCRIPT_DIR/skills-manifest.json"
BACKUP_DIR="$HOME/.claude/skills.backup.$(date +%Y%m%d%H%M%S)"
LOG_FILE="/tmp/amazing_cc_skills_install.log"

# Defaults
MODE="symlink"
MAX_JOBS=4
OFFLINE=false
UPDATE_ONLY=false
SELECTED_SKILLS=""
VERBOSE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters (use temp files for parallel-safe counting)
COUNT_DIR=$(mktemp -d)
echo "0" > "$COUNT_DIR/success"
echo "0" > "$COUNT_DIR/failed"
echo "0" > "$COUNT_DIR/skipped"

cleanup() {
    rm -rf "$COUNT_DIR"
}
trap cleanup EXIT

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install or update Claude Code skills from amazing_cc_skills.

Options:
  --copy            Copy skills instead of symlinking (default: symlink)
  --select LIST     Comma-separated list of skills to install
  --jobs N          Max parallel installs (default: 4)
  --offline         Skip git pull, use local skills/ folder only
  --update          Update mode: skip backup, only sync changed skills
  --verbose         Show detailed output
  -h, --help        Show this help

Examples:
  ./install.sh                           # Install all skills (symlink)
  ./install.sh --copy                    # Install all skills (copy)
  ./install.sh --select qa,ship,review   # Install specific skills
  ./install.sh --update                  # Update existing installation
  ./install.sh --offline --copy          # Offline install via copy
EOF
    exit 0
}

log() { echo -e "${BLUE}[info]${NC} $*"; }
success() { echo -e "${GREEN}[ok]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
fail() { echo -e "${RED}[fail]${NC} $*" >&2; }

increment() {
    local file="$COUNT_DIR/$1"
    # Use flock for atomic increment on Linux, or a simple approach for macOS
    local val
    val=$(cat "$file")
    echo $((val + 1)) > "$file"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --copy)     MODE="copy"; shift ;;
        --select)   SELECTED_SKILLS="$2"; shift 2 ;;
        --jobs)     MAX_JOBS="$2"; shift 2 ;;
        --offline)  OFFLINE=true; shift ;;
        --update)   UPDATE_ONLY=true; shift ;;
        --verbose)  VERBOSE=true; shift ;;
        -h|--help)  usage ;;
        *)          fail "Unknown option: $1"; usage ;;
    esac
done

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  amazing_cc_skills installer${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Step 1: Update from git if online
if [[ "$OFFLINE" == false ]]; then
    if command -v git &>/dev/null && [[ -d "$SCRIPT_DIR/.git" ]]; then
        log "Pulling latest skills from git..."
        if git -C "$SCRIPT_DIR" pull --ff-only 2>/dev/null; then
            success "Updated to latest version"
        else
            warn "Git pull failed, using local files as fallback"
        fi
    elif command -v git &>/dev/null; then
        warn "Not a git repo — using local skills/ folder"
    else
        warn "Git not found — using local skills/ folder"
    fi
else
    log "Offline mode: using local skills/ folder"
fi

# Step 2: Validate source
if [[ ! -d "$SKILLS_SOURCE" ]]; then
    fail "Skills source directory not found: $SKILLS_SOURCE"
    exit 1
fi

AVAILABLE_SKILLS=($(ls -d "$SKILLS_SOURCE"/*/ 2>/dev/null | xargs -I{} basename {}))
TOTAL_AVAILABLE=${#AVAILABLE_SKILLS[@]}

if [[ $TOTAL_AVAILABLE -eq 0 ]]; then
    fail "No skills found in $SKILLS_SOURCE"
    exit 1
fi

log "Found $TOTAL_AVAILABLE skills available"

# Step 3: Filter skills if --select was used
if [[ -n "$SELECTED_SKILLS" ]]; then
    IFS=',' read -ra SELECTED <<< "$SELECTED_SKILLS"
    INSTALL_SKILLS=()
    for s in "${SELECTED[@]}"; do
        s=$(echo "$s" | xargs) # trim whitespace
        if [[ -d "$SKILLS_SOURCE/$s" ]]; then
            INSTALL_SKILLS+=("$s")
        else
            warn "Skill not found: $s (skipping)"
            increment skipped
        fi
    done
else
    INSTALL_SKILLS=("${AVAILABLE_SKILLS[@]}")
fi

if [[ ${#INSTALL_SKILLS[@]} -eq 0 ]]; then
    fail "No valid skills to install"
    exit 1
fi

log "Installing ${#INSTALL_SKILLS[@]} skills using $MODE mode (parallelism: $MAX_JOBS)"

# Step 4: Backup existing skills (first run only)
mkdir -p "$SKILLS_TARGET"

if [[ "$UPDATE_ONLY" == false ]] && [[ -n "$(ls -A "$SKILLS_TARGET" 2>/dev/null)" ]]; then
    log "Backing up existing skills to $BACKUP_DIR"
    cp -r "$SKILLS_TARGET" "$BACKUP_DIR" 2>/dev/null || true
    success "Backup created"
fi

# Step 5: Install skills in parallel
install_skill() {
    local skill="$1"
    local src="$SKILLS_SOURCE/$skill"
    local dst="$SKILLS_TARGET/$skill"

    # Check manifest for changes (skip if unchanged)
    if [[ "$UPDATE_ONLY" == true ]] && [[ -d "$dst" ]] && [[ -f "$MANIFEST" ]]; then
        local src_checksum
        src_checksum=$(python3 -c "
import json, sys
try:
    m = json.load(open('$MANIFEST'))
    print(m.get('skills',{}).get('$skill',{}).get('checksum',''))
except: print('')
" 2>/dev/null || echo "")

        if [[ -n "$src_checksum" ]]; then
            local dst_checksum
            dst_checksum=$(python3 -c "
import hashlib, os
h = hashlib.md5()
for root, dirs, files in os.walk('$dst'):
    for f in sorted(files):
        with open(os.path.join(root, f), 'rb') as fh:
            h.update(fh.read())
print(h.hexdigest())
" 2>/dev/null || echo "")

            if [[ "$src_checksum" == "$dst_checksum" ]]; then
                [[ "$VERBOSE" == true ]] && echo -e "  ${YELLOW}skip${NC} $skill (unchanged)"
                increment skipped
                return 0
            fi
        fi
    fi

    # Remove existing
    rm -rf "$dst" 2>/dev/null || true

    if [[ "$MODE" == "symlink" ]]; then
        if ln -sf "$src" "$dst" 2>>"$LOG_FILE"; then
            success "  $skill"
            increment success
        else
            fail "  $skill (symlink failed)"
            increment failed
        fi
    else
        if cp -r "$src" "$dst" 2>>"$LOG_FILE"; then
            success "  $skill"
            increment success
        else
            fail "  $skill (copy failed)"
            increment failed
        fi
    fi
}

export -f install_skill increment success fail warn
export SKILLS_SOURCE SKILLS_TARGET MANIFEST MODE UPDATE_ONLY VERBOSE LOG_FILE COUNT_DIR
export RED GREEN YELLOW BLUE CYAN NC

# Run installs in parallel using background jobs
echo ""
active_jobs=0
for skill in "${INSTALL_SKILLS[@]}"; do
    install_skill "$skill" &
    active_jobs=$((active_jobs + 1))

    if [[ $active_jobs -ge $MAX_JOBS ]]; then
        wait -n 2>/dev/null || wait
        active_jobs=$((active_jobs - 1))
    fi
done
wait

# Step 6: Summary
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Installation Summary${NC}"
echo -e "${CYAN}========================================${NC}"

S=$(cat "$COUNT_DIR/success")
F=$(cat "$COUNT_DIR/failed")
K=$(cat "$COUNT_DIR/skipped")

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
