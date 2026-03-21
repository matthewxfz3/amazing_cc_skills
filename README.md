# amazing_cc_skills

A curated collection of **85+ production-ready Claude Code skills** — install them all in one command and supercharge your Claude Code workflow.

Skills are organized across engineering, marketing, design, DevOps, security, and more. This repo is **AI-native**: it includes a `CLAUDE.md` for Claude Code context, a `skills-manifest.json` for smart update detection, and a built-in `/manage-skills` skill so you can install and update everything without leaving your Claude Code session.

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

- **85+ skills** across 10+ categories
- **Parallel installation** — installs multiple skills simultaneously
- **Fault-tolerant** — one skill failure never blocks the rest
- **Smart updates** — checksums in `skills-manifest.json` detect changes, skip unchanged skills
- **Symlink by default** — `git pull` in the repo auto-updates your skills
- **Offline fallback** — works without network using the local `skills/` archive
- **AI-native** — `CLAUDE.md` + `/manage-skills` for seamless Claude Code integration

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

## Skill Categories

### Engineering & Development
| Skill | Description |
|-------|-------------|
| `systematic-debugging` | Structured debugging with root cause analysis |
| `test-driven-development` | TDD workflow — tests before implementation |
| `writing-plans` | Multi-step task planning before coding |
| `executing-plans` | Execute implementation plans with review checkpoints |
| `dispatching-parallel-agents` | Run 2+ independent tasks in parallel |
| `subagent-driven-development` | Implementation via independent sub-agents |
| `verification-before-completion` | Verify work before claiming completion |
| `receiving-code-review` | Handle code review feedback with rigor |
| `requesting-code-review` | Request reviews before merging |
| `finishing-a-development-branch` | Guide branch completion (merge, PR, cleanup) |
| `using-git-worktrees` | Isolated git worktrees for feature work |
| `investigate` | 4-phase debugging: investigate, analyze, hypothesize, implement |
| `frontend-design` | Production-grade frontend interfaces |
| `brainstorming` | Explore intent and requirements before building |

### Shipping & DevOps
| Skill | Description |
|-------|-------------|
| `ship` | Full ship workflow: tests, review, version bump, PR |
| `review` | Pre-landing PR review for structural issues |
| `land-and-deploy` | Merge PR, wait for CI, verify production health |
| `setup-deploy` | Configure deployment settings |
| `canary` | Post-deploy canary monitoring |
| `benchmark` | Performance regression detection |
| `retro` | Weekly engineering retrospective |
| `document-release` | Post-ship documentation updates |
| `careful` | Safety guardrails for destructive commands |
| `freeze` | Restrict edits to a specific directory |
| `unfreeze` | Remove freeze restrictions |
| `guard` | Maximum safety mode (careful + freeze) |

### QA & Testing
| Skill | Description |
|-------|-------------|
| `qa` | Systematic QA testing with iterative bug fixes |
| `qa-only` | Report-only QA testing (no fixes) |
| `browse` | Headless browser for testing and verification |
| `setup-browser-cookies` | Import browser cookies for authenticated testing |
| `design-review` | Visual QA: spacing, hierarchy, consistency fixes |

### Marketing & Growth
| Skill | Description |
|-------|-------------|
| `copywriting` | Marketing copy for any page type |
| `copy-editing` | Edit and improve existing copy |
| `content-strategy` | Plan what content to create |
| `email-sequence` | Email sequences, drip campaigns, lifecycle flows |
| `cold-email` | B2B cold outreach that gets replies |
| `social-content` | Social media content creation |
| `ad-creative` | Ad copy at scale for any platform |
| `paid-ads` | PPC campaign strategy and optimization |
| `marketing-ideas` | Marketing inspiration and strategies |
| `marketing-psychology` | Behavioral science for marketing |
| `launch-strategy` | Product launch planning |
| `lead-magnets` | Content offers for lead generation |
| `free-tool-strategy` | Engineering-as-marketing tool planning |
| `referral-program` | Referral and affiliate programs |
| `product-marketing-context` | Foundational product/audience context |

### SEO & Search
| Skill | Description |
|-------|-------------|
| `seo-audit` | Technical and on-page SEO audits |
| `ai-seo` | Optimize for AI search engines (ChatGPT, Perplexity) |
| `schema-markup` | Structured data and JSON-LD |
| `programmatic-seo` | Template-based pages at scale |
| `site-architecture` | Site structure and navigation planning |

### CRO & Conversion
| Skill | Description |
|-------|-------------|
| `page-cro` | Landing page conversion optimization |
| `signup-flow-cro` | Signup/registration flow optimization |
| `onboarding-cro` | Post-signup activation and onboarding |
| `form-cro` | Form optimization (non-signup) |
| `popup-cro` | Popup and modal conversion optimization |
| `paywall-upgrade-cro` | In-app upgrade screens and paywalls |
| `ab-test-setup` | A/B test planning and implementation |
| `analytics-tracking` | GA4, GTM, event tracking setup |
| `churn-prevention` | Cancellation flows and retention |
| `pricing-strategy` | Pricing decisions and packaging |

### Sales & Revenue
| Skill | Description |
|-------|-------------|
| `sales-enablement` | Pitch decks, one-pagers, objection handling |
| `competitor-alternatives` | Competitor comparison pages |
| `revops` | Revenue operations and lead lifecycle |

### Design
| Skill | Description |
|-------|-------------|
| `design-consultation` | Design system creation (DESIGN.md) |
| `plan-design-review` | Design plan review before implementation |
| `plan-ceo-review` | CEO/founder-mode plan review |
| `plan-eng-review` | Engineering manager plan review |
| `office-hours` | YC-style brainstorming and idea validation |

### Document & File Processing
| Skill | Description |
|-------|-------------|
| `pdf` | Read, create, merge, split, OCR PDF files |
| `docx` | Create and edit Word documents |
| `pptx` | Create and edit PowerPoint presentations |
| `xlsx` | Create and edit spreadsheets |

### Factories (Meta-Skills)
| Skill | Description |
|-------|-------------|
| `prompt-factory` | Generate production-ready mega-prompts (69 presets) |
| `agent-factory` | Create custom Claude Code agents |
| `slash-command-factory` | Generate custom slash commands |
| `hook-factory` | Generate Claude Code hooks |
| `manage-skills` | Install/update/list/remove skills from this collection |

### Security & Advanced
| Skill | Description |
|-------|-------------|
| `shannon` | Autonomous AI pentester for web apps |
| `codex` | OpenAI Codex CLI for second opinions |
| `notebooklm` | Query Google NotebookLM from Claude Code |
| `valyu-best-practices` | Valyu API for real-time search |
| `gstack` | Full development workflow toolkit |
| `gstack-upgrade` | Upgrade gstack to latest version |
| `using-superpowers` | Skill discovery and usage patterns |
| `writing-skills` | Create and verify new skills |

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
