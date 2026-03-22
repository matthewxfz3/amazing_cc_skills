#!/usr/bin/env python3
"""
Security scanner for Claude Code skills.

Scans SKILL.md and supporting files for risky patterns:
- Direct database access (SQLite, chat.db, etc.)
- Message sending (email, SMS, iMessage, Slack)
- File system access (read private dirs, home folder)
- Network calls (curl, fetch, API calls to external services)
- Credential access (keychain, env vars, tokens)
- Destructive commands (rm -rf, DROP TABLE, force-push)
- Data exfiltration (upload, POST to external, base64 encode + send)
- Code execution (eval, exec, subprocess with shell=True)

Usage:
    python3 lib/security.py                       # Scan all skills
    python3 lib/security.py --skill imessage       # Scan one skill
    python3 lib/security.py --json                 # Output JSON
    python3 lib/security.py --strict               # Fail on any warning
"""

import json
import os
import re
import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJ_ROOT / "skills"

# ============================================================================
# Risk patterns: (category, severity, pattern, description)
#
# Severity levels:
#   critical  — almost certainly dangerous (sending messages, DB access)
#   high      — likely dangerous (network calls, file access)
#   medium    — potentially dangerous (code execution, env vars)
#   low       — worth noting (logging, file writes)
# ============================================================================

RISK_PATTERNS = [
    # --- Database access ---
    ("database", "critical", r"chat\.db|messages\.db|contacts\.db", "Accesses local message/contact database"),
    ("database", "critical", r"~/Library/Messages|~/Library/Mail", "Accesses private macOS app data"),
    ("database", "high", r"sqlite3|sqlite|\.db\b", "Uses SQLite database access"),
    ("database", "high", r"SELECT\s+.+\s+FROM|INSERT\s+INTO|DELETE\s+FROM|DROP\s+TABLE", "Contains raw SQL queries"),

    # --- Messaging / sending ---
    ("messaging", "critical", r"send.?message|send.?text|send.?sms|send.?imessage", "Can send messages (iMessage/SMS)"),
    ("messaging", "critical", r"send.?email|smtp|sendgrid|mailgun|ses\.send", "Can send emails"),
    ("messaging", "high", r"slack.*post|slack.*send|webhook.*send", "Can post to Slack/webhooks"),
    ("messaging", "high", r"osascript.*Messages|tell application.*Messages", "Uses AppleScript to control Messages.app"),

    # --- File system access ---
    ("filesystem", "high", r"~/Library/|/Library/|/Users/\w+/Library", "Accesses macOS Library directories"),
    ("filesystem", "high", r"Full Disk Access|full.?disk.?access", "Requires Full Disk Access permission"),
    ("filesystem", "medium", r"~/.ssh|~/.aws|~/.config|~/.env|credentials", "Accesses sensitive config/credential files"),
    ("filesystem", "medium", r"keychain|security find-password|security find-generic", "Accesses macOS Keychain"),

    # --- Network / external calls ---
    ("network", "high", r"curl\s+.*POST|curl\s+.*-X\s+POST|requests\.post\(", "Makes POST requests to external services"),
    ("network", "medium", r"curl\s|wget\s|requests\.(get|put|delete)\(|fetch\(|urllib", "Makes network requests"),
    ("network", "medium", r"https?://(?!kroki\.io|cdn\.jsdelivr|github\.com|storage\.googleapis)", "Calls external URLs (not common CDNs)"),

    # --- Code execution ---
    ("execution", "high", r"eval\(|exec\(|subprocess.*shell\s*=\s*True", "Dynamic code execution (eval/exec/shell)"),
    ("execution", "medium", r"os\.system\(|os\.popen\(|subprocess\.run\(|subprocess\.Popen\(", "Spawns system processes"),
    ("execution", "medium", r"osascript|applescript", "Runs AppleScript (can control macOS apps)"),

    # --- Credential / token access ---
    ("credentials", "high", r"API.?KEY|API.?TOKEN|SECRET.?KEY|PRIVATE.?KEY|Bearer\s", "References API keys or tokens"),
    ("credentials", "high", r"password|passwd|OPENAI_API_KEY|ANTHROPIC_API_KEY", "References passwords or known API keys"),
    ("credentials", "medium", r"os\.environ|process\.env|getenv\(", "Reads environment variables"),

    # --- Destructive operations ---
    ("destructive", "critical", r"rm\s+-rf\s+[~/]|rm\s+-rf\s+/", "Destructive file deletion from root/home"),
    ("destructive", "high", r"git\s+push\s+.*--force|git\s+reset\s+--hard", "Force push or hard reset"),
    ("destructive", "medium", r"DROP\s+TABLE|TRUNCATE\s+TABLE|DELETE\s+FROM\s+\w+\s*;", "Destructive database operations"),

    # --- Data exfiltration ---
    ("exfiltration", "critical", r"base64.*encode.*curl|curl.*base64|upload.*private|exfil", "Potential data exfiltration pattern"),
    ("exfiltration", "high", r"upload.*to.*external|send.*data.*to.*server", "Sends data to external server"),

    # --- Privacy ---
    ("privacy", "high", r"location|GPS|geolocation|CLLocationManager", "Accesses location data"),
    ("privacy", "high", r"camera|microphone|screen.?capture|screenshot.*upload", "Accesses camera/microphone/screen"),
    ("privacy", "medium", r"browsing.?history|browser.?history|cookies|localStorage", "Accesses browser data"),
]

# Patterns to ignore (documentation, comments about security)
IGNORE_PATTERNS = [
    r"^#",           # Markdown headers
    r"^\s*//",       # Comments
    r"^\s*\*",       # Block comments
    r"DANGER WARNING",  # Our own warning text
    r"not intended for", # Our own disclaimers
]


