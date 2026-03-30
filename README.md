# sdcoh — Story Design Coherence

Manage dependency graphs between story design documents. Detect change impact and stale downstream files.

## Install

```bash
pip install sdcoh
```

## Quick Start

```bash
cd your-novel-project/
sdcoh init --name "My Novel"
# Add sdcoh frontmatter to your design docs
sdcoh scan
sdcoh status
```

## Claude Code Integration

```bash
/plugin marketplace add ysttsu/sdcoh
/plugin install sdcoh@sdcoh
```

## Documentation

See [design spec](docs/design.md) for full details.
