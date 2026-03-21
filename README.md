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

## Skills by Startup Journey

Every startup asks the same questions in roughly the same order. Skills are organized by **when you need them**, not what technology they use.

---

### Phase 1: "Is this idea any good?" — Validate (5 skills)

> Before you write a line of code. Figure out if anyone cares.

| Skill | What it does for you |
|-------|---------------------|
| `office-hours` | YC-style forcing questions — exposes whether there's real demand |
| `brainstorming` | Explores requirements and design before you commit to building |
| `product-marketing-context` | Forces you to define your ICP, positioning, and value prop |
| `plan-ceo-review` | Challenges your scope — are you thinking too small or too big? |
| `competitor-alternatives` | Maps the competitive landscape so you know where you fit |

---

### Phase 2: "How do I build this?" — Build (14 skills)

> You've validated. Now build the thing — fast, with quality.

| Skill | What it does for you |
|-------|---------------------|
| `writing-plans` | Plan before coding — spec out multi-step tasks |
| `executing-plans` | Follow the plan with review checkpoints |
| `frontend-design` | Production-grade UI that doesn't look like AI slop |
| `design-consultation` | Create a design system (typography, colors, spacing) |
| `plan-eng-review` | Architecture review before you start coding |
| `plan-design-review` | Design review before implementation |
| `investigate` | 4-phase debugging when things break |
| `test-driven-development` | Tests first, then implementation |
| `subagent-driven-development` | Parallelize independent build tasks |
| `using-git-worktrees` | Isolate feature work without breaking main |
| `receiving-code-review` | Handle feedback with rigor, not blind agreement |
| `writing-skills` | Create custom skills for your own workflow |
| `gstack` | Full development workflow toolkit |
| `codex` | Second opinion from a different AI system |

---

### Phase 3: "How do I ship this?" — Ship (16 skills)

> Code is done. Now get it live — safely, reliably, fast.

| Skill | What it does for you |
|-------|---------------------|
| `ship` | Full workflow: tests, review, version bump, changelog, PR |
| `review` | Pre-landing PR review — catches security and structural issues |
| `land-and-deploy` | Merge, wait for CI, verify production health |
| `setup-deploy` | Configure your deploy platform (Vercel, Fly, Render, etc.) |
| `qa` | Systematic QA testing — finds and fixes bugs |
| `qa-only` | QA report without touching code (for stakeholder review) |
| `browse` | Headless browser — test flows, take screenshots, verify state |
| `setup-browser-cookies` | Import real cookies for testing authenticated pages |
| `design-review` | Visual QA — catches spacing, hierarchy, consistency issues |
| `benchmark` | Performance regression detection before/after |
| `canary` | Post-deploy monitoring — watches for errors in production |
| `document-release` | Update docs after shipping |
| `retro` | Weekly retrospective — what shipped, what broke, what's next |
| `careful` | Safety guardrails for destructive commands |
| `guard` | Maximum safety mode for production work |
| `shannon` | Security audit — finds real vulnerabilities before attackers do |

---

### Phase 4: "How do people find me?" — Get Found (15 skills)

> Your product is live. Now the hardest part: getting noticed.

| Skill | What it does for you |
|-------|---------------------|
| `seo-audit` | Find out why you're not ranking and fix it |
| `ai-seo` | Get cited by ChatGPT, Perplexity, and AI search engines |
| `schema-markup` | Rich results in Google (stars, FAQs, breadcrumbs) |
| `programmatic-seo` | Build hundreds of SEO pages from templates + data |
| `site-architecture` | Plan your site structure, URLs, and internal linking |
| `content-strategy` | Decide what content to create and in what order |
| `copywriting` | Write compelling page copy that converts |
| `copy-editing` | Polish existing copy — tighten, sharpen, clarify |
| `social-content` | Create content for LinkedIn, Twitter/X, Instagram, TikTok |
| `marketing-ideas` | Unstuck yourself — get fresh marketing inspiration |
| `marketing-psychology` | Apply cognitive biases and persuasion principles |
| `launch-strategy` | Plan your Product Hunt launch, beta release, or announcement |
| `free-tool-strategy` | Build a free tool that generates leads and backlinks |
| `lead-magnets` | Create ebooks, checklists, templates for email capture |
| `popup-cro` | Optimize popups and modals for email collection |

---

### Phase 5: "How do I get customers?" — Acquire (8 skills)

> Traffic is flowing. Now turn strangers into leads, leads into customers.

| Skill | What it does for you |
|-------|---------------------|
| `paid-ads` | Google/Meta/LinkedIn ad campaigns — strategy and optimization |
| `ad-creative` | Generate ad copy variations at scale |
| `cold-email` | B2B outbound that actually gets replies |
| `email-sequence` | Nurture sequences, onboarding drips, re-engagement flows |
| `referral-program` | Get existing customers to bring you new ones |
| `sales-enablement` | Pitch decks, one-pagers, objection handling docs |
| `revops` | Lead scoring, routing, and marketing-to-sales handoff |
| `competitor-alternatives` | "Us vs Them" pages that win comparison shoppers |

---

### Phase 6: "Why aren't people converting?" — Convert (8 skills)

> You have visitors. They're not signing up or paying. Fix the funnel.

| Skill | What it does for you |
|-------|---------------------|
| `page-cro` | Diagnose and fix underperforming landing pages |
| `signup-flow-cro` | Reduce friction in your registration flow |
| `form-cro` | Optimize lead capture and contact forms |
| `paywall-upgrade-cro` | Design upgrade screens that convert free to paid |
| `pricing-strategy` | Figure out what to charge and how to package it |
| `ab-test-setup` | Test two versions and know which one wins |
| `analytics-tracking` | Set up GA4, GTM, events — know what's actually happening |
| `onboarding-cro` | Get new signups to their "aha moment" faster |

---

### Phase 7: "How do I keep customers?" — Retain & Grow (3 skills)

> Acquisition without retention is a leaky bucket. Plug the holes.

| Skill | What it does for you |
|-------|---------------------|
| `churn-prevention` | Cancel flows, save offers, dunning, win-back strategies |
| `email-sequence` | Re-engagement and lifecycle emails to keep users active |
| `pricing-strategy` | Adjust tiers and packaging as you learn what customers value |

---

### Phase 8: "How do I work faster?" — Power Tools (10 skills)

> Multiply your output. These skills make everything above faster.

| Skill | What it does for you |
|-------|---------------------|
| `prompt-factory` | Generate production-ready prompts for any role (69 presets) |
| `agent-factory` | Create custom AI agents for your specific workflows |
| `slash-command-factory` | Build custom Claude Code commands |
| `hook-factory` | Automate Claude Code behaviors with hooks |
| `manage-skills` | Install, update, list, remove skills from this collection |
| `pdf` | Read, create, merge, split, OCR any PDF |
| `docx` | Create and edit Word documents |
| `pptx` | Create and edit presentations |
| `xlsx` | Create and edit spreadsheets |
| `notebooklm` | Query Google NotebookLM for source-grounded research |
| `valyu-best-practices` | Real-time search across web, academic, financial sources |
| `freeze` / `unfreeze` | Scope edits to one directory to avoid accidental changes |

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
