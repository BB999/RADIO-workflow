# ニュース動画生成ワークフロー セットアップガイド

## 概要

AI-Powered News Video Generation Workflowのセットアップ手順です。このワークフローを使用すると、ニュースコンテンツから**プロフェッショナルなニュース動画**を完全自動生成できます。

### 🎥 生成される成果物
- 📺 高品質AIアンカー画像
- 🎵 プロ品質ナレーション音声
- 👄 リップシンク同期動画
- 📝 多言語字幕（タイミング最適化）
- 🎬 カスタムタイトルフレーム
- 📰 完全統合された最終ニュース動画

## ステップ1: リポジトリのクローンとセットアップ

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
│       ├── orchestrator-news-video-generation.yml      # メインオーケストレータ
│       ├── module-setup-branch.yml                     # ブランチセットアップ
│       ├── module-news-planning-ccsdk.yml              # ニュース企画立案
│       ├── module-image-generation-kc-multi-model-ccsdk.yml  # 画像生成
│       ├── module-video-generation-kc-multi-model-ccsdk.yml  # 動画生成
│       ├── module-audio-generation-kc-multi-model-ccsdk.yml  # 音声生成
│       ├── module-lipsync-generation-kc-multi-model-ccsdk.yml # リップシンク
│       ├── module-lipsync-video-analysis-gca.yml       # リップシンク解析
│       ├── module-subtitle-overlay-ffmpeg-ccsdk.yml    # 字幕オーバーレイ
│       ├── module-banner-text-overlay-kc-i2i-fal-flux-kontext-max-ccsdk.yml # タイトル作成
│       ├── module-video-title-frame-ffmpeg-ccsdk.yml   # タイトルフレーム統合
│       ├── module-create-pr.yml                        # プルリクエスト作成
│       ├── module-create-summary.yml                   # サマリー作成
│       └── kamuicode/
│           └── kamuicode-usage.md                      # マルチモデル設定（必須）
└── .claude/
    ├── mcp-kamuicode.json                              # MCP設定
    └── settings.json                                   # Claude Code権限設定
```

### 1.2 ファイルのコピー

```bash
# ワークフローディレクトリを作成
mkdir -p .github/workflows

# 必要なワークフローファイルをコピー
cp kamuicode-workflow/module-workflow/orchestrator-news-video-generation.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-setup-branch.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-news-planning-ccsdk.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-image-generation-kc-multi-model-ccsdk.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-video-generation-kc-multi-model-ccsdk.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-audio-generation-kc-multi-model-ccsdk.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-lipsync-generation-kc-multi-model-ccsdk.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-lipsync-video-analysis-gca.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-subtitle-overlay-ffmpeg-ccsdk.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-banner-text-overlay-kc-i2i-fal-flux-kontext-max-ccsdk.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-video-title-frame-ffmpeg-ccsdk.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-create-pr.yml .github/workflows/
cp kamuicode-workflow/module-workflow/module-create-summary.yml .github/workflows/

# kamuicode設定ファイルをコピー（マルチモデル機能で必須）
mkdir -p .github/workflows/kamuicode
cp kamuicode-workflow/module-workflow/kamuicode/kamuicode-usage.md .github/workflows/kamuicode/

# ファイルが正しくコピーされたか確認
ls -la .github/workflows/
ls -la .github/workflows/kamuicode/
```

## ステップ2: GitHub Secretsの設定

### 2.1 必要なSecrets

| Secret名 | 説明 | 必要性 | 取得方法 |
|---------|------|--------|----------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code OAuth Token（**必須**） | 全モジュールで使用 | Claude Code認証設定 |
| `PAT_TOKEN` | GitHub Personal Access Token（**必須**） | プルリクエスト作成で使用 | GitHub Settings → Developer settings |
| `GEMINI_API_KEY` | Gemini API Key（**必須**） | リップシンク解析で使用 | [Google AI Studio](https://aistudio.google.com/) |

**⚠️ 重要**: ニュース動画生成では全3つのAPIキーが必須です。

### 2.2 CLAUDE_CODE_OAUTH_TOKENの設定

Claude Codeの認証トークンを使用します。詳細は[Claude Code公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)を参照してください。

### 2.3 PAT_TOKENの取得方法

1. GitHubにログイン
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 「Generate new token (classic)」をクリック
4. 以下の権限を選択：
   - `repo` (リポジトリへの完全アクセス)
   - `workflow` (GitHub Actionsワークフローの更新)
5. 「Generate token」をクリック
6. 作成されたトークンをコピー（⚠️この画面でしか表示されません）

### 2.4 GEMINI_API_KEYの取得方法

1. [Google AI Studio](https://aistudio.google.com/)にアクセス
2. Googleアカウントでログイン
3. 左側メニューの「Get API key」をクリック
4. 「Create API key」をクリック
5. 作成されたAPIキーをコピー

### 2.5 Secrets設定手順

**方法1: GitHub CLI（推奨・簡単）**

```bash
# カレントディレクトリがリポジトリ内の場合
gh secret set CLAUDE_CODE_OAUTH_TOKEN --app actions
gh secret set PAT_TOKEN --app actions
gh secret set GEMINI_API_KEY --app actions

