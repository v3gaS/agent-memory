"""Regression tests for the agent-memory documentation system."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts" / "docs_integrity.py"


@pytest.fixture(scope="module")
def repo_root() -> Path:
    return REPO_ROOT


def test_docs_integrity_script_exists(repo_root: Path) -> None:
    assert SCRIPTS.is_file(), "scripts/docs_integrity.py must exist"


def test_docs_integrity_passes(repo_root: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_agents_md_documents_test_discipline(repo_root: Path) -> None:
    agents = repo_root / "AGENTS.md"
    assert agents.is_file()
    text = agents.read_text(encoding="utf-8").lower()
    assert "never weaken" in text, "AGENTS.md must forbid weakening tests to pass"


def test_cursorrules_documents_test_discipline(repo_root: Path) -> None:
    rules = repo_root / ".cursorrules"
    assert rules.is_file()
    text = rules.read_text(encoding="utf-8").lower()
    assert "never weaken" in text, ".cursorrules must forbid weakening tests to pass"


def test_required_docs_present(repo_root: Path) -> None:
    required = [
        "AGENTS.md",
        "docs/README.md",
        "docs/BACKLOG.md",
        "docs/FINDINGS.md",
        "agent_memory.state.yaml",
    ]
    for rel in required:
        assert (repo_root / rel).is_file(), f"missing {rel}"


def test_state_yaml_has_test_discipline(repo_root: Path) -> None:
    state_path = repo_root / "agent_memory.state.yaml"
    if not state_path.is_file():
        pytest.skip("agent_memory.state.yaml not present")
    text = state_path.read_text(encoding="utf-8")
    assert "never_weaken_tests" in text or "test_discipline" in text
