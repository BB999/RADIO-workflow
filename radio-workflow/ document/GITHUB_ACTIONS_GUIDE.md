# GitHub Actions 実践ガイド - kamuicode Workflow

本プロジェクトにおけるGitHub Actionsの実践的な活用方法と実装パターン

## 📚 目次

1. [基本アーキテクチャ](#基本アーキテクチャ)
2. [実装パターン](#実装パターン)
3. [モジュール設計](#モジュール設計)
4. [エラーハンドリング](#エラーハンドリング)
5. [デバッグとトラブルシューティング](#デバッグとトラブルシューティング)
6. [ベストプラクティス](#ベストプラクティス)

## 🏗️ 基本アーキテクチャ

### ワークフローの階層構造

```
┌─────────────────────────────────────┐
│     Orchestrator Workflows          │  ← ユーザーが実行
│  (orchestrator-*.yml)               │
└──────────────┬──────────────────────┘
               │ uses: workflow_call
┌──────────────▼──────────────────────┐
│       Module Workflows              │  ← 再利用可能な機能単位
│  (module-*.yml)                     │
└──────────────┬──────────────────────┘
               │ docker run / npx
┌──────────────▼──────────────────────┐
│    External Services & SDKs         │  ← Claude Code SDK, kamuicode MCP
└─────────────────────────────────────┘
```

### ワークフロー種別と命名規則

| 種別 | プレフィックス | 役割 | 例 |
|------|---------------|------|-----|
| オーケストレータ | `orchestrator-` | 統合ワークフロー | `orchestrator-news-video-generation.yml` |
| モジュール | `module-` | 単一機能 | `module-image-generation-kc-multi-model-ccsdk.yml` |
| トリガー | `issue-` | Issue連携 | `issue-video-trigger.yml` |
| 直接実行 | `create-` | スタンドアロン | `create-music-video.yml` |

## 💻 実装パターン

### 1. ワークフロー間のデータ受け渡し

```yaml
# 親ワークフロー（orchestrator）
jobs:
  planning:
    uses: ./.github/workflows/module-planning-ccsdk.yml
    outputs:
      image-prompt: ${{ jobs.generate.outputs.image-prompt }}
  
  image-generation:
    needs: planning
    uses: ./.github/workflows/module-image-generation.yml
    with:
      image-prompt: ${{ needs.planning.outputs.image-prompt }}  # データの受け渡し
```

### 2. 条件付き実行とエラー処理

```yaml
# 前のジョブが成功した場合のみ実行
lipsync-generation:
  needs: [video-generation, audio-generation]
  if: always() && needs.video-generation.result == 'success'
  uses: ./.github/workflows/module-lipsync-generation.yml
```

### 3. 動的なブランチ作成とファイル管理

```yaml
setup-branch:
  runs-on: ubuntu-latest
  outputs:
    branch-name: ${{ steps.create-branch.outputs.branch-name }}
    folder-name: ${{ steps.create-branch.outputs.folder-name }}
  steps:
    - name: Create branch for generation
      id: create-branch
      run: |
        BRANCH_NAME="feature/ai-generated-$(date +%Y%m%d)-${{ github.run_id }}"
        FOLDER_NAME="output-$(date +%Y%m%d)-${{ github.run_id }}"
        git checkout -b $BRANCH_NAME
        echo "branch-name=$BRANCH_NAME" >> $GITHUB_OUTPUT
        echo "folder-name=$FOLDER_NAME" >> $GITHUB_OUTPUT
```

### 4. Claude Code SDK実行パターン

```yaml
# Docker方式（推奨）
- name: Run Claude Code Agent
  uses: docker://ghcr.io/anthropics/claude-code:latest
  with:
    api-key: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-config: .claude/mcp-kamuicode.json
    command: |
      タスクの詳細な指示をここに記述

# NPX方式（Node.js環境必須）
- name: Setup and Run Claude Code
  env:
    ANTHROPIC_API_KEY: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
  run: |
    npm install @anthropic-ai/claude-code
    npx @anthropic-ai/claude-code \
      --mcp .claude/mcp-kamuicode.json \
      -c "タスクの実行"
```

### 5. マルチモデル対応の実装

```yaml
# 動的モデル選択
on:
  workflow_dispatch:
    inputs:
      image-model:
        type: choice
        options:
          - t2i-google-imagen3
          - t2i-fal-imagen4-ultra
          - t2i-fal-flux-schnell
        default: t2i-fal-imagen4-fast

jobs:
  generate:
    with:
      model-type: ${{ inputs.image-model }}
```

## 🧩 モジュール設計

### モジュールの基本構造

```yaml
name: module-example
on:
  workflow_call:  # 他のワークフローから呼び出し可能
    inputs:
      # 入力パラメータ
      prompt:
        required: true
        type: string
    outputs:
      # 出力値
      result-url:
        value: ${{ jobs.process.outputs.url }}
    secrets:
      # 必要なシークレット
      api_key:
        required: true

jobs:
  process:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.generate.outputs.url }}
    steps:
      - uses: actions/checkout@v4
      - id: generate
        run: |
          # 処理実行
          echo "url=https://example.com/result" >> $GITHUB_OUTPUT
```

### モジュール間の依存関係管理

```yaml
# 並列実行可能なジョブ
audio-generation:
  needs: [planning]  # planningのみに依存
  
title-background-generation:
  needs: [planning]  # 同じくplanningのみに依存
  # → audio-generationと並列実行される

# 順次実行が必要なジョブ
subtitle-overlay:
  needs: [lipsync-generation, subtitle-analysis]  # 両方の完了が必要
```

## 🚨 エラーハンドリング

### 1. リトライ機構

```yaml
- name: Generate with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 30
    max_attempts: 3
    retry_wait_seconds: 60
    command: |
      docker run ghcr.io/anthropics/claude-code:latest \
        --mcp .claude/mcp-kamuicode.json \
        -c "生成タスク"
```

### 2. タイムアウト設定

```yaml
jobs:
  generate:
    runs-on: ubuntu-latest
    timeout-minutes: 45  # ジョブ全体のタイムアウト
    steps:
      - name: Long running task
        timeout-minutes: 30  # 個別ステップのタイムアウト
        run: |
          # 長時間処理
```

### 3. 条件付き続行

```yaml
# エラーが発生しても後続処理を実行
- name: Optional step
  continue-on-error: true
  run: |
    # 失敗してもワークフローは続行

# 特定の条件でのみ実行
- name: Cleanup on failure
  if: failure()
  run: |
    # エラー時のクリーンアップ処理
```

## 🔍 デバッグとトラブルシューティング

### デバッグ出力の追加

```yaml
- name: Debug information
  run: |
    echo "::debug::Current directory: $(pwd)"
    echo "::debug::Environment variables:"
    env | grep -E '^(GITHUB_|INPUT_)' | sort
    
    echo "::group::File structure"
    find . -type f -name "*.yml" | head -20
    echo "::endgroup::"
```

### ステップサマリーの活用

```yaml
- name: Generate summary
  run: |
    cat >> $GITHUB_STEP_SUMMARY << EOF
    ## 🎬 生成結果
    
    | 項目 | 結果 |
    |------|------|
    | 画像URL | ${{ steps.image.outputs.url }} |
    | 動画URL | ${{ steps.video.outputs.url }} |
    | 処理時間 | ${{ steps.timer.outputs.duration }} |
    EOF
```

### よくあるエラーと対処法

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `Permission denied` | GITHUB_TOKENの権限不足 | `permissions:`セクションで必要な権限を追加 |
| `Secret not found` | Secretsの未設定 | リポジトリ設定でSecretsを確認・追加 |
| `Workflow not found` | パスの誤り | `.github/workflows/`配下の正しいパスを指定 |
| `Output not available` | 出力の未定義 | `outputs:`セクションで出力を定義 |

## 📝 ベストプラクティス

### 1. ワークフロー設計の原則

- **単一責任**: 各モジュールは1つの明確な機能を持つ
- **疎結合**: モジュール間の依存を最小限に
- **再利用性**: 汎用的なパラメータ設計
- **冪等性**: 何度実行しても同じ結果

### 2. セキュリティ

```yaml
# Secretsは環境変数経由で使用
env:
  API_KEY: ${{ secrets.API_KEY }}  # ✅ 推奨

# ログに出力しない
- run: |
    echo "::add-mask::${{ secrets.API_KEY }}"  # マスキング
```

### 3. パフォーマンス最適化

```yaml
# アーティファクトのキャッシュ
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

# 並列実行の活用
strategy:
  matrix:
    model: [imagen4-fast, flux-schnell]
  max-parallel: 2
```

### 4. ドキュメント化

```yaml
# ワークフロー内のコメント
- name: Generate image # 画像生成ステップ
  # このステップではkamuicode MCPを使用して
  # 指定されたプロンプトから画像を生成します
  uses: docker://ghcr.io/anthropics/claude-code:latest
```

### 5. 監視とログ

```yaml
# 実行時間の記録
- name: Start timer
  id: timer
  run: echo "start=$(date +%s)" >> $GITHUB_OUTPUT

- name: Calculate duration
  run: |
    duration=$(($(date +%s) - ${{ steps.timer.outputs.start }}))
    echo "Processing took ${duration} seconds"
```

## 🔗 関連リソース

- [GitHub Actions公式ドキュメント](https://docs.github.com/ja/actions)
- [Claude Code SDK](https://docs.anthropic.com/en/docs/claude-code)
- [プロジェクトREADME](./README.md)
- [モジュールワークフロー詳細](./module-workflow/README.md)

---

このガイドは実際のワークフロー実装から抽出されたパターンとベストプラクティスに基づいています。継続的に更新され、新しいパターンが追加されます。

🤖 **Powered by GitHub Actions & Claude Code SDK**