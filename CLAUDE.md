# amazing_cc_skills

This is a Claude Code skills distribution repository. It contains 85+ production-ready skills organized by category.

## Project Structure
- `skills/` — All skill directories, each containing a `SKILL.md` and supporting files
- `skills-manifest.json` — Tracks checksums and metadata for each skill (used by installer to detect changes)
- `install.sh` — Fault-tolerant, parallel installer (bash)
- `uninstall.sh` — Clean removal with backup restore
- `skills/manage-skills/SKILL.md` — Claude Code skill for managing skills from within a session

## Key Files
- `skills-manifest.json` — Check this to see if skills need updating (compare checksums)
- `install.sh` — Supports: `--copy`, `--select`, `--jobs N`, `--offline`, `--update`, `--verbose`

## Conventions
- Each skill lives in its own directory under `skills/`
- The primary skill definition is always `SKILL.md` with YAML frontmatter
- Supporting files (templates, references, examples) live alongside SKILL.md
