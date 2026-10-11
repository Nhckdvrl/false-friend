"""Ensure the paper registry and local-research backlinks remain navigable."""
from pathlib import Path
import subprocess
import sys


def test_knowledge_integrity_cli():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "scripts/check_knowledge.py"],
        cwd=root, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "paper notes" in result.stdout
