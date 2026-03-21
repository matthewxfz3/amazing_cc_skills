# amazing_cc_skills

A curated collection of **79 production-ready Claude Code skills** across 15 categories — ranked, categorized, and installable in one command.

Every skill is scored and tiered (S/A/B/C/D) based on GitHub signals — stars, forks, issues, discussions, and contributors. See the full **[RANKINGS.md](RANKINGS.md)** leaderboard. This repo is **AI-native**: `CLAUDE.md` for context, `skills-manifest.json` for smart updates, and a built-in `/manage-skills` skill for in-session management.

## Sources & Attribution

This collection aggregates skills from multiple sources in the Claude Code ecosystem:

| Source | Skills | Description |
|--------|--------|-------------|
| **[gstack](https://github.com/anthropics/claude-code)** | ~26 skills | AI engineering workflow toolkit — shipping, QA, design review, deploy, browse, benchmarking, code review, and more. The backbone of the DevOps and shipping categories. |
| **Claude Code Skills Factory** | ~4 skills | Meta-skills that generate other skills — `prompt-factory` (69 role presets across 15 domains), `agent-factory`, `slash-command-factory`, `hook-factory`. |
| **Claude Code Community** | ~40 skills | Engineering workflow skills contributed by the Claude Code community — `systematic-debugging`, `test-driven-development`, `writing-plans`, `dispatching-parallel-agents`, `verification-before-completion`, and other development best-practice skills. |
| **gstack Marketing Suite** | ~15 skills | Marketing, SEO, CRO, and growth skills — `copywriting`, `seo-audit`, `page-cro`, `email-sequence`, `paid-ads`, `content-strategy`, `pricing-strategy`, and more. |
| **This repo** | 1 skill | `manage-skills` — built specifically for this collection to install/update/list/remove skills from within Claude Code. |

> **Note:** Skills in this repo are collected, curated, and redistributed under MIT license. If you are the original author of a skill and want attribution updated or a skill removed, please open an issue.

### What are Claude Code Skills?

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) is Anthropic's official CLI for Claude. **Skills** are markdown files (`.md`) with YAML frontmatter that extend Claude Code with reusable prompts, workflows, and agent behaviors. They live in `~/.claude/skills/` and are invoked as `/skill-name` slash commands. Skills are the primary mechanism for scaling Claude Code's capabilities across teams and machines.

## Quick Install

```bash
git clone https://github.com/matthewxfz3/amazing_cc_skills.git ~/amazing_cc_skills
cd ~/amazing_cc_skills
chmod +x install.sh
./install.sh
```

Or install from within Claude Code using the `/manage-skills` skill.

## Features

- **79 skills** across **15 categories** — curated, no duplicates
- **Ranked & tiered** — every skill scored by GitHub signals (see [RANKINGS.md](RANKINGS.md))
- **Parallel installation** — installs multiple skills simultaneously
- **Fault-tolerant** — one skill failure never blocks the rest
- **Smart updates** — checksums in `skills-manifest.json` detect changes, skip unchanged skills
- **Symlink by default** — `git pull` in the repo auto-updates your skills
- **Offline fallback** — works without network using the local `skills/` archive
- **AI-native** — `CLAUDE.md` + `/manage-skills` for seamless Claude Code integration

## Skill Rankings

Run `./rank.sh` to compute scores based on live GitHub signals:

```bash
./rank.sh                  # Full ranking with GitHub API
./rank.sh --offline        # Rank using local signals only
./rank.sh --leaderboard    # Show top skills per category
```

Rankings are saved to [RANKINGS.md](RANKINGS.md) and `skills-manifest.json`.

### Scoring Method

| Signal | Weight | Source |
|--------|--------|--------|
| Depth (file count + size) | 40% | Local analysis |
| Community mentions | 20% | GitHub Issues & Discussions |
| Documentation quality | 10% | Skill description completeness |
| Repo health | 30% | Stars, forks, contributors |

### Tiers

| Tier | Score | Meaning |
|------|-------|---------|
| S | 80-100 | Best-in-class |
| A | 60-79 | High quality |
| B | 40-59 | Solid |
| C | 20-39 | Good baseline |
| D | 0-19 | Minimal |

## Install Options

```bash
./install.sh                           # Install all (symlink mode)
./install.sh --copy                    # Install all (copy mode)
./install.sh --select qa,ship,review   # Install specific skills only
./install.sh --update                  # Update: sync only changed skills
./install.sh --offline --copy          # No network, copy from local archive
./install.sh --jobs 8                  # Increase parallelism
./install.sh --verbose                 # Show detailed output
```

## Uninstall

```bash
./uninstall.sh    # Remove installed skills, optionally restore backup
```

## Skill Categories (15)

### Engineering (10 skills)
| Skill | Description |
|-------|-------------|
| `brainstorming` | Explore intent and requirements before building |
| `executing-plans` | Execute implementation plans with review checkpoints |
| `frontend-design` | Production-grade frontend interfaces |
| `investigate` | 4-phase debugging: investigate, analyze, hypothesize, implement |
| `receiving-code-review` | Handle code review feedback with rigor |
| `subagent-driven-development` | Implementation via independent sub-agents |
| `test-driven-development` | TDD workflow — tests before implementation |
| `using-git-worktrees` | Isolated git worktrees for feature work |
| `writing-plans` | Multi-step task planning before coding |
| `writing-skills` | Create and verify new skills |

