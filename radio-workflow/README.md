# AI Radio Audio Generator Workflow

音楽付きAIラジオ音声生成ワークフロー

## 🎙️ 概要

このGitHub Actionsワークフローは、**原稿と音楽の雰囲気**から完全なラジオ音声（音楽付き）を自動生成します。

### 🎯 生成フロー

1. **📝 台本作成** - 原稿から1分程度のラジオ台本を生成
2. **🎤 音声生成** - aivis-apiでカムイ日報風の音声を生成（並列）
3. **🎵 音楽生成** - Google Lyriaで背景音楽を生成（並列）
4. **🎚️ 音声合成** - FFmpegで音声と音楽を合成して完成

### 🔧 技術スタック

- **台本生成**: Claude Code SDK（原稿要約・口調調整）
- **音声生成**: aivis-api（高品質音声合成）
- **音楽生成**: Google Lyria（kamuicode MCP経由）
- **音声合成**: FFmpeg（音声・音楽ミキシング）
- **AI統合**: Claude Code SDK + kamuicode MCP

## 🚀 使用方法

### 手動実行

1. リポジトリの**Actions**タブに移動
2. **Create Radio Audio with Music**ワークフローを選択
3. **Run workflow**ボタンをクリック
4. 入力項目を設定：
   - **原稿内容**: ラジオで話したい内容のテキスト
   - **音楽の雰囲気**: 背景音楽の雰囲気（例：リラックス、エネルギッシュ、ジャズ風）
5. **Run workflow**を実行

### 入力例

#### 原稿例
```
今日はClaudeCodeの新機能について話したいと思います。
MCPサーバーとの連携がさらに強化されて、kamuicodeを使った
画像生成や音楽生成がワンクリックでできるようになりました。
特に音楽生成の品質が向上していて、Google Lyriaを使った
高品質な楽曲が簡単に作れるのが素晴らしいですね。
```

#### 音楽の雰囲気例
```
リラックス、アンビエント、夜の落ち着いた雰囲気
```

## 📁 出力構造

```
radio-audio-[タイムスタンプ]/
├── planning/
│   ├── radio-script.txt        # 生成された台本（1分程度）
│   ├── voice-style.json        # aivis-api音声スタイル設定
│   ├── music-prompt.txt        # 音楽生成用プロンプト
│   └── radio-strategy.md       # 全体的な制作戦略
├── audio/
│   └── radio-voice.wav         # 生成された音声（カムイ日報風）
├── music/
│   └── background-music.wav    # 生成された背景音楽
└── final/
    └── final-radio-audio.wav   # 最終合成音声（音楽付き）
```

## 🔧 セットアップ要件

### 必要なSecrets

```yaml
ANTHROPIC_API_KEY: # Claude API Key
AIVIS_API_KEY: # aivis-api Key（音声生成用）
PAT_TOKEN: # GitHub Personal Access Token
```

### 必要なファイル

```
.claude/
└── mcp-kamuicode.json    # kamuicode MCP設定
```

### 権限設定

```yaml
permissions:
  contents: write
  pull-requests: write
  actions: read
```

## 🎤 音声の特徴

### カムイ日報風の話し方
- 「えっと」「ですね」「ちょっと」などの口癖
- 「〜みたいな感じ」「〜っていう感じ」での説明
- 技術的な内容を親しみやすく解説
- カジュアルだが丁寧な語調

### aivis-api設定
- **モデル**: a59cb814-0083-4369-8542-f51a29e72af7（高品質音声）
- **形式**: WAV（高音質合成用）
- **話速**: 1.0-1.2（内容に応じて調整）
- **感情強度**: 音楽の雰囲気に合わせて調整

## 🎵 音楽の雰囲気例

### 🌃 リラックス系
```
"リラックス、アンビエント、夜の落ち着いた雰囲気"
"ジャズ、ピアノ、カフェのような穏やかな音楽"
```

### ⚡ エネルギッシュ系
```
"エネルギッシュ、ポップ、明るいアップテンポ"
"エレクトロニック、テクノ、活動的な雰囲気"
```

### 🎯 技術・プロフェッショナル系
```
"ミニマル、集中、作業に適した背景音楽"
"コーポレート、プレゼンテーション向け、上品"
```

## 🤖 技術的詳細

### AI Agent構成
- **台本計画Agent**: 原稿分析と台本作成
- **音声生成Agent**: aivis-api実行
- **音楽生成Agent**: Google Lyria実行（並列）
- **音声合成Agent**: FFmpeg実行と最終統合

### 並列処理最適化
- 音声生成と音楽生成: 並列実行
- 依存関係: 台本→（音声・音楽並列）→合成

### FFmpeg合成設定
- 背景音楽ボリューム: 音声の20-30%
- フェードイン・アウト: 2秒
- 高品質WAV出力
- 音声長に合わせた音楽調整

## 📊 品質管理

### 音声品質
- サンプリングレート: 44.1kHz
- 音声チャンネル: モノラル
- ビットレート: 高品質設定

### 音楽品質
- Google Lyria: 高品質音楽生成
- 音声に適したボリュームバランス
- フェード処理による自然な合成

## 🎯 使用例・活用シーン

### 📡 ポッドキャスト制作
- 技術解説番組
- 製品紹介・レビュー
- 学習コンテンツ

### 🏢 企業・プレゼンテーション
- 製品デモ音声
- 会社紹介ナレーション
- トレーニング用音声

### 🎓 教育・学習
- 技術チュートリアル
- 知識共有コンテンツ
- オンライン講座

## 📄 ライセンス

MIT License

## 👥 貢献

Issues、Pull Requests大歓迎です！

---

🎙️ **AI-generated Radio Audio Workflow** - Powered by [Claude Code SDK](https://github.com/anthropics/claude-code), [aivis-api](https://aivis-project.com) & [kamuicode MCP](https://www.kamui.ai/ja)