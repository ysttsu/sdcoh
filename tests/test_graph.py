# tests/test_graph.py
from pathlib import Path

from sdcoh.config import load_config
from sdcoh.scanner import scan_project
from sdcoh.graph import (
    find_impact,
    find_cycles,
    find_orphans,
    build_tree_text,
    validate_references,
)


def test_find_impact_direct(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    impacted = find_impact(result, "design:characters")
    ids = {i["id"] for i in impacted}
    assert "design:beat-sheet" in ids
    assert "brief:ep01" in ids


def test_find_impact_transitive(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    impacted = find_impact(result, "design:characters")
    ids = {i["id"] for i in impacted}
    # characters → beat-sheet → ep01 (transitive)
    assert "episode:ep01" in ids
    # characters → beat-sheet → brief:ep01 (transitive)
    assert "brief:ep01" in ids


def test_find_impact_with_depth_limit(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    impacted = find_impact(result, "design:characters", max_depth=1)
    ids = {i["id"] for i in impacted}
    assert "design:beat-sheet" in ids
    assert "brief:ep01" in ids
    # ep01 depends on beat-sheet (depth 2), should NOT be included
    assert "episode:ep01" not in ids


def test_find_impact_includes_update_targets(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    impacted = find_impact(result, "episode:ep01")
    ids = {i["id"] for i in impacted}
    assert "design:characters" in ids  # via updates/triggers_update


def test_find_impact_unknown_node(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    impacted = find_impact(result, "design:nonexistent")
    assert impacted == []


def test_find_cycles_none(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    cycles = find_cycles(result)
    assert cycles == []


def test_find_orphans(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    orphans = find_orphans(result)
    # style has no incoming depends_on edges (only outgoing from ep01)
    # but ep01 depends on style, so style is referenced
    # characters has no depends_on → it's a root, not orphan
    # All nodes are connected in this fixture
    assert orphans == []


def test_validate_references(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    broken = validate_references(result)
    assert broken == []


def test_build_tree_text(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    text = build_tree_text(result)
    assert "design:characters" in text
    assert "design:beat-sheet" in text
