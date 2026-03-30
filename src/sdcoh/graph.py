"""DAG operations: impact analysis, cycle detection, tree display, validation."""

from __future__ import annotations

from collections import defaultdict

from sdcoh.scanner import ScanResult


def _build_reverse_adj(result: ScanResult) -> dict[str, list[dict]]:
    """Build reverse adjacency: target → list of edges where source depends on target."""
    rev: dict[str, list[dict]] = defaultdict(list)
    for edge in result.edges:
        if edge["direction"] == "depends_on":
            # source depends on target → if target changes, source is impacted
            rev[edge["target"]].append(edge)
    return rev


def _build_update_adj(result: ScanResult) -> dict[str, list[dict]]:
    """Build update adjacency: source → list of update edges."""
    adj: dict[str, list[dict]] = defaultdict(list)
    for edge in result.edges:
        if edge["direction"] == "updates":
            adj[edge["source"]].append(edge)
    return adj


def find_impact(
    result: ScanResult,
    node_id: str,
    max_depth: int = 0,
) -> list[dict]:
    """Find all nodes impacted by a change to node_id.

    Walks reverse depends_on edges (who depends on me?) and update edges.
    Returns list of dicts with 'id' and 'relation' keys.
    """
    node_ids = {n["id"] for n in result.nodes}
    if node_id not in node_ids:
        return []

    rev = _build_reverse_adj(result)
    upd = _build_update_adj(result)

    visited: set[str] = set()
    impacted: list[dict] = []

    def walk(nid: str, depth: int) -> None:
        if max_depth > 0 and depth > max_depth:
            return
        # Reverse depends_on: who depends on nid?
        for edge in rev.get(nid, []):
            src = edge["source"]
            if src not in visited:
                visited.add(src)
                impacted.append({"id": src, "relation": edge["relation"]})
                walk(src, depth + 1)
        # Update edges: what does nid trigger updates to?
        for edge in upd.get(nid, []):
            tgt = edge["target"]
            if tgt not in visited:
                visited.add(tgt)
                impacted.append({"id": tgt, "relation": edge["relation"]})
                walk(tgt, depth + 1)

    visited.add(node_id)
    walk(node_id, 1)
    return impacted


def find_cycles(result: ScanResult) -> list[list[str]]:
    """Detect cycles in depends_on edges using DFS."""
    adj: dict[str, list[str]] = defaultdict(list)
    for edge in result.edges:
        if edge["direction"] == "depends_on":
            adj[edge["source"]].append(edge["target"])

    all_ids = {n["id"] for n in result.nodes}
    visited: set[str] = set()
    on_stack: set[str] = set()
    cycles: list[list[str]] = []

    def dfs(nid: str, path: list[str]) -> None:
        visited.add(nid)
        on_stack.add(nid)
        path.append(nid)
        for neighbor in adj.get(nid, []):
            if neighbor in on_stack:
                idx = path.index(neighbor)
                cycles.append(path[idx:] + [neighbor])
            elif neighbor not in visited and neighbor in all_ids:
                dfs(neighbor, path)
        path.pop()
        on_stack.discard(nid)

    for nid in all_ids:
        if nid not in visited:
            dfs(nid, [])

    return cycles


def find_orphans(result: ScanResult) -> list[str]:
    """Find nodes that are neither referenced by depends_on nor update edges."""
    referenced: set[str] = set()
    for edge in result.edges:
        referenced.add(edge["source"])
        referenced.add(edge["target"])
    return sorted(n["id"] for n in result.nodes if n["id"] not in referenced)


def validate_references(result: ScanResult) -> list[str]:
    """Find edges that reference non-existent node IDs."""
    node_ids = {n["id"] for n in result.nodes}
    broken = []
    for edge in result.edges:
        if edge["target"] not in node_ids:
            broken.append(f'{edge["source"]} → {edge["target"]} (not found)')
        if edge["source"] not in node_ids:
            broken.append(f'{edge["source"]} (not found) → {edge["target"]}')
    return broken


def build_tree_text(result: ScanResult) -> str:
    """Build a text representation of the dependency tree."""
    # Find roots: nodes that have no depends_on edges (as source)
    has_deps: set[str] = set()
    for edge in result.edges:
        if edge["direction"] == "depends_on":
            has_deps.add(edge["source"])

    roots = sorted(n["id"] for n in result.nodes if n["id"] not in has_deps)

    # Build forward adjacency (who depends on me)
    rev = _build_reverse_adj(result)
    lines: list[str] = []

    def render(nid: str, prefix: str, is_last: bool, visited: set[str]) -> None:
        connector = "└→ " if is_last else "├→ "
        if prefix:
            lines.append(f"{prefix}{connector}{nid}")
        else:
            lines.append(nid)

        if nid in visited:
            return
        visited.add(nid)

        children = sorted({e["source"] for e in rev.get(nid, [])})
        child_prefix = prefix + ("   " if is_last else "│  ")
        for i, child in enumerate(children):
            render(child, child_prefix, i == len(children) - 1, visited)

    visited: set[str] = set()
    for root in roots:
        render(root, "", True, visited)
        if root != roots[-1]:
            lines.append("")

    return "\n".join(lines)