### Shipping (6 skills)
| Skill | Description |
|-------|-------------|
| `document-release` | Post-ship documentation updates |
| `land-and-deploy` | Merge PR, wait for CI, verify production health |
| `retro` | Weekly engineering retrospective |
| `review` | Pre-landing PR review for structural issues |
| `setup-deploy` | Configure deployment settings |
| `ship` | Full ship workflow: tests, review, version bump, PR |

### QA & Testing (6 skills)
| Skill | Description |
|-------|-------------|
| `benchmark` | Performance regression detection |
| `browse` | Headless browser for testing and verification |
| `canary` | Post-deploy canary monitoring |
| `qa` | Systematic QA testing with iterative bug fixes |
| `qa-only` | Report-only QA testing (no fixes) |
| `setup-browser-cookies` | Import browser cookies for authenticated testing |

### Safety (4 skills)
| Skill | Description |
|-------|-------------|
| `careful` | Safety guardrails for destructive commands |
| `freeze` | Restrict edits to a specific directory |
| `guard` | Maximum safety mode (careful + freeze) |
| `unfreeze` | Remove freeze restrictions |

### Design (6 skills)
| Skill | Description |
|-------|-------------|
| `design-consultation` | Design system creation (DESIGN.md) |
| `design-review` | Visual QA: spacing, hierarchy, consistency fixes |
| `office-hours` | YC-style brainstorming and idea validation |
| `plan-ceo-review` | CEO/founder-mode plan review |
| `plan-design-review` | Design plan review before implementation |
| `plan-eng-review` | Engineering manager plan review |

### Marketing (10 skills)
| Skill | Description |
|-------|-------------|
| `ad-creative` | Ad copy at scale for any platform |
| `content-strategy` | Plan what content to create |
| `copy-editing` | Edit and improve existing copy |
| `copywriting` | Marketing copy for any page type |
| `launch-strategy` | Product launch planning |
| `marketing-ideas` | Marketing inspiration and strategies |
| `marketing-psychology` | Behavioral science for marketing |
| `paid-ads` | PPC campaign strategy and optimization |
| `product-marketing-context` | Foundational product/audience context |
| `social-content` | Social media content creation |

### Email & Outreach (2 skills)
| Skill | Description |
|-------|-------------|
| `cold-email` | B2B cold outreach that gets replies |
| `email-sequence` | Email sequences, drip campaigns, lifecycle flows |

### SEO (5 skills)
| Skill | Description |
|-------|-------------|
| `ai-seo` | Optimize for AI search engines (ChatGPT, Perplexity) |
| `programmatic-seo` | Template-based pages at scale |
| `schema-markup` | Structured data and JSON-LD |
| `seo-audit` | Technical and on-page SEO audits |
| `site-architecture` | Site structure and navigation planning |

### CRO & Conversion (8 skills)
| Skill | Description |
|-------|-------------|
| `ab-test-setup` | A/B test planning and implementation |
| `analytics-tracking` | GA4, GTM, event tracking setup |
| `form-cro` | Form optimization (non-signup) |
| `onboarding-cro` | Post-signup activation and onboarding |
| `page-cro` | Landing page conversion optimization |
| `paywall-upgrade-cro` | In-app upgrade screens and paywalls |
| `popup-cro` | Popup and modal conversion optimization |
| `signup-flow-cro` | Signup/registration flow optimization |

### Growth (5 skills)
| Skill | Description |
|-------|-------------|
| `churn-prevention` | Cancellation flows and retention |
| `free-tool-strategy` | Engineering-as-marketing tool planning |
| `lead-magnets` | Content offers for lead generation |
| `pricing-strategy` | Pricing decisions and packaging |
| `referral-program` | Referral and affiliate programs |

### Sales (3 skills)
| Skill | Description |
|-------|-------------|
| `competitor-alternatives` | Competitor comparison pages |
| `revops` | Revenue operations and lead lifecycle |
| `sales-enablement` | Pitch decks, one-pagers, objection handling |

### Documents (4 skills)
| Skill | Description |
|-------|-------------|
| `docx` | Create and edit Word documents |
| `pdf` | Read, create, merge, split, OCR PDF files |
| `pptx` | Create and edit PowerPoint presentations |
| `xlsx` | Create and edit spreadsheets |

### Factories (5 skills)
| Skill | Description |
|-------|-------------|
| `agent-factory` | Create custom Claude Code agents |
| `hook-factory` | Generate Claude Code hooks |
| `manage-skills` | Install/update/list/remove skills from this collection |
| `prompt-factory` | Generate production-ready mega-prompts (69 presets) |
| `slash-command-factory` | Generate custom slash commands |

### Security (1 skill)
| Skill | Description |
|-------|-------------|
| `shannon` | Autonomous AI pentester for web apps |

### Integrations (4 skills)
| Skill | Description |
|-------|-------------|
| `codex` | OpenAI Codex CLI for second opinions |
| `gstack` | Full development workflow toolkit |
| `notebooklm` | Query Google NotebookLM from Claude Code |
| `valyu-best-practices` | Valyu API for real-time search |

## How Skills Work

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: my-skill
description: When to trigger this skill
---

# Skill prompt content here...
```

Skills are installed to `~/.claude/skills/` and become available as `/skill-name` slash commands in Claude Code.

## Smart Updates

The `skills-manifest.json` file tracks MD5 checksums for every skill. When you run `./install.sh --update`, it:

1. Pulls the latest from git
2. Compares checksums of each skill against what's installed
3. Only updates skills that have actually changed
4. Skips unchanged skills entirely

## Contributing

1. Fork this repo
2. Add your skill to `skills/your-skill-name/SKILL.md`
3. Run the manifest generator to update checksums
4. Submit a PR

## License

MIT
