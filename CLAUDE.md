# amazing_cc_skills

79 curated Claude Code skills for startups and small businesses, organized by 8 startup journey phases.

## Project Structure
- `skills/` — 79 skill directories, each containing `SKILL.md` + supporting files
- `rankings.json` — **Source of truth for rankings** — read/write by scripts and LLMs
- `skills-manifest.json` — Checksums, categories, metadata (used by installer)
- `RANKINGS.md` — Auto-generated from `rankings.json` (human-readable, do not edit)
- `install.sh` — Fault-tolerant parallel installer
- `uninstall.sh` — Clean removal with backup restore
- `rank.sh` — Fetch GitHub signals and recompute rankings
- `lib/` — Shared code: `common.sh`, `manifest.py`, `rank.py`

## Key Files for LLMs

### rankings.json (read/write)
The primary config for skill quality data. Structure:
- `meta` — when/how rankings were computed
- `repo_signals` — GitHub stars, forks, contributors, discussions
- `scoring` — weights, tier thresholds (explains the formula)
- `leaderboard` — ordered list: `[{rank, name, score, tier, phase}]`
- `by_phase` — skills grouped by startup journey phase
- `by_tier` — skills grouped by quality tier (S/A/B/C/D)
- `skills` — per-skill detail with full signal breakdown
- `user_overrides` — manual score/tier overrides (preserved across re-ranks)

### skills-manifest.json (read/write)
- `categories` — 8 startup journey phases with skill lists
- `skills.<name>.checksum` — MD5 for change detection
- `skills.<name>.ranking.score` — summary score (detail in rankings.json)

## Scripts
- `./install.sh` — `--copy`, `--select`, `--jobs N`, `--offline`, `--update`, `--dry-run`
- `./rank.sh` — `--offline`, `--json`
- `python3 lib/manifest.py` — `--check` (staleness), `--checksums-only`
- `python3 lib/rank.py` — `--signals file.json`, `--json`

## Conventions
- Each skill lives in `skills/<name>/SKILL.md` with YAML frontmatter
- Skills are categorized by startup journey phase (1-validate through 8-power-tools)
- Rankings flow: `rank.sh` → `rankings.json` → `RANKINGS.md` (generated)
