# tests/test_config.py
import pytest
from pathlib import Path

from sdcoh.config import load_config, SdcohConfig, ConfigNotFoundError


def test_load_config_from_yaml(tmp_path: Path) -> None:
    yml = tmp_path / "sdcoh.yml"
    yml.write_text(
        "project:\n"
        '  name: "Test Novel"\n'
        '  alias: "test"\n'
        "scan:\n"
        "  - design/\n"
        "  - drafts/\n"
        "node_types:\n"
        "  design: { layer: 0 }\n"
        "  episode: { layer: 2 }\n"
    )
    cfg = load_config(tmp_path)
    assert cfg.project_name == "Test Novel"
    assert cfg.project_alias == "test"
    assert cfg.scan_dirs == ["design/", "drafts/"]
    assert cfg.node_types["design"]["layer"] == 0
    assert cfg.node_types["episode"]["layer"] == 2


def test_load_config_defaults(tmp_path: Path) -> None:
    yml = tmp_path / "sdcoh.yml"
    yml.write_text(
        "project:\n"
        '  name: "Minimal"\n'
    )
    cfg = load_config(tmp_path)
    assert cfg.project_alias == "minimal"
    assert "design/" in cfg.scan_dirs
    assert "drafts/" in cfg.scan_dirs
    assert cfg.openviking_enabled is False


def test_load_config_not_found(tmp_path: Path) -> None:
    with pytest.raises(ConfigNotFoundError):
        load_config(tmp_path)


def test_load_config_with_openviking(tmp_path: Path) -> None:
    yml = tmp_path / "sdcoh.yml"
    yml.write_text(
        "project:\n"
        '  name: "OV Test"\n'
        "openviking:\n"
        "  enabled: true\n"
        '  endpoint: "http://localhost:1933"\n'
        "  auto_register: true\n"
    )
    cfg = load_config(tmp_path)
    assert cfg.openviking_enabled is True
    assert cfg.openviking_endpoint == "http://localhost:1933"
    assert cfg.openviking_auto_register is True