# Directories that contain reference/educational content (not executable)
REFERENCE_DIRS = {"references", "examples", "evals", "templates", "presets", "node_modules"}


def scan_file(filepath: Path) -> list[dict]:
    """Scan a single file for risk patterns."""
    findings = []

    # Skip files in reference/educational directories
    parts = set(filepath.parts)
    is_reference_file = bool(parts & REFERENCE_DIRS)

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Skip lines that are clearly documentation
        is_doc = any(re.match(p, line.strip()) for p in IGNORE_PATTERNS)
        is_doc = is_doc or is_reference_file

        for category, severity, pattern, description in RISK_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "file": str(filepath.relative_to(PROJ_ROOT)),
                    "line": line_num,
                    "line_content": line.strip()[:120],
                    "category": category,
                    "severity": severity,
                    "description": description,
                    "pattern": pattern,
                    "in_documentation": is_doc,
                })

    return findings


def scan_skill(skill_name: str) -> dict:
    """Scan all files in a skill directory."""
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.is_dir():
        return {"skill": skill_name, "error": "not found", "findings": []}

    findings = []
    for filepath in skill_dir.rglob("*"):
        if filepath.is_file() and filepath.suffix in (
            ".md", ".py", ".js", ".ts", ".sh", ".bash", ".yaml", ".yml",
            ".json", ".toml", ".cfg", ".conf", ".html",
        ):
            findings.extend(scan_file(filepath))

    # Compute risk score
    severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
    # Don't count documentation mentions as heavily
    risk_score = sum(
        severity_weights.get(f["severity"], 0) * (0.1 if f["in_documentation"] else 1.0)
        for f in findings
    )

    # Determine risk level (thresholds tuned to reduce false positives)
    if risk_score >= 50:
        risk_level = "dangerous"
    elif risk_score >= 25:
        risk_level = "high"
    elif risk_score >= 10:
        risk_level = "medium"
    elif risk_score > 0:
        risk_level = "low"
    else:
        risk_level = "safe"

    # Unique categories found
    categories = sorted(set(f["category"] for f in findings))

    return {
        "skill": skill_name,
        "risk_level": risk_level,
        "risk_score": round(risk_score, 1),
        "categories": categories,
        "finding_count": len(findings),
        "critical_count": sum(1 for f in findings if f["severity"] == "critical"),
        "high_count": sum(1 for f in findings if f["severity"] == "high"),
        "medium_count": sum(1 for f in findings if f["severity"] == "medium"),
        "findings": findings,
    }


def scan_all() -> list[dict]:
    """Scan all skills."""
    results = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir():
            results.append(scan_skill(skill_dir.name))
    return results


def print_report(results: list[dict], verbose: bool = False) -> None:
    """Print human-readable security report."""
    # Summary
    total = len(results)
    dangerous = [r for r in results if r["risk_level"] == "dangerous"]
    high = [r for r in results if r["risk_level"] == "high"]
    medium = [r for r in results if r["risk_level"] == "medium"]
    low = [r for r in results if r["risk_level"] == "low"]
    safe = [r for r in results if r["risk_level"] == "safe"]

    print(f"\n{'='*60}")
    print(f"  Security Scan: {total} skills")
    print(f"{'='*60}\n")

    print(f"  🔴 Dangerous:  {len(dangerous)}")
    print(f"  🟠 High:       {len(high)}")
    print(f"  🟡 Medium:     {len(medium)}")
    print(f"  🔵 Low:        {len(low)}")
    print(f"  🟢 Safe:       {len(safe)}")
    print()

    # Detail for non-safe skills
    for group, label, emoji in [
        (dangerous, "DANGEROUS", "🔴"),
        (high, "HIGH RISK", "🟠"),
        (medium, "MEDIUM RISK", "🟡"),
    ]:
        if not group:
            continue
        print(f"  {emoji} {label}:")
        for r in sorted(group, key=lambda x: -x["risk_score"]):
            cats = ", ".join(r["categories"])
            print(f"    {r['skill']:30s} score={r['risk_score']:5.1f}  [{cats}]")
            if verbose:
                for f in r["findings"]:
                    doc = " (doc)" if f["in_documentation"] else ""
                    print(f"      L{f['line']:4d} [{f['severity']:8s}] {f['description']}{doc}")
                    print(f"             {f['line_content']}")
                print()
        print()

    # Safe skills (just list)
    if safe and not verbose:
        print(f"  🟢 SAFE ({len(safe)} skills): {', '.join(r['skill'] for r in safe[:10])}", end="")
        if len(safe) > 10:
            print(f" ... and {len(safe)-10} more")
        else:
            print()
    print()


def main():
    json_output = "--json" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    strict = "--strict" in sys.argv

    # Single skill scan
    skill_name = None
    for i, arg in enumerate(sys.argv):
        if arg == "--skill" and i + 1 < len(sys.argv):
            skill_name = sys.argv[i + 1]

    if skill_name:
        result = scan_skill(skill_name)
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print_report([result], verbose=True)
        if strict and result["risk_level"] in ("dangerous", "high"):
            sys.exit(1)
    else:
        results = scan_all()
        if json_output:
            print(json.dumps(results, indent=2))
        else:
            print_report(results, verbose=verbose)
        if strict:
            dangerous = [r for r in results if r["risk_level"] in ("dangerous", "high")]
            if dangerous:
                print(f"STRICT MODE: {len(dangerous)} skills flagged as dangerous/high risk")
                sys.exit(1)


if __name__ == "__main__":
    main()
