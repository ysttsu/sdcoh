"""Parse frontmatter from Markdown files and build dependency graph."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
from fnmatch import fnmatch

from sdcoh.config import SdcohConfig


@dataclass
class ScanResult:
    """Result of scanning a project."""

    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def save(self, root: Path) -> Path:
        """Save graph to .sdcoh/graph.json."""
        out_dir = root / ".sdcoh"
        out_dir.mkdir(exist_ok=True)
        graph_path = out_dir / "graph.json"
        graph_path.write_text(
            json.dumps(
                {
                    "version": "1.0",
                    "scanned_at": datetime.now(timezone.utc).isoformat(),
                    "nodes": self.nodes,
                    "edges": self.edges,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return graph_path


def scan_project(cfg: SdcohConfig) -> ScanResult:
    """Scan all Markdown files in configured directories and build the graph."""
    result = ScanResult()
    node_ids: set[str] = set()

    for scan_dir in cfg.scan_dirs:
        dir_path = cfg.root / scan_dir.rstrip("/")
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.rglob("*.md")):
            _process_file(md_file, cfg.root, result, node_ids)

    return result


def _expand_pattern(
    pattern: str,
    all_node_ids: set[str],
    self_id: str,
) -> list[str]:
    """Expand a glob pattern against known node IDs.

    If pattern contains no glob characters, returns [pattern] as-is.
    Otherwise returns sorted matched IDs, excluding self_id.
    """
    if not any(c in pattern for c in ("*", "?", "[")):
        return [pattern]
    return sorted(
        nid for nid in all_node_ids
        if fnmatch(nid, pattern) and nid != self_id
    )


def _process_file(
    md_file: Path,
    root: Path,
    result: ScanResult,
    node_ids: set[str],
) -> None:
    """Process a single Markdown file."""
    rel_path = str(md_file.relative_to(root))

    try:
        post = frontmatter.load(str(md_file))
    except Exception as e:
        result.warnings.append(f"{rel_path} (parse error: {e})")
        return

    sdcoh_meta = post.metadata.get("sdcoh")

    if sdcoh_meta is None:
        result.warnings.append(rel_path)
        return

    node_id = sdcoh_meta.get("id")
    if not node_id:
        result.warnings.append(rel_path)
        return

    node_type = node_id.split(":")[0] if ":" in node_id else "unknown"
    mtime = datetime.fromtimestamp(
        md_file.stat().st_mtime, tz=timezone.utc
    ).isoformat()

    if node_id not in node_ids:
        result.nodes.append(
            {
                "id": node_id,
                "type": node_type,
                "path": rel_path,
                "mtime": mtime,
            }
        )
        node_ids.add(node_id)

    for dep in sdcoh_meta.get("depends_on", []):
        result.edges.append(
            {
                "source": node_id,
                "target": dep["id"],
                "relation": dep["relation"],
                "direction": "depends_on",
            }
        )

    for upd in sdcoh_meta.get("updates", []):
        result.edges.append(
            {
                "source": node_id,
                "target": upd["id"],
                "relation": upd["relation"],
                "direction": "updates",
            }
        )
