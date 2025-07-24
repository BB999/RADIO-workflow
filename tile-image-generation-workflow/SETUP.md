# タイル画像生成ワークフロー セットアップガイド

## 概要

4枚の関連する画像を自動生成し、タイル状に配置して1枚の合成画像を作成するAI画像生成ワークフローです。

### 🎨 主要機能
- **4枚同時生成**: 統一されたテーマで4枚の画像を並列生成
- **マルチモデル対応**: 5種類のAI画像生成モデルに対応
- **柔軟なレイアウト**: 2x2、1x4、4x1の3種類のタイル配置
- **自動合成**: ImageMagickによる高品質なタイル画像組み立て
- **カスタムプロンプト**: 手動指定または自動生成

### 🖼️ 生成される成果物
- ✅ 4枚の個別高品質画像
- ✅ タイル状に配置された合成画像
- ✅ 詳細な企画書と プロンプト
- ✅ Google認証済みURL（外部アクセス用）

## ステップ1: リポジトリのセットアップ

### 1.1 リポジトリのクローン

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/kamuicode-workflow.git
cd kamuicode-workflow
```

## ディレクトリ構造

```
your-repo/
├── .github/
│   └── workflows/
│       └── create-tile-images.yml               # メインワークフロー
└── .claude/
    ├── mcp-kamuicode.json                       # MCP設定（必須）
    └── settings.json                            # Claude Code権限設定
```

### 1.2 ファイルのコピー

```bash
# ワークフローディレクトリを作成
mkdir -p .github/workflows

# タイル画像生成ワークフローをコピー
cp kamuicode-workflow/tile-image-generation-workflow/create-tile-images.yml .github/workflows/

# ファイルが正しくコピーされたか確認
ls -la .github/workflows/create-tile-images.yml
```

## ステップ2: GitHub Secretsの設定

### 2.1 必要なSecrets

| Secret名 | 説明 | 必要性 | 取得方法 |
|---------|------|--------|----------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code OAuth Token（**必須**） | 企画立案・画像生成で使用 | Claude Code認証設定 |
| `PAT_TOKEN` | GitHub Personal Access Token（**必須**） | ブランチ・プルリクエスト作成 | GitHub Settings → Developer settings |

### 2.2 CLAUDE_CODE_OAUTH_TOKENの設定

Claude Codeの認証トークンを使用します。詳細は[Claude Code公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)を参照してください。

### 2.3 PAT_TOKENの取得方法

1. GitHubにログイン
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 「Generate new token (classic)」をクリック
4. 以下の権限を選択：
   - `repo` (リポジトリへの完全アクセス)
   - `workflow` (GitHub Actionsワークフローの更新)
   - `pull_requests` (プルリクエスト作成)
5. 「Generate token」をクリック
6. 作成されたトークンをコピー

### 2.4 Secrets設定手順

**方法1: GitHub CLI（推奨）**

```bash
# カレントディレクトリがリポジトリ内の場合
gh secret set CLAUDE_CODE_OAUTH_TOKEN --app actions
gh secret set PAT_TOKEN --app actions

# 設定確認
gh secret list --app actions
```

**方法2: GitHub Web UI**

1. **GitHubリポジトリページ** → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**をクリック
3. 各Secretを追加

### 2.5 設定確認

設定完了後、以下が表示されることを確認：
- ✅ `CLAUDE_CODE_OAUTH_TOKEN` (Updated X minutes ago)
- ✅ `PAT_TOKEN` (Updated X minutes ago)

## ステップ3: Claude Code設定

### 3.1 MCP設定ファイルの配置

```bash
# Claude設定ディレクトリを作成
mkdir -p .claude

# kamuicode MCP設定ファイルを配置
# ⚠️ 実際のkamuicode設定が必要です
```

**⚠️ 重要**: `.claude/mcp-kamuicode.json`ファイルを手動で作成する必要があります。kamuicode提供者から提供される実際の設定を使用してください。

### 3.2 Claude Code権限設定

`.claude/settings.json` ファイルを作成し、必要なツールの権限を設定：

```bash
# settings.jsonファイルを作成
cat > .claude/settings.json << 'EOF'
{
  "defaultMode": "acceptEdits",
  "permissions": {
    "allow": [
      "Bash(curl:*)",
      "Bash(wget:*)",
      "Bash(sleep:*)",
      "Bash(stat:*)",
      "Bash(find:*)",
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(head:*)",
      "Bash(mkdir:*)",
      "Bash(git:checkout:*)",
      "Bash(git:config:*)",
      "Bash(git:push:*)",
      "Bash(git:add:*)",
      "Bash(git:diff:*)",
      "Bash(git:commit:*)",
      "Bash(git:pull:*)",
      "Bash(date:*)",
      "Bash(jq:*)",
      "Bash(tr:*)",
      "Bash(wc:*)",
      "Bash(echo:*)",
      "Bash(npx:*)",
      "Bash(file:*)",
      "Bash(montage:*)",
      "Bash(convert:*)",
      "mcp__t2i-google-imagen3__*",
      "mcp__t2i-fal-imagen4-ultra__*",
      "mcp__t2i-fal-imagen4-fast__*",
      "mcp__t2i-fal-flux-schnell__*",
      "mcp__t2i-fal-rundiffusion-photo-flux__*",
      "Read",
      "Write",
      "Edit"
    ]
  }
}
EOF

# 設定ファイルが作成されたか確認
cat .claude/settings.json
```

**⚠️ 重要**: この設定がないと、Claude CodeがMCPツールを使用できずワークフローが失敗します。

## ステップ4: GitHub権限設定（必要に応じて）

ワークフローが権限エラーで失敗する場合のみ、以下を確認：

**Settings** → **Actions** → **General** → **Workflow permissions**
- ✅ "Read and write permissions" を選択
- ✅ "Allow GitHub Actions to create and approve pull requests" をチェック

## 使い方

### 🎨 タイル画像生成の実行

1. **GitHub Actions**ページにアクセス
2. **Create Tile Images (4x Grid)**を選択
3. **Run workflow**をクリック
4. パラメータを入力：

#### 基本パラメータ

```
main_concept: "四季の風景"
image_model: "t2i-fal-imagen4-fast"
tile_layout: "2x2"
custom_prompts: ""
```

#### 高度な使用例

**季節をテーマにした2x2タイル:**
```
main_concept: "四季の美しい日本の風景"
image_model: "t2i-fal-imagen4-ultra"
tile_layout: "2x2"
custom_prompts: ""
```

**動物シリーズの横並び:**
```
main_concept: "可愛い動物たち"
image_model: "t2i-fal-flux-schnell"
tile_layout: "1x4"
custom_prompts: ""
```

**カスタムプロンプト指定:**
```
main_concept: "ファンタジーの世界"
image_model: "t2i-fal-rundiffusion-photo-flux"
tile_layout: "2x2"
custom_prompts: '{"1":"magical forest with glowing trees","2":"ancient castle in the clouds","3":"dragon flying over mountains","4":"wizard in mystical library"}'
```

5. **Run workflow**をクリックして実行

### 📊 処理フロー

1. **🌟 ブランチセットアップ** - 専用ブランチ作成
2. **📋 企画立案** - 4枚の画像の詳細プロンプト生成
3. **🎨 並列画像生成** - 4つのジョブで同時に画像生成
   - 画像生成エージェント 1/4
   - 画像生成エージェント 2/4  
   - 画像生成エージェント 3/4
   - 画像生成エージェント 4/4
4. **🖼️ タイル合成** - ImageMagickで4枚を1枚に統合
5. **📝 プルリクエスト作成** - 結果をレビュー用に提出

### ⏱️ 処理時間

- **標準実行時間**: 約15-25分
- **並列処理**: 4枚の画像を同時生成で時短
- **モデル別速度**:
  - `t2i-fal-flux-schnell`: 最高速（5-10分）
  - `t2i-fal-imagen4-fast`: 高速（10-15分）
  - `t2i-fal-imagen4-ultra`: 高品質（20-25分）

## 対応モデル

### 🎨 画像生成モデル

| モデル名 | 特徴 | 品質 | 速度 | 用途 |
|---------|------|------|------|------|
| `t2i-google-imagen3` | Google製高品質 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 最高品質が必要な場合 |
| `t2i-fal-imagen4-ultra` | 商用最高品質 | ⭐⭐⭐⭐⭐ | ⭐⭐ | プロフェッショナル用途 |
| `t2i-fal-imagen4-fast` | バランス型 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **推奨・汎用** |
| `t2i-fal-flux-schnell` | 超高速 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 高速プロトタイピング |
| `t2i-fal-rundiffusion-photo-flux` | 写実特化 | ⭐⭐⭐⭐ | ⭐⭐⭐ | フォトリアリスティック |

### 📐 レイアウトオプション

| レイアウト | 配置 | 用途 | 例 |
|-----------|------|------|-----|
| `2x2` | 2行2列グリッド | **汎用・推奨** | 四季、時間帯、感情表現 |
| `1x4` | 1行4列横並び | ストーリー性 | 成長過程、手順説明 |
| `4x1` | 4行1列縦並び | タイムライン | 歴史、進化、段階 |

## トラブルシューティング

### ワークフローが起動しない
- Secretsが正しく設定されているか確認
- ワークフローファイルがデフォルトブランチにあるか確認

### 画像生成が失敗する
- 全2つのAPIキーの有効性を確認  
- MCP設定ファイルの内容を確認
- Actions のログを確認

### タイル合成が失敗する
- ImageMagickのインストール状況を確認
- 4枚の個別画像が正常に生成されているか確認
- レイアウト指定が正しいか確認

### 生成された画像の品質が低い
- より高品質なモデル（imagen4-ultra等）を試す
- プロンプトをより詳細に指定
- カスタムプロンプトで細かく制御

## 🎯 活用例

### デザイン・クリエイティブ
```
main_concept: "ミニマルデザインのアイコンセット"
tile_layout: "2x2"
image_model: "t2i-fal-imagen4-ultra"
```

### 教育・説明資料
```
main_concept: "プログラミング学習の4段階"
tile_layout: "1x4"  
image_model: "t2i-fal-imagen4-fast"
```

### マーケティング素材
```
main_concept: "商品の特徴を表現する4つの画像"
tile_layout: "2x2"
image_model: "t2i-fal-rundiffusion-photo-flux"
```

### アート・表現
```
main_concept: "抽象的な感情の表現"
tile_layout: "4x1"
image_model: "t2i-google-imagen3"
```

---

**作成日**: 2025年7月24日  
**対応バージョン**: Claude Code対応  
**必要な権限**: GitHub Actions、Claude Code OAuth、kamuicode MCP