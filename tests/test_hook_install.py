from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml
from brkraw.core import config as config_core


def test_hook_install_template(tmp_path: Path) -> None:
    env = os.environ.copy()
    env[config_core.ENV_CONFIG_HOME] = str(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "brkraw.cli.main",
            "hook",
            "install",
            "template",
        ],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    registry_path = tmp_path / "hooks.yaml"
    assert registry_path.exists(), "hook registry not created"

    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    hooks = registry.get("hooks", {})
    assert "brkraw-hook-template" in hooks, "template hook not registered"

    paths = config_core.paths(root=tmp_path)
    namespace = "brkraw-hook-template"
    assert (paths.rules_dir / namespace).exists(), "rules not installed"
    assert (paths.specs_dir / namespace).exists(), "specs not installed"
    assert (paths.transforms_dir / namespace).exists(), "transforms not installed"
