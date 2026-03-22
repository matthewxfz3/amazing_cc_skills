# amazing_cc_skills

**79 Claude Code skills for startups and small businesses.** Organized by what you actually need to do — from validating your idea to retaining customers.

```bash
git clone https://github.com/matthewxfz3/amazing_cc_skills.git ~/amazing_cc_skills
cd ~/amazing_cc_skills && chmod +x install.sh && ./install.sh
```

## What's Inside

| Phase | Question | Skills | Scenarios |
|-------|----------|--------|-----------|
| **1. Validate** | Is this idea any good? | 5 | 4 |
| **2. Build** | How do I build this? | 14 | 10 |
| **3. Ship** | How do I ship this? | 16 | 12 |
| **4. Get Found** | How do people find me? | 15 | 11 |
| **5. Acquire** | How do I get customers? | 8 | 7 |
| **6. Convert** | Why aren't people converting? | 8 | 8 |
| **7. Retain** | How do I keep customers? | 3 | 3 |
| **8. Power Tools** | How do I work faster? | 13 | 8 |

**79 skills. 63 scenarios. 8 phases.**

## I Have a Problem...

See **[SCENARIOS.md](SCENARIOS.md)** — find your situation, get the right skill.

## Which Skills Are Best?

See **[RANKINGS.md](RANKINGS.md)** — every skill scored and tiered (S/A/B/C/D) based on GitHub signals.

## Install Options

```bash
./install.sh                           # Symlink all skills
./install.sh --copy                    # Copy instead of symlink
./install.sh --select qa,ship,review   # Install specific skills
./install.sh --update                  # Sync only changed skills
./install.sh --offline --copy          # No network, use local archive
./install.sh --dry-run                 # Preview without changes
```

## Update & Rank

```bash
git pull && ./install.sh --update      # Pull latest, sync changes
./rank.sh                              # Recompute rankings from GitHub signals
./rank.sh --offline                    # Rank using local data only
```

## Sources

| Source | Skills | What |
|--------|--------|------|
| **gstack** | ~26 | Engineering workflow: shipping, QA, design review, deploy, browse |
| **Claude Code Skills Factory** | ~4 | Meta-skills: prompt-factory, agent-factory, hook-factory, slash-command-factory |
| **Claude Code Community** | ~35 | Engineering best practices: TDD, debugging, planning, code review |
| **gstack Marketing Suite** | ~15 | Marketing, SEO, CRO, growth, sales |

## For AI Agents

This repo is AI-native. See [CLAUDE.md](CLAUDE.md) for how to query `rankings.json` — the machine-readable source of truth with scores, scenarios, and signal breakdowns for all 79 skills.

## Security

Skills are scanned for risky patterns (database access, messaging, credentials, destructive commands). Dangerous skills are **excluded by default** during installation.

```bash
python3 lib/security.py              # Scan all skills
python3 lib/security.py --verbose    # Show every finding
python3 lib/security.py --strict     # CI mode: exit 1 on dangerous
./install.sh --allow-dangerous       # Opt in to dangerous skills
```

To mark a skill as dangerous, add to its `SKILL.md` frontmatter:
```yaml
dangerous: true
dangerous_reason: Why this skill is risky
```

## How Skills Work

Each skill is a directory with a `SKILL.md` file:

```yaml
---
name: my-skill
description: When to trigger this skill
---
# Prompt content...
```

Install to `~/.claude/skills/` and invoke as `/skill-name` in Claude Code.

## License

MIT