# 設定確認
gh secret list --app actions
```

**方法2: GitHub Web UI**

1. **GitHubリポジトリページ**にアクセス
2. **Settings**タブをクリック
3. 左サイドバーの**Secrets and variables** → **Actions**をクリック
4. **New repository secret**をクリック
5. 各Secretを順番に追加

### 2.6 設定確認

設定完了後、Secretsページに以下が表示されることを確認：
- ✅ `CLAUDE_CODE_OAUTH_TOKEN` (Updated X minutes ago)
- ✅ `PAT_TOKEN` (Updated X minutes ago)
- ✅ `GEMINI_API_KEY` (Updated X minutes ago)

## ステップ3: Claude Code設定の準備

### 3.1 MCP設定ファイルの配置

```bash
# Claude設定ディレクトリを作成
mkdir -p .claude

# kamuicode MCP設定ファイルを配置
# ⚠️ 実際のkamuicode設定が必要です
```

**⚠️ 重要**: `.claude/mcp-kamuicode.json`ファイルを手動で作成する必要があります。具体的な設定内容は、kamuicode提供者から提供される実際の設定に従ってください。

### 3.2 Claude Code権限設定（重要）

`.claude/settings.json` ファイルを作成し、ニュース動画生成で使用するツールの権限を設定：

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
      "Bash(open:*)",
      "Bash(ffmpeg:*)",
      "mcp__t2i-google-imagen3__*",
      "mcp__t2i-fal-imagen4-ultra__*",
      "mcp__t2i-fal-imagen4-fast__*",
      "mcp__t2i-fal-flux-schnell__*",
      "mcp__t2i-fal-rundiffusion-photo-flux__*",
      "mcp__t2v-fal-veo3-fast__*",
      "mcp__i2v-fal-hailuo-02-pro__*",
      "mcp__r2v-fal-vidu-q1__*",
      "mcp__t2s-fal-minimax-speech-02-turbo__*",
      "mcp__v2v-fal-creatify-lipsync__*",
      "mcp__i2i-fal-flux-kontext-max__*"
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

### 🆕 ニュース動画生成の実行

1. **GitHub Actions**ページにアクセス
2. **orchestrator-news-video-generation**を選択
3. **Run workflow**をクリック
4. パラメータを入力：

```
concept: "最新技術ニュース"
news-content: "AIの最新動向について報告します..."
target-language: "japanese"
image-model: "t2i-fal-imagen4-fast"
video-model: "i2v-fal-hailuo-02-pro"
audio-model: "t2s-fal-minimax-speech-02-turbo"
lipsync-model: "v2v-fal-creatify-lipsync"
```

5. **Run workflow**をクリックして実行

### 📊 処理フロー

1. **🌟 ニュース企画立案** - コンセプトから詳細な企画を生成
2. **🎨 AIアンカー画像生成** - プロフェッショナルなアナウンサー画像
3. **🎬 ベース動画生成** - 画像からリアルな動画を生成
4. **🎵 音声ナレーション生成** - 高品質な音声合成
5. **🎬 タイトルフレーム作成** - カスタムタイトル画像
6. **👄 リップシンク統合** - 音声と動画の完全同期
7. **🔍 字幕タイミング解析** - Gemini Visionによる高精度解析
8. **📝 字幕オーバーレイ** - 最適化されたタイミングで字幕追加
9. **🎭 タイトルフレーム統合** - 最終動画にタイトルを追加
10. **📰 完成動画とプルリクエスト作成**

### ⏱️ 処理時間

- **標準実行時間**: 約20-30分
- **並列処理**: 画像生成とタイトル作成を同時実行
- **最適化**: マルチモデル対応で処理速度向上

## トラブルシューティング

### ワークフローが起動しない
- Secretsが正しく設定されているか確認
- ワークフローファイルがデフォルトブランチにあるか確認
- `kamuicode-usage.md`ファイルが配置されているか確認

### 動画生成が失敗する
- 全3つのAPIキーの有効性を確認
- MCP設定ファイルの内容を確認
- Actions のログを確認

### リップシンク処理が失敗する
- Gemini API Keyが正しく設定されているか確認
- ベース動画の品質を確認（撮影ガイドライン参照）

### 字幕タイミングがずれる
- リップシンク解析の結果を確認
- 音声の品質と明瞭さを確認

## 📖 参考資料

- **撮影ガイドライン**: `news_video_creation_workflow.md`を参照
- **Claude Code公式ドキュメント**: https://docs.anthropic.com/en/docs/claude-code
- **kamuicode MCP設定**: kamuicode提供者に問い合わせ

## 🎯 活用例

### 企業ニュース配信
```
concept: "四半期業績発表"
news-content: "当社の第3四半期の業績について..."
target-language: "japanese"
```

### 技術解説動画
```
concept: "AI技術解説"
news-content: "最新のAI技術動向について詳しく解説..."
target-language: "japanese"
```

### 多言語ニュース
```
concept: "グローバルニュース"
news-content: "Latest developments in AI technology..."
target-language: "english"
```

---

**作成日**: 2025年7月24日  
**対応バージョン**: v0.3.0以降  
**必要な権限**: GitHub Actions、Claude Code、Gemini API