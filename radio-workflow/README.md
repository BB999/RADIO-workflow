# AI Radio Audio Generator Workflow

音楽付きAIラジオ音声生成ワークフロー

## 🎙️ 概要

このGitHub Actionsワークフローは、**原稿と音楽の雰囲気**から完全なラジオ音声（音楽付き）を**2つの異なるバージョン**で自動生成します。

### 🎯 生成フロー

1. **📝 台本作成** - 原稿から2種類のアプローチで台本を生成（A：カジュアル / B：プロフェッショナル）
2. **🎤 音声生成** - aivis-apiでカムイ日報風の音声を2バージョン生成（並列）
3. **🎵 音楽生成** - Google Lyriaで背景音楽を2バージョン生成（並列）
4. **🎚️ 音声合成** - FFmpegで音声と音楽を合成して2つの完成版を出力

### 🔄 2バージョンシステム

- **バージョンA（カジュアル）**: 親しみやすい口調、リラックスした音楽、背景音楽60%
- **バージョンB（プロフェッショナル）**: 技術的表現重視、集中できる音楽、背景音楽60%

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
│   ├── version-a/              # バージョンA計画ファイル
│   │   ├── radio-script.txt        # 台本（カジュアル）
│   │   ├── voice-style.json        # 音声スタイル設定
│   │   ├── music-prompt.txt        # 音楽生成プロンプト
│   │   └── radio-strategy.md       # 制作戦略
│   └── version-b/              # バージョンB計画ファイル
│       ├── radio-script.txt        # 台本（プロフェッショナル）
│       ├── voice-style.json        # 音声スタイル設定
│       ├── music-prompt.txt        # 音楽生成プロンプト
│       └── radio-strategy.md       # 制作戦略
├── audio/
│   ├── version-a/
│   │   └── radio-voice.wav         # 音声A（カジュアル口調）
│   └── version-b/
│       └── radio-voice.wav         # 音声B（プロフェッショナル口調）
├── music/
│   ├── version-a/
│   │   └── background-music.wav    # 音楽A（親しみやすい）
│   └── version-b/
│       └── background-music.wav    # 音楽B（技術的・集中向け）
└── final/
    ├── version-a/
    │   └── final-radio-audio.wav   # 最終合成音声A（音楽60%）
    └── version-b/
        └── final-radio-audio.wav   # 最終合成音声B（音楽20%）
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

### バージョンA（カジュアル）
- **話し方**: 「えっと」「ですね」「ちょっと」を多用、親しみやすい口調
- **特徴**: 「〜みたいな感じ」「〜っていう感じ」での説明重視
- **aivis-api設定**: 話速1.0、感情強度0.5（標準的な表現）

### バージョンB（プロフェッショナル）
- **話し方**: 技術的表現重視、詳細な説明アプローチ
- **特徴**: 専門用語の丁寧な解説、効率性・正確性重視
- **aivis-api設定**: 話速1.2、感情強度0.3（控えめな表現）

### 共通設定
- **モデル**: a59cb814-0083-4369-8542-f51a29e72af7（高品質音声）
- **形式**: WAV（高音質合成用）

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
- **台本計画Agent**: 原稿分析と2バージョンの台本作成（A：カジュアル / B：プロフェッショナル）
- **音声生成AgentA**: aivis-api実行（カジュアル口調）
- **音声生成AgentB**: aivis-api実行（プロフェッショナル口調）
- **音楽生成AgentA**: Google Lyria実行（親しみやすい音楽）
- **音楽生成AgentB**: Google Lyria実行（技術的・集中向け音楽）
- **音声合成AgentA**: FFmpeg実行（音楽60%ボリューム）
- **音声合成AgentB**: FFmpeg実行（音楽20%ボリューム）

### 並列処理最適化
- 音声生成と音楽生成: 並列実行
- 依存関係: 台本→（音声・音楽並列）→合成

### FFmpeg合成設定

#### バージョンA（カジュアル）
- 背景音楽ボリューム: 音声の60%（音楽を楽しむ）
- フェードイン・アウト: 2秒（柔らかい印象）
- 高品質WAV出力
- 音声長に合わせた音楽調整

#### バージョンB（プロフェッショナル）
- 背景音楽ボリューム: 音声の60%（プロフェッショナルでも音楽を楽しむ）
- フェードイン・アウト: 1.5秒（精密な印象）
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