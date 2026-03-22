#!/usr/bin/env python3
"""
Regenerate skills-manifest.json from the skills/ directory.

Usage:
    python3 lib/manifest.py                  # Regenerate manifest
    python3 lib/manifest.py --check          # Check if manifest is up-to-date
    python3 lib/manifest.py --checksums-only # Only update checksums
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJ_ROOT / "skills"
MANIFEST_PATH = PROJ_ROOT / "skills-manifest.json"

# Journey-based categories
CATEGORIES = {
    "1-validate": {
        "label": "Validate Your Idea",
        "phase": 1,
        "question": "Is this idea any good?",
        "skills": [
            "office-hours", "brainstorming", "product-marketing-context",
            "plan-ceo-review", "competitor-alternatives",
        ],
    },
    "2-build": {
        "label": "Build Your Product",
        "phase": 2,
        "question": "How do I build this?",
        "skills": [
            "writing-plans", "executing-plans", "frontend-design",
            "design-consultation", "plan-eng-review", "plan-design-review",
            "investigate", "test-driven-development",
            "subagent-driven-development", "using-git-worktrees",
            "receiving-code-review", "writing-skills", "gstack", "codex",
        ],
    },
    "3-ship": {
        "label": "Ship & Deploy",
        "phase": 3,
        "question": "How do I ship this?",
        "skills": [
            "ship", "review", "land-and-deploy", "setup-deploy", "qa",
            "qa-only", "browse", "setup-browser-cookies", "design-review",
            "benchmark", "canary", "document-release", "retro", "careful",
            "guard", "shannon",
        ],
    },
    "4-get-found": {
        "label": "Get Found",
        "phase": 4,
        "question": "How do people find me?",
        "skills": [
            "seo-audit", "ai-seo", "schema-markup", "programmatic-seo",
            "site-architecture", "content-strategy", "copywriting",
            "copy-editing", "social-content", "marketing-ideas",
            "marketing-psychology", "launch-strategy", "free-tool-strategy",
            "lead-magnets", "popup-cro",
        ],
    },
    "5-acquire": {
        "label": "Get Customers",
        "phase": 5,
        "question": "How do I get customers?",
        "skills": [
            "paid-ads", "ad-creative", "cold-email", "email-sequence",
            "referral-program", "sales-enablement", "revops",
            "competitor-alternatives",
        ],
    },
    "6-convert": {
        "label": "Convert Visitors",
        "phase": 6,
        "question": "Why aren't people converting?",
        "skills": [
            "page-cro", "signup-flow-cro", "form-cro", "paywall-upgrade-cro",
            "pricing-strategy", "ab-test-setup", "analytics-tracking",
            "onboarding-cro",
        ],
    },
    "7-retain": {
        "label": "Retain & Grow",
        "phase": 7,
        "question": "How do I keep customers?",
        "skills": ["churn-prevention", "email-sequence", "pricing-strategy"],
    },
    "8-power-tools": {
        "label": "Power Tools",
        "phase": 8,
        "question": "How do I work faster?",
        "skills": [
            "prompt-factory", "agent-factory", "slash-command-factory",
            "hook-factory", "manage-skills", "pdf", "docx", "pptx", "xlsx",
            "notebooklm", "valyu-best-practices", "freeze", "unfreeze",
        ],
    },
}


def dir_checksum(path: Path) -> str:
    """Compute deterministic MD5 of all files in a directory."""
    h = hashlib.md5()
    for root, dirs, files in os.walk(path):
        dirs.sort()
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            with open(fpath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
    return h.hexdigest()


def dir_stats(path: Path) -> tuple[int, int]:
    """Return (file_count, total_size_bytes) for a directory."""
    count = 0
    size = 0
    for root, _, files in os.walk(path):
        for fname in files:
            count += 1
            size += os.path.getsize(os.path.join(root, fname))
    return count, size


def extract_description(skill_path: Path) -> str:
    """Extract description from SKILL.md YAML frontmatter."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return ""
    with open(skill_md) as f:
        for line in f:
            line = line.strip()
            if line.startswith("description:"):
                desc = line.split("description:", 1)[1].strip().strip("\"'")
                if len(desc) > 120:
                    desc = desc[:120].rsplit(" ", 1)[0] + "..."
                return desc
    return ""


def build_phase_lookup() -> dict[str, list[str]]:
    """Build skill -> [phase_ids] reverse lookup."""
    lookup: dict[str, list[str]] = {}
    for cat_id, cat in CATEGORIES.items():
        for skill in cat["skills"]:
            lookup.setdefault(skill, []).append(cat_id)
    return lookup


def generate_manifest(checksums_only: bool = False) -> dict:
    """Generate the full manifest from disk."""
    phase_lookup = build_phase_lookup()

    # Load existing manifest if doing checksums-only update
    existing = {}
    if checksums_only and MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            existing = json.load(f)

    skills = {}
    for skill_path in sorted(SKILLS_DIR.iterdir()):
        if not skill_path.is_dir():
            continue
        name = skill_path.name
        file_count, size_bytes = dir_stats(skill_path)
        checksum = dir_checksum(skill_path)
        phases = phase_lookup.get(name, ["8-power-tools"])

        if checksums_only and name in existing.get("skills", {}):
            entry = existing["skills"][name].copy()
            entry["checksum"] = checksum
            entry["file_count"] = file_count
            entry["size_bytes"] = size_bytes
        else:
            entry = {
                "category": phases[0],
                "phases": phases,
                "checksum": checksum,
                "last_updated": datetime.fromtimestamp(
                    skill_path.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
                "file_count": file_count,
                "size_bytes": size_bytes,
                "description": extract_description(skill_path),
                "ranking": {"score": None, "tier": None, "signals": {}},
            }
        skills[name] = entry

    manifest = {
        "version": "3.0.0",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "repo": "https://github.com/matthewxfz3/amazing_cc_skills",
        "categories": CATEGORIES,
        "ranking": existing.get("ranking", {
            "method": "github_signals",
            "signals": ["stars", "forks", "issues_opened", "discussions", "contributors"],
            "last_ranked": None,
        }),
        "skills": skills,
    }
    return manifest


def main():
    check_mode = "--check" in sys.argv
    checksums_only = "--checksums-only" in sys.argv

    manifest = generate_manifest(checksums_only=checksums_only)

    if check_mode:
        if not MANIFEST_PATH.exists():
            print("Manifest does not exist", file=sys.stderr)
            sys.exit(1)
        with open(MANIFEST_PATH) as f:
            current = json.load(f)
        current_checksums = {
            k: v.get("checksum") for k, v in current.get("skills", {}).items()
        }
        new_checksums = {
            k: v.get("checksum") for k, v in manifest["skills"].items()
        }
        if current_checksums == new_checksums and set(current_checksums) == set(new_checksums):
            print(f"Manifest is up-to-date ({len(new_checksums)} skills)")
            sys.exit(0)
        else:
            changed = [
                k for k in new_checksums
                if new_checksums[k] != current_checksums.get(k)
            ]
            added = set(new_checksums) - set(current_checksums)
            removed = set(current_checksums) - set(new_checksums)
            print(f"Manifest is stale:", file=sys.stderr)
            if changed:
                print(f"  Changed: {', '.join(changed)}", file=sys.stderr)
            if added:
                print(f"  Added: {', '.join(added)}", file=sys.stderr)
            if removed:
                print(f"  Removed: {', '.join(removed)}", file=sys.stderr)
            sys.exit(1)

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(f"Generated manifest: {len(manifest['skills'])} skills across {len(CATEGORIES)} phases")


if __name__ == "__main__":
    main()
