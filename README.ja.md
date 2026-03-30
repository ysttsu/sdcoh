# sdcoh — Story Design Coherence

[![PyPI](https://img.shields.io/pypi/v/sdcoh?style=flat-square&color=blue&v=1)](https://pypi.org/project/sdcoh/)
[![Python](https://img.shields.io/pypi/pyversions/sdcoh?style=flat-square&v=1)](https://pypi.org/project/sdcoh/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/ysttsu/sdcoh?style=flat-square)](https://github.com/ysttsu/sdcoh/stargazers)

[English README](README.md)

**小説の設計書間に依存グラフを張り、変更の波及を可視化するCLIツール。**

AIで小説を書くと、設計書がどんどん増える。キャラシート、ビートシート、伏線台帳、文体定義、ブリーフ、原稿。1つ変えたら5つ更新が必要。1つ忘れたら、矛盾が生まれる。

sdcohはこの依存関係を明示的に管理する。

## 課題

```
キャラシートを更新した…
  → でもビートシートの更新を忘れた
  → するとブリーフが古い情報で作られる
  → するとAIが間違った設定で原稿を書く
  → するとなぜ原稿が微妙なのか探すのに1時間かかる
```

## 解決

```bash
$ sdcoh status

⚠️ 更新が必要（3件）:
  design:continuity      最終更新 3/15 ← episode:ep07 更新 3/28
  design:expression-log  最終更新 3/10 ← episode:ep05 更新 3/27
  brief:ep08             最終更新 3/13 ← design:beat-sheet 更新 3/25

✅ 整合（12件）
```

## インストール

```bash
pip install sdcoh
```

OpenViking連携（オプション）:
```bash
pip install sdcoh[openviking]
```

## クイックスタート

### 1. プロジェクトの初期化

```bash
cd your-novel-project/
sdcoh init --name "私の小説" --alias my-novel
```

`sdcoh.yml` と `.sdcoh/` ディレクトリが作成される。

### 2. 設計書にフロントマターを追加

各Markdownファイルの先頭にYAMLフロントマターで依存関係を宣言する:

```yaml
---
sdcoh:
  id: "design:beat-sheet"
  depends_on:
    - id: "design:characters"
      relation: derives_from
---

# ビートシート
...
```

### 3. スキャンしてチェック

```bash
sdcoh scan        # 依存グラフを構築
sdcoh graph       # グラフを可視化
sdcoh validate    # 壊れた参照をチェック
sdcoh status      # 古い下流ドキュメントを検出
```

### 4. 編集前に影響範囲を確認

```bash
$ sdcoh impact design/characters.md

影響先（4件）:
  🟡 design:beat-sheet          ← derives_from
  🟡 design:foreshadowing       ← references
  🟡 brief:ep02                 ← references
  🟡 episode:ep01               ← implements
```

## プロジェクト設定（sdcoh.yml）

```yaml
project:
  name: "私の小説"
  alias: "my-novel"

# スキャン対象ディレクトリ
scan:
  - design/
  - drafts/
  - briefs/
  - reviews/
  - research/
  - docs/

# ノード種別（layerが小さいほど上流）
node_types:
  research: { layer: -1 }  # 最上流
  design:   { layer: 0 }
  brief:    { layer: 1 }
  episode:  { layer: 2 }
  review:   { layer: 3 }   # 最下流

# OpenViking連携（オプション）
openviking:
  enabled: false
  endpoint: "http://localhost:1933"
  auto_register: true
```

## デフォルトのディレクトリ構成

```
novel-project/
├── sdcoh.yml        # プロジェクト設定
├── design/          # 設計書（キャラシート、ビートシート、文体定義等）
├── drafts/          # 原稿
├── briefs/          # 執筆ブリーフ（AI Agent向け）
├── reviews/         # レビュー結果
├── research/        # リサーチ資料
└── docs/            # ワークフロー文書
```

## フロントマター仕様

### フィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `id` | Yes | ノードID。`{種別}:{名前}` 形式 |
| `depends_on` | No | 上流依存。相手が変わったら自分に影響がある |
| `updates` | No | 下流更新。自分が変わったら相手の更新が必要 |

### 依存関係の種類（relation）

| relation | 意味 | 例 |
|----------|------|-----|
| `derives_from` | この設計書から導出した | ビートシート ← キャラシート |
| `implements` | この設計を原稿で実装した | 原稿 ← ビートシート |
| `constrained_by` | このルールに従う | 原稿 ← 文体定義 |
| `references` | 参照している | ブリーフ ← 伏線台帳 |
| `extracts_from` | ここから抽出した | 表現ログ ← 原稿 |
| `triggers_update` | 変更されたら更新が必要 | Continuity ← 原稿 |

### 双方向依存

一部の関係は双方向。`depends_on`（上流）と `updates`（下流）を組み合わせて表現する:

```yaml
# 原稿から表現ログへの抽出
# drafts/ep01.md
sdcoh:
  id: "episode:ep01"
  updates:
    - id: "design:expression-log"
      relation: extracts_from

# 表現ログはブリーフが参照する（重複回避）
# design/expression-log.md
sdcoh:
  id: "design:expression-log"
  depends_on:
    - id: "episode:ep01"
      relation: extracts_from
```

## CLIリファレンス

| コマンド | 説明 |
|---------|------|
| `sdcoh init` | プロジェクト初期化（`sdcoh.yml` + `.sdcoh/`） |
| `sdcoh scan` | フロントマター解析 → 依存グラフ構築 |
| `sdcoh impact <path>` | 指定ファイルの変更が何に影響するか |
| `sdcoh graph` | 依存ツリーを表示 |
| `sdcoh validate` | 壊れた参照・循環依存・孤立ノードを検出 |
| `sdcoh status` | 古い下流ドキュメントを検出 |

### オプション

```
sdcoh scan --quiet          # 最小出力（hook用）
sdcoh scan --warn           # フロントマターなしファイルを一覧表示
sdcoh impact <path> --depth N  # 走査深度を制限
sdcoh status --warn-only    # 警告がある場合のみ出力
sdcoh status --json         # JSON形式で出力
```

## Claude Code連携

### プラグインとしてインストール

```bash
/plugin marketplace add ysttsu/sdcoh
/plugin install sdcoh@sdcoh
```

### スキル

| スキル | トリガー | 動作 |
|--------|---------|------|
| `/sdcoh-scan` | 「スキャン」「グラフ更新」 | `sdcoh scan` + `sdcoh validate` |
| `/sdcoh-impact` | 「影響は？」「何に響く？」 | 直近の編集ファイルに `sdcoh impact` |
| `/sdcoh-status` | 「更新漏れ」「整合性チェック」 | `sdcoh status` |

### PostToolUse Hook（編集時に自動スキャン）

`.claude/settings.json` に追加:

```jsonc
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "if": "Write(*/design/*)|Edit(*/design/*)",
      "hooks": [{
        "type": "command",
        "command": "sdcoh scan --quiet && sdcoh status --warn-only",
        "timeout": 10
      }]
    }]
  }
}
```

## 背景

このツールは[CoDD（Coherence-Driven Development）](https://zenn.dev/shio_shoppaize/articles/shogun-codd-coherence)にインスピレーションを受けている。CoDDはソフトウェアの設計書間の整合性を管理するツールだが、sdcohはその思想を**小説執筆ワークフロー**に適用したもの。

AI共創で長編小説を書くと、設計書は20〜30本以上になる。著者が「ディレクター」としてAIエージェントに執筆を委譲するワークフローでは、設計書の整合性が作品の品質を直接左右する。sdcohは設計変更時にすべての下流ドキュメントにフラグを立て、長編小説につきまとう微妙な矛盾を防ぐ。

## ライセンス

MIT
