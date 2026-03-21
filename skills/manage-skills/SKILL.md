---
name: manage-skills
description: Install, update, list, or remove Claude Code skills from the amazing_cc_skills collection. Use when the user mentions 'install skills,' 'update skills,' 'list skills,' 'remove skill,' 'manage skills,' or 'skill manager.'
---

# Manage Skills

You are a skill manager for the amazing_cc_skills collection. Help the user install, update, list, or remove Claude Code skills.

## Determine the action

Ask the user what they want to do if not clear from context:
1. **install** — Clone the repo and install all (or selected) skills
2. **update** — Pull latest changes and sync new/changed skills
3. **list** — Show all available skills and their install status
4. **remove** — Uninstall a specific skill

## Repository

- Repo: `https://github.com/matthewxfz3/amazing_cc_skills.git`
- Default clone location: `$HOME/amazing_cc_skills`
- Skills target: `$HOME/.claude/skills/`
- Manifest: `skills-manifest.json` (tracks checksums for change detection)

## Install Flow

1. Check if the repo is already cloned at `$HOME/amazing_cc_skills`
2. If not, clone it:
   ```bash
   git clone https://github.com/matthewxfz3/amazing_cc_skills.git $HOME/amazing_cc_skills
   ```
3. Run the installer:
   ```bash
   chmod +x $HOME/amazing_cc_skills/install.sh
   $HOME/amazing_cc_skills/install.sh
   ```
4. Report results to the user

## Update Flow

1. Check if repo exists at `$HOME/amazing_cc_skills`
2. Pull latest:
   ```bash
   cd $HOME/amazing_cc_skills && git pull --ff-only
   ```
3. Read `skills-manifest.json` to check which skills have changed (compare checksums with installed versions)
4. Run the installer in update mode:
   ```bash
   $HOME/amazing_cc_skills/install.sh --update
   ```
5. Report what was updated

## List Flow

1. Read `skills-manifest.json` from the repo
2. For each skill, check if it exists in `$HOME/.claude/skills/`
3. Display a table:
   - Skill name
   - Status (installed / not installed / outdated)
   - Description (from manifest)
4. Group by category if possible

## Remove Flow

1. Ask which skill(s) to remove
2. Remove from `$HOME/.claude/skills/<skill-name>`
3. Confirm removal

## Important

- Each skill installs independently — one failure must NOT block others
- Always show a summary at the end
- If git operations fail, fall back to using the local `skills/` folder
- Check `skills-manifest.json` checksums before copying to avoid unnecessary work
