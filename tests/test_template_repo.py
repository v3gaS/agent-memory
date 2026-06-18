"""Self-tests for the agent-memory template repository (standalone checkout)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install.sh"


@pytest.fixture
def smoke_target(tmp_path: Path) -> Path:
    target = tmp_path / "app"
    target.mkdir()
    proc = subprocess.run(
        [
            "bash",
            str(INSTALL),
            "--local",
            "--target",
            str(target),
            "--yes",
            "--preset",
            "python",
            "--project-name",
            "Template Repo Smoke",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": os.environ.get("PATH", "")},
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return target


def test_install_sh_exists() -> None:
    assert INSTALL.is_file()


def test_version_file() -> None:
    assert (ROOT / "VERSION").is_file()


def test_install_smoke_creates_agents_md(smoke_target: Path) -> None:
    assert (smoke_target / "AGENTS.md").is_file()


def test_install_smoke_docs_integrity(smoke_target: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(smoke_target / "scripts" / "docs_integrity.py")],
        cwd=smoke_target,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
