# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.1] - 2026-03-31

### Added

- **Glob pattern support in `depends_on` and `updates`** — Use fnmatch-style patterns like `episode:*` or `design:voice-*` to declare dependencies on multiple nodes at once. Patterns are expanded at scan time; `graph.json` contains only concrete edges, so downstream tools require no changes.
- New `_expand_pattern()` function using Python's `fnmatch` (stdlib, no new dependencies).
- Warning when a glob pattern matches zero nodes, helping catch typos early.

### Changed

- Scanner refactored from 1-pass to 2-pass architecture: Pass 1 collects all node IDs, Pass 2 builds edges with pattern expansion. This is necessary because glob patterns need the full set of node IDs to resolve against.
- Internal functions reorganized: `_process_file()` replaced by `_parse_frontmatter()` and `_build_edges()` for clearer separation of concerns.

## [0.1.0] - 2026-03-30

Initial release.

### Added

- `sdcoh.yml` configuration with scan directories and node types.
- Frontmatter-based dependency declarations (`depends_on`, `updates`) with 6 relation types.
- CLI commands: `init`, `scan`, `impact`, `graph`, `validate`, `status`.
- Graph operations: impact analysis, cycle detection, orphan detection, tree display, reference validation.
- Status checker: detect stale downstream documents via mtime comparison.
- OpenViking integration: auto-register documents and semantic search.
- Claude Code skills for `sdcoh-scan`, `sdcoh-impact`, `sdcoh-status`.
