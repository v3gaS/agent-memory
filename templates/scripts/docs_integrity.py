#!/usr/bin/env python3
"""Documentation integrity checks — stdlib-first, stack-agnostic.

Validates:
- Required docs from agent_memory.state.yaml (or built-in defaults)
- Relative markdown links resolve
- AGENTS.md links docs/README.md and states test discipline
- docs/README.md has agent task router
- No placeholder {{TOKENS}} left in KEEP docs (post-bootstrap)

Run: python3 scripts/docs_integrity.py
CI:  python3 -m pytest tests/test_docs_integrity.py -q
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[1]
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_]+\}\}")
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", "scaffold"}

DEFAULT_REQUIRED = (
    "AGENTS.md",
    "docs/README.md",
    "docs/SUBSYSTEM_TEMPLATE.md",
    "docs/BACKLOG.md",
    "docs/FINDINGS.md",
    "docs/CORE.md",
    "docs/OPERATIONS.md",
    "agent_memory.state.yaml",
)


@dataclass(frozen=True)
class Issue:
    path: Path
    message: str

    def render(self, root: Path) -> str:
        try:
            rel = self.path.relative_to(root)
        except ValueError:
            rel = self.path
        return f"{rel}: {self.message}"


def _load_state(root: Path) -> dict:
    state_path = root / "agent_memory.state.yaml"
    if yaml is None or not state_path.is_file():
        return {}
    data = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def required_docs(root: Path) -> tuple[str, ...]:
    state = _load_state(root)
    integrity = state.get("integrity") or {}
    req = integrity.get("required_docs")
    if isinstance(req, list) and req:
        return tuple(str(x) for x in req)
    return DEFAULT_REQUIRED


def check_required(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for rel in required_docs(root):
        p = root / rel
        if not p.is_file():
            issues.append(Issue(root / rel, "missing required doc"))
    return issues


def check_agents_contract(root: Path) -> list[Issue]:
    path = root / "AGENTS.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    issues: list[Issue] = []
    if "docs/README.md" not in text:
        issues.append(Issue(path, "must link docs/README.md"))
    if "never weaken" not in text.lower() and "never weaken the test" not in text.lower():
        issues.append(Issue(path, "must document test discipline (never weaken tests)"))
    if "## Ownership map" not in text:
        issues.append(Issue(path, "missing Ownership map section"))
    return issues


def check_docs_readme_router(root: Path) -> list[Issue]:
    path = root / "docs" / "README.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    issues: list[Issue] = []
    if "## Agent task router" not in text:
        issues.append(Issue(path, "missing Agent task router section"))
    if "| Tests |" not in text and "| Tests" not in text:
        issues.append(Issue(path, "task router must include Tests column"))
    return issues


def check_placeholders(root: Path) -> list[Issue]:
    """Fail if bootstrap placeholders remain in required docs."""
    issues: list[Issue] = []
    for rel in required_docs(root):
        p = root / rel
        if not p.is_file() or p.suffix != ".md":
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if PLACEHOLDER_RE.search(line):
                issues.append(Issue(p, f"unsubstituted placeholder line {i}: {line.strip()[:60]}"))
    return issues


def _iter_markdown(root: Path) -> list[Path]:
    paths: list[Path] = []
    for p in sorted(root.rglob("*.md")):
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        paths.append(p)
    return paths


def check_links(root: Path, files: list[Path] | None = None) -> list[Issue]:
    issues: list[Issue] = []
    targets = files or _iter_markdown(root)
    for path in targets:
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in MD_LINK_RE.findall(text):
            target = raw.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#")[0].strip()
            if not clean:
                continue
            dest = (path.parent / clean).resolve()
            if not dest.exists():
                issues.append(Issue(path, f"broken link: {target}"))
    return issues


def run_all(root: Path | None = None) -> list[Issue]:
    root = root or REPO_ROOT
    issues: list[Issue] = []
    issues.extend(check_required(root))
    issues.extend(check_agents_contract(root))
    issues.extend(check_docs_readme_router(root))
    # Placeholder check optional — only warn on AGENTS + docs/README during early bootstrap
    # Uncomment strict mode by setting AGENT_MEMORY_STRICT_PLACEHOLDERS=1
    import os
    if os.environ.get("AGENT_MEMORY_STRICT_PLACEHOLDERS") == "1":
        issues.extend(check_placeholders(root))
    doc_files = [root / r for r in required_docs(root) if (root / r).is_file()]
    issues.extend(check_links(root, [p for p in doc_files if p.suffix == ".md"]))
    issues.extend(check_links(root, [root / "docs" / "README.md", root / "AGENTS.md"]))
    return issues


def main() -> int:
    root = REPO_ROOT
    issues = run_all(root)
    if issues:
        for issue in issues:
            print(issue.render(root), file=sys.stderr)
        print(f"\n{len(issues)} issue(s)", file=sys.stderr)
        return 1
    print("docs integrity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
