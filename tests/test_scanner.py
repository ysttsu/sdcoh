# tests/test_scanner.py
from pathlib import Path

from sdcoh.config import load_config
from sdcoh.scanner import scan_project, ScanResult, _expand_pattern


def test_scan_finds_all_nodes(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    ids = {n["id"] for n in result.nodes}
    assert ids == {
        "design:characters",
        "design:beat-sheet",
        "design:style",
        "episode:ep01",
        "brief:ep01",
    }


def test_scan_builds_edges(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    edges = {(e["source"], e["target"], e["relation"]) for e in result.edges}
    assert ("design:beat-sheet", "design:characters", "derives_from") in edges
    assert ("episode:ep01", "design:beat-sheet", "implements") in edges
    assert ("episode:ep01", "design:style", "constrained_by") in edges
    assert ("brief:ep01", "design:beat-sheet", "derives_from") in edges
    assert ("brief:ep01", "design:characters", "references") in edges


def test_scan_builds_update_edges(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    update_edges = [
        e for e in result.edges if e["direction"] == "updates"
    ]
    assert len(update_edges) == 1
    assert update_edges[0]["source"] == "episode:ep01"
    assert update_edges[0]["target"] == "design:characters"
    assert update_edges[0]["relation"] == "triggers_update"


def test_scan_reports_files_without_frontmatter(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    assert "design/no-frontmatter.md" in result.warnings


def test_scan_stores_mtime(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    node = next(n for n in result.nodes if n["id"] == "design:characters")
    assert "mtime" in node
    assert "path" in node


def test_scan_saves_graph_json(sample_project: Path) -> None:
    cfg = load_config(sample_project)
    result = scan_project(cfg)
    result.save(cfg.root)
    graph_path = cfg.root / ".sdcoh" / "graph.json"
    assert graph_path.exists()


def test_expand_pattern_literal_returns_as_is() -> None:
    all_ids = {"design:characters", "design:beat-sheet", "episode:ep01"}
    result = _expand_pattern("design:characters", all_ids, "episode:ep01")
    assert result == ["design:characters"]


def test_expand_pattern_glob_matches() -> None:
    all_ids = {"design:characters", "design:beat-sheet", "design:style", "episode:ep01"}
    result = _expand_pattern("design:*", all_ids, "episode:ep01")
    assert result == ["design:beat-sheet", "design:characters", "design:style"]


def test_expand_pattern_excludes_self() -> None:
    all_ids = {"design:characters", "design:beat-sheet", "design:style"}
    result = _expand_pattern("design:*", all_ids, "design:characters")
    assert result == ["design:beat-sheet", "design:style"]


def test_expand_pattern_no_match_returns_empty() -> None:
    all_ids = {"design:characters", "episode:ep01"}
    result = _expand_pattern("brief:*", all_ids, "episode:ep01")
    assert result == []


def test_scan_expands_glob_depends_on(glob_project: Path) -> None:
    cfg = load_config(glob_project)
    result = scan_project(cfg)
    deps_edges = [
        e for e in result.edges
        if e["source"] == "episode:ep01" and e["direction"] == "depends_on"
    ]
    targets = sorted(e["target"] for e in deps_edges)
    assert targets == ["design:beat-sheet", "design:characters", "design:style"]
    assert all(e["relation"] == "implements" for e in deps_edges)


def test_scan_expands_glob_updates(glob_project: Path) -> None:
    design_dir = glob_project / "design"
    (design_dir / "beat-sheet.md").write_text(
        "---\n"
        "sdcoh:\n"
        '  id: "design:beat-sheet"\n'
        "  updates:\n"
        '    - id: "episode:*"\n'
        '      relation: triggers_update\n'
        "---\n"
        "# Beat Sheet\n"
    )
    cfg = load_config(glob_project)
    result = scan_project(cfg)
    update_edges = [
        e for e in result.edges
        if e["source"] == "design:beat-sheet" and e["direction"] == "updates"
    ]
    assert len(update_edges) == 1
    assert update_edges[0]["target"] == "episode:ep01"


def test_scan_glob_no_match_warns(glob_project: Path) -> None:
    drafts = glob_project / "drafts"
    (drafts / "ep01.md").write_text(
        "---\n"
        "sdcoh:\n"
        '  id: "episode:ep01"\n'
        "  depends_on:\n"
        '    - id: "research:*"\n'
        '      relation: references\n'
        "---\n"
        "# Episode 1\n"
    )
    cfg = load_config(glob_project)
    result = scan_project(cfg)
    assert any("research:*" in w for w in result.warnings)
