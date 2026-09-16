"""Reject publication until project identity and tagged release are finalized."""

import os
import tomllib
from pathlib import Path

project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
if os.environ.get("EXPECTED_PROJECT") != project["name"]:
    raise SystemExit("Set PYPI_PROJECT_NAME to the reviewed, final distribution name")
if project["version"] == "0.0.0.dev0":
    raise SystemExit("The local extraction version must not be published")
if os.environ.get("GITHUB_REF") != f"refs/tags/v{project['version']}":
    raise SystemExit("Release tag and package version do not match")
if not project.get("urls", {}).get("Repository"):
    raise SystemExit("Set the final public repository URL in project.urls")
