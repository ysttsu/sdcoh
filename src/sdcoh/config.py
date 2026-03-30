"""Load and validate sdcoh.yml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


class ConfigNotFoundError(FileNotFoundError):
    """Raised when sdcoh.yml is not found."""


_DEFAULT_SCAN_DIRS = [
    "design/",
    "drafts/",
    "briefs/",
    "reviews/",
    "research/",
    "docs/",
]

_DEFAULT_NODE_TYPES = {
    "research": {"layer": -1},
    "design": {"layer": 0},
    "brief": {"layer": 1},
    "episode": {"layer": 2},
    "review": {"layer": 3},
}


@dataclass
class SdcohConfig:
    """Parsed sdcoh.yml configuration."""

    root: Path
    project_name: str
    project_alias: str
    scan_dirs: list[str] = field(default_factory=lambda: list(_DEFAULT_SCAN_DIRS))
    node_types: dict[str, dict] = field(default_factory=lambda: dict(_DEFAULT_NODE_TYPES))
    openviking_enabled: bool = False
    openviking_endpoint: str = "http://localhost:1933"
    openviking_auto_register: bool = False


def load_config(root: Path) -> SdcohConfig:
    """Load sdcoh.yml from the given directory."""
    yml_path = root / "sdcoh.yml"
    if not yml_path.exists():
        raise ConfigNotFoundError(f"sdcoh.yml not found in {root}")

    data = yaml.safe_load(yml_path.read_text(encoding="utf-8")) or {}
    project = data.get("project", {})
    name = project.get("name", "Untitled")
    alias = project.get("alias", name.lower().replace(" ", "-"))

    ov = data.get("openviking", {})

    return SdcohConfig(
        root=root,
        project_name=name,
        project_alias=alias,
        scan_dirs=data.get("scan", list(_DEFAULT_SCAN_DIRS)),
        node_types=data.get("node_types", dict(_DEFAULT_NODE_TYPES)),
        openviking_enabled=ov.get("enabled", False),
        openviking_endpoint=ov.get("endpoint", "http://localhost:1933"),
        openviking_auto_register=ov.get("auto_register", False),
    )
