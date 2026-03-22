#!/usr/bin/env python3
"""
Scenario index for amazing_cc_skills.

Maps real-world problems/situations to the skills that solve them.
Each phase has multiple scenarios. Each scenario has:
  - trigger: what the user says or the situation they're in
  - skills: ordered list of skills to use (best first)

This file is the single source of truth for scenario definitions.
"""

SCENARIOS = {
    "1-validate": {
        "label": "Validate Your Idea",
        "scenarios": {
            "is-this-worth-building": {
                "trigger": "I have an idea but don't know if anyone would pay for it",
                "problem": "Unvalidated idea, risk of building something nobody wants",
                "skills": ["office-hours", "brainstorming"],
            },
            "who-is-my-customer": {
                "trigger": "I don't know who my target customer is or how to describe my product",
                "problem": "Unclear positioning, ICP, or value proposition",
                "skills": ["product-marketing-context"],
            },
            "am-i-thinking-big-enough": {
                "trigger": "I have a plan but I'm not sure if the scope is right",
                "problem": "Scope uncertainty — too ambitious or not ambitious enough",
                "skills": ["plan-ceo-review"],
            },
            "who-are-my-competitors": {
                "trigger": "I need to understand the competitive landscape",
                "problem": "Don't know how competitors position or what alternatives exist",
                "skills": ["competitor-alternatives"],
            },
        },
    },
    "2-build": {
        "label": "Build Your Product",
        "scenarios": {
            "plan-before-coding": {
                "trigger": "I have requirements but need to plan the implementation",
                "problem": "Complex task that needs breaking down before writing code",
                "skills": ["writing-plans", "executing-plans"],
            },
            "build-the-ui": {
                "trigger": "I need to build a frontend that looks professional",
                "problem": "Need production-grade UI, not generic AI-looking output",
                "skills": ["frontend-design", "design-consultation"],
            },
            "review-architecture": {
                "trigger": "I want someone to check my architecture before I build",
                "problem": "Risk of structural issues, wrong patterns, or missed edge cases",
                "skills": ["plan-eng-review", "plan-design-review"],
            },
            "something-is-broken": {
                "trigger": "I have a bug and I don't know why",
                "problem": "Unexpected behavior, test failures, or errors",
                "skills": ["investigate"],
            },
            "write-tests-first": {
                "trigger": "I want to implement a feature with proper test coverage",
                "problem": "Need confidence that new code works and doesn't break existing code",
                "skills": ["test-driven-development"],
            },
            "parallelize-work": {
                "trigger": "I have multiple independent tasks to do at once",
                "problem": "Sequential work is too slow, tasks don't depend on each other",
                "skills": ["subagent-driven-development"],
            },
            "handle-code-review": {
                "trigger": "I got code review feedback and I'm not sure I agree with all of it",
                "problem": "Need to evaluate feedback critically, not just accept blindly",
                "skills": ["receiving-code-review"],
            },
            "isolate-feature-work": {
                "trigger": "I want to work on a feature without affecting the main branch",
                "problem": "Need isolation for risky or long-running changes",
                "skills": ["using-git-worktrees"],
            },
            "create-custom-skill": {
                "trigger": "I want to create a reusable skill for my own workflow",
                "problem": "Repetitive workflow that should be automated as a skill",
                "skills": ["writing-skills"],
            },
            "get-second-opinion": {
                "trigger": "I want another AI to review or challenge my code",
                "problem": "Need an independent perspective on code quality",
                "skills": ["codex"],
            },
        },
    },
    "3-ship": {
        "label": "Ship & Deploy",
        "scenarios": {
            "ready-to-ship": {
                "trigger": "My code is ready, I want to create a PR and ship it",
                "problem": "Need full ship workflow: tests, review, version bump, PR",
                "skills": ["ship"],
            },
            "review-before-merge": {
                "trigger": "I want to review the diff before landing this PR",
                "problem": "Need to catch security issues, side effects, or structural problems",
                "skills": ["review"],
            },
            "deploy-to-production": {
                "trigger": "PR is approved, I want to merge and verify production",
                "problem": "Need to merge, wait for CI, and confirm production health",
                "skills": ["land-and-deploy", "setup-deploy"],
            },
            "test-the-app": {
                "trigger": "I need to QA test my app and fix bugs",
                "problem": "Don't know if the app works correctly end-to-end",
                "skills": ["qa", "qa-only", "browse"],
            },
            "test-authenticated-pages": {
                "trigger": "I need to test pages that require login",
                "problem": "Headless browser doesn't have my session/cookies",
                "skills": ["setup-browser-cookies", "browse"],
            },
            "check-visual-quality": {
                "trigger": "The app works but the design looks off",
                "problem": "Spacing, alignment, hierarchy, or consistency issues",
                "skills": ["design-review"],
            },
            "check-performance": {
                "trigger": "I want to make sure my changes didn't slow things down",
                "problem": "Need before/after performance comparison",
                "skills": ["benchmark"],
            },
            "monitor-after-deploy": {
                "trigger": "I just deployed, I want to watch for errors",
                "problem": "Need to catch post-deploy regressions quickly",
                "skills": ["canary"],
            },
            "update-docs-after-shipping": {
                "trigger": "I shipped a feature, now docs are outdated",
                "problem": "README, CHANGELOG, and other docs don't match what shipped",
                "skills": ["document-release"],
            },
            "weekly-team-review": {
                "trigger": "What did we ship this week? What went well?",
                "problem": "Need structured retrospective with data",
                "skills": ["retro"],
            },
            "working-on-production": {
                "trigger": "I'm touching production systems and don't want to break anything",
                "problem": "Risk of destructive commands or accidental changes",
                "skills": ["guard", "careful"],
            },
            "security-audit": {
                "trigger": "I want to check my app for vulnerabilities before launch",
                "problem": "Need to find real security issues, not just theoretical ones",
                "skills": ["shannon"],
            },
        },
    },
    "4-get-found": {
        "label": "Get Found",
        "scenarios": {
            "not-ranking-in-google": {
                "trigger": "My site isn't showing up in Google search results",
                "problem": "Technical SEO issues, missing meta tags, or poor content",
                "skills": ["seo-audit"],
            },
            "not-showing-in-ai-search": {
                "trigger": "I want ChatGPT and Perplexity to mention my product",
                "problem": "Content isn't structured for AI citation or extraction",
                "skills": ["ai-seo"],
            },
            "no-rich-results": {
                "trigger": "My search results don't show stars, FAQs, or other rich data",
                "problem": "Missing structured data / JSON-LD markup",
                "skills": ["schema-markup"],
            },
            "need-lots-of-seo-pages": {
                "trigger": "I want to rank for hundreds of keywords at scale",
                "problem": "Can't manually create pages for every keyword variation",
                "skills": ["programmatic-seo"],
            },
            "planning-site-structure": {
                "trigger": "I'm building a new site and need to plan the page hierarchy",
                "problem": "Unclear navigation, URL structure, or internal linking",
                "skills": ["site-architecture"],
            },
            "dont-know-what-to-write": {
                "trigger": "I need a content strategy but I don't know where to start",
                "problem": "No plan for what topics to cover or in what order",
                "skills": ["content-strategy"],
            },
            "need-page-copy": {
                "trigger": "I need to write compelling copy for my website",
                "problem": "Blank page, weak headlines, unclear value proposition",
                "skills": ["copywriting", "copy-editing"],
            },
            "need-social-media-content": {
                "trigger": "I need posts for LinkedIn, Twitter, Instagram",
                "problem": "Don't know what to post or how to repurpose content",
                "skills": ["social-content"],
            },
            "stuck-on-marketing": {
                "trigger": "I don't know how to market my product",
                "problem": "No marketing ideas, need inspiration",
                "skills": ["marketing-ideas", "marketing-psychology"],
            },
            "launching-a-product": {
                "trigger": "I'm about to launch and need a plan",
                "problem": "No launch strategy, don't know how to maximize impact",
                "skills": ["launch-strategy"],
            },
            "need-lead-magnets": {
                "trigger": "I want to capture emails with free content or tools",
                "problem": "No lead magnets, gated content, or free tools",
                "skills": ["lead-magnets", "free-tool-strategy", "popup-cro"],
            },
        },
    },
    "5-acquire": {
        "label": "Get Customers",
        "scenarios": {
            "run-paid-ads": {
                "trigger": "I want to run Google or Facebook ads",
                "problem": "No ad strategy, targeting, or budget plan",
                "skills": ["paid-ads", "ad-creative"],
            },
            "cold-outbound": {
                "trigger": "I want to reach out to potential customers directly",
                "problem": "Cold emails that don't get replies",
                "skills": ["cold-email"],
            },
            "nurture-leads": {
                "trigger": "I have leads but they're not converting to customers",
                "problem": "No email sequences to warm up and nurture leads",
                "skills": ["email-sequence"],
            },
            "get-referrals": {
                "trigger": "I want existing customers to bring me new ones",
                "problem": "No referral program or viral loop",
                "skills": ["referral-program"],
            },
            "enable-sales-team": {
                "trigger": "My sales team needs better materials",
                "problem": "No pitch decks, one-pagers, or objection handling docs",
                "skills": ["sales-enablement"],
            },
            "leads-not-reaching-sales": {
                "trigger": "Marketing generates leads but sales doesn't follow up",
                "problem": "No lead scoring, routing, or handoff process",
                "skills": ["revops"],
            },
            "win-comparison-shoppers": {
                "trigger": "Prospects are comparing us to competitors",
                "problem": "No comparison pages or competitive positioning",
                "skills": ["competitor-alternatives"],
            },
        },
    },
    "6-convert": {
        "label": "Convert Visitors",
        "scenarios": {
            "landing-page-not-converting": {
                "trigger": "People visit my page but don't sign up or buy",
                "problem": "Low conversion rate on landing/pricing/feature pages",
                "skills": ["page-cro"],
            },
            "signup-dropoff": {
                "trigger": "People start signing up but don't finish",
                "problem": "Friction in registration flow, too many steps or fields",
                "skills": ["signup-flow-cro"],
            },
            "forms-not-working": {
                "trigger": "My lead capture or contact form has low completion",
                "problem": "Too many fields, confusing layout, or unclear value",
                "skills": ["form-cro"],
            },
            "free-users-wont-pay": {
                "trigger": "Free users aren't upgrading to paid",
                "problem": "Weak upgrade prompts, unclear value of paid tier",
                "skills": ["paywall-upgrade-cro"],
            },
            "what-should-i-charge": {
                "trigger": "I don't know how to price my product",
                "problem": "Unclear pricing model, tiers, or willingness to pay",
                "skills": ["pricing-strategy"],
            },
            "need-to-test-changes": {
                "trigger": "I changed something and want to know if it actually helped",
                "problem": "No A/B test framework or statistical rigor",
                "skills": ["ab-test-setup"],
            },
            "dont-know-whats-happening": {
                "trigger": "I can't tell what users are doing on my site",
                "problem": "No analytics, event tracking, or conversion measurement",
                "skills": ["analytics-tracking"],
            },
            "users-sign-up-but-dont-stick": {
                "trigger": "People create accounts but never come back",
                "problem": "No onboarding flow, users don't reach the aha moment",
                "skills": ["onboarding-cro"],
            },
        },
    },
    "7-retain": {
        "label": "Retain & Grow",
        "scenarios": {
            "customers-canceling": {
                "trigger": "People keep canceling their subscriptions",
                "problem": "No save offers, exit surveys, or win-back flows",
                "skills": ["churn-prevention"],
            },
            "users-going-inactive": {
                "trigger": "Active users are becoming inactive over time",
                "problem": "No re-engagement emails or lifecycle communication",
                "skills": ["email-sequence"],
            },
            "pricing-not-working": {
                "trigger": "Revenue isn't growing even though users are growing",
                "problem": "Wrong pricing, packaging, or value metric",
                "skills": ["pricing-strategy"],
            },
        },
    },
    "8-power-tools": {
        "label": "Power Tools",
        "scenarios": {
            "generate-prompts": {
                "trigger": "I need a production-ready prompt for a specific role or task",
                "problem": "Writing good prompts from scratch is slow and inconsistent",
                "skills": ["prompt-factory"],
            },
            "create-agents": {
                "trigger": "I want to build a custom AI agent for my workflow",
                "problem": "Need structured agent with proper tools and MCP integration",
                "skills": ["agent-factory"],
            },
            "create-commands": {
                "trigger": "I want a custom slash command for a repeated workflow",
                "problem": "Doing the same multi-step task manually every time",
                "skills": ["slash-command-factory"],
            },
            "create-hooks": {
                "trigger": "I want Claude Code to automatically do something on events",
                "problem": "Need automated behaviors tied to tool calls or file changes",
                "skills": ["hook-factory"],
            },
            "manage-skill-collection": {
                "trigger": "I want to install, update, or remove skills",
                "problem": "Need to manage the amazing_cc_skills collection",
                "skills": ["manage-skills"],
            },
            "work-with-documents": {
                "trigger": "I need to create, read, or edit PDF/Word/PowerPoint/Excel files",
                "problem": "Need to process office documents programmatically",
                "skills": ["pdf", "docx", "pptx", "xlsx"],
            },
            "research-with-sources": {
                "trigger": "I need source-grounded answers or real-time search",
                "problem": "Need citations from documents or live web/academic data",
                "skills": ["notebooklm", "valyu-best-practices"],
            },
            "scope-edits-safely": {
                "trigger": "I want to restrict edits to one folder while debugging",
                "problem": "Risk of accidentally changing unrelated code",
                "skills": ["freeze", "unfreeze"],
            },
        },
    },
}


def get_all_scenarios() -> dict:
    """Return the full scenario tree."""
    return SCENARIOS


def find_skills_for_problem(query: str) -> list[dict]:
    """Search scenarios by trigger or problem text. Returns matching scenarios."""
    query_lower = query.lower()
    results = []
    for phase_id, phase in SCENARIOS.items():
        for scenario_id, scenario in phase["scenarios"].items():
            trigger = scenario["trigger"].lower()
            problem = scenario["problem"].lower()
            if query_lower in trigger or query_lower in problem:
                results.append({
                    "phase": phase_id,
                    "phase_label": phase["label"],
                    "scenario": scenario_id,
                    "trigger": scenario["trigger"],
                    "problem": scenario["problem"],
                    "skills": scenario["skills"],
                })
    return results


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--search":
        query = " ".join(sys.argv[2:])
        results = find_skills_for_problem(query)
        if results:
            for r in results:
                print(f"[{r['phase']}] {r['scenario']}")
                print(f"  Trigger: {r['trigger']}")
                print(f"  Skills:  {', '.join(r['skills'])}")
                print()
        else:
            print(f"No scenarios match '{query}'")
    else:
        print(json.dumps(SCENARIOS, indent=2))
