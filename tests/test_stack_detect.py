"""Tests for stack_detect.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCAFFOLD = Path(__file__).resolve().parents[1]
STACK_DETECT = SCAFFOLD / "stack_detect.py"


def test_detect_python_project(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(STACK_DETECT), "--root", str(tmp_path), "--json"],
        capture_output=True,
        text=True,
        cwd=SCAFFOLD,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert "Python" in data["summary"]
    assert data["default_test_command"] == "pytest -q"


def test_detect_node_monorepo(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"next": "14", "react": "18"}, "scripts": {"test": "jest"}}),
        encoding="utf-8",
    )
    (tmp_path / "apps").mkdir()
    (tmp_path / "apps" / "web").mkdir()
    (tmp_path / "apps" / "web" / "package.json").write_text("{}", encoding="utf-8")
    (tmp_path / "pnpm-workspace.yaml").write_text("packages:\n  - apps/*\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(STACK_DETECT), "--root", str(tmp_path), "--json"],
        capture_output=True,
        text=True,
        cwd=SCAFFOLD,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert "Node.js" in data["summary"]
    assert "Next.js" in data["summary"]
    assert "monorepo" in data["summary"].lower()
    assert data["default_test_command"] == "npm test"


def test_sync_merges_new_stack(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='a'\n", encoding="utf-8")
    state = tmp_path / "agent_memory.state.yaml"
    state.write_text(
        "stack: Python\nstack_signals:\n  - id: python\n    label: Python\n    evidence: pyproject.toml\n    first_seen: '2026-01-01'\n    last_seen: '2026-01-01'\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(STACK_DETECT), "--root", str(tmp_path), "--sync"],
        capture_output=True,
        text=True,
        cwd=SCAFFOLD,
    )
    assert proc.returncode == 0, proc.stderr
    text = state.read_text(encoding="utf-8")
    assert "node" in text or "Node.js" in text
    assert "python" in text
