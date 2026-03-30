"""Optional OpenViking integration for auto-registration and semantic search."""

from __future__ import annotations

from pathlib import Path

from sdcoh.config import SdcohConfig
from sdcoh.scanner import ScanResult


def auto_register(cfg: SdcohConfig, result: ScanResult, prev_graph_path: Path | None = None) -> list[str]:
    """Register changed nodes with OpenViking via HTTP API.

    Returns list of registered node paths.
    """
    if not cfg.openviking_enabled or not cfg.openviking_auto_register:
        return []

    try:
        import httpx
    except ImportError:
        return []

    registered: list[str] = []
    endpoint = cfg.openviking_endpoint.rstrip("/")

    for node in result.nodes:
        file_path = cfg.root / node["path"]
        if not file_path.exists():
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
            resp = httpx.post(
                f"{endpoint}/api/add",
                json={"path": node["path"], "content": content},
                timeout=10.0,
            )
            if resp.status_code == 200:
                registered.append(node["path"])
        except Exception:
            continue

    return registered


def semantic_search(cfg: SdcohConfig, query: str, limit: int = 5) -> list[dict]:
    """Search OpenViking for semantically related documents.

    Returns list of dicts with 'path' and 'score' keys.
    """
    if not cfg.openviking_enabled:
        return []

    try:
        import httpx
    except ImportError:
        return []

    endpoint = cfg.openviking_endpoint.rstrip("/")
    try:
        resp = httpx.post(
            f"{endpoint}/api/find",
            json={"query": query, "limit": limit},
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception:
        pass

    return []
