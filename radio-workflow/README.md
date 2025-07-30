# ラジオ局ワークフローシステム

AI技術を活用して、台本から完全なラジオ番組を自動生成するGitHub Actionsワークフローです。

## 概要

このワークフローは、ユーザーが提供する台本を基に、以下のプロセスを自動化します：

1. **台本分析**: 台本を「オープニング」「メイン」「エンディング」の3セクションに分割
2. **音声生成**: Aivis Cloud APIを使用して各セクションの音声を生成
3. **BGM生成**: MCPツールを使用して各セクションに適したBGMを生成
4. **音声合成**: ffmpegで音声とBGMを結合し、最終的なラジオ番組を作成

## 使用方法

### 1. 必要な設定

#### APIキーの設定
GitHub リポジトリの Settings → Secrets and variables → Actions で以下のシークレットを設定：

- `CLAUDE_CODE_OAUTH_TOKEN`: Claude APIキー（ANTHROPIC_API_KEYの代替として使用）
- `AIVIS_API_KEY`: Aivis Cloud APIキー（[ダッシュボード](https://api.aivis-project.com/dashboard)から取得）
- `PAT_TOKEN`: （オプション）GitHub Personal Access Token

#### MCPツールの設定
`.claude/mcp-kamuicode.json` にBGM生成用のMCPツール設定が必要です。

### 2. ワークフローの実行

1. GitHub リポジトリの Actions タブに移動
2. "Create Radio from Script" ワークフローを選択
3. "Run workflow" をクリック
4. 台本を入力して実行

### 3. 入力例

```
こんにちは、リスナーの皆さん！今日は AI技術の最新動向についてお話しします。

最近のAI技術の進歩は目覚ましく、特に音声合成技術は人間と区別がつかないレベルに達しています。
今日のゲストは、AI研究の第一人者である田中博士です。

それでは、田中博士、よろしくお願いします。
「こんにちは、皆さん。今日はAIの未来についてお話しできることを楽しみにしています。」

まず、最近のAI技術の中で特に注目されている分野について教えてください。
「はい、特に注目されているのは、自然言語処理と音声合成の分野ですね。」

なるほど、興味深いですね。具体的にはどのような応用が考えられますか？
「例えば、このようなラジオ番組も、将来的には完全にAIが制作できるようになるでしょう。」

それは驚きですね！リスナーの皆さん、いかがでしたか？
今日はAI技術の最新動向について、田中博士にお話を伺いました。

次回もお楽しみに！さようなら！
```

## 出力構造

生成されるファイルは以下の構造で保存されます：

```
radio-YYYYMMDD-{run_id}/
├── analysis/
│   ├── opening-script.txt      # オープニング台本
│   ├── main-script.txt          # メイン台本
│   ├── ending-script.txt        # エンディング台本
│   ├── script-analysis.md       # 分析レポート
│   └── script-structure.json    # 構成情報
├── voice/
│   ├── opening-voice.mp3        # オープニング音声
│   ├── main-voice.mp3           # メイン音声
│   ├── ending-voice.mp3         # エンディング音声
│   └── voice-durations.json     # 音声長情報
├── bgm/
│   ├── opening-bgm.mp3          # オープニングBGM
│   ├── main-bgm.mp3             # メインBGM
│   └── ending-bgm.mp3           # エンディングBGM
└── final/
    ├── radio-program.mp3        # 最終ラジオ番組
    └── radio-metadata.json      # メタデータ
```

## 技術仕様

### 使用技術

- **音声生成**: Aivis Cloud API
  - モデル: a59cb814-0083-4369-8542-f51a29e72af7
  - SSML対応で細かな音声制御が可能
  - 高速生成（15文字を0.3秒以下）

- **BGM生成**: MCPツール（musicgen-large等）
  - 各セクションの長さに合わせた生成
  - ラジオ番組に適した控えめな音楽

- **音声処理**: ffmpeg
  - BGM音量を60%に調整
  - セクション間に0.5秒の無音挿入
  - 最終出力: MP3 192kbps

### ワークフローのジョブ構成

1. **setup-branch**: 作業ブランチの作成
2. **script-analysis**: 台本を分析してセクションに分割
3. **voice-generation**: 各セクションの音声生成
4. **bgm-generation**: 各セクションのBGM生成
5. **audio-mixing**: 音声とBGMの結合
6. **create-pr**: プルリクエスト作成

## カスタマイズ

### 音声パラメータの調整

`voice-generation` ジョブ内で以下のパラメータを調整可能：

```json
{
  "emotional_intensity": 1.0,    // 感情表現の強さ (0.0-2.0)
  "speaking_rate": 1.0,          // 話速 (0.5-2.0)
  "pitch": 0.0,                  // ピッチ (-1.0-1.0)
  "volume": 1.0                  // 音量 (0.0-2.0)
}
```

### BGMスタイルの変更

`bgm-generation` ジョブ内のプロンプトを編集して、BGMのスタイルを変更できます。

### セクション分割の調整

`script-analysis` ジョブ内の分割ガイドラインを編集して、セクションの配分を変更できます。

## トラブルシューティング

### よくある問題

1. **音声生成エラー**
   - Aivis Cloud APIキーが正しく設定されているか確認
   - 台本に不正な文字が含まれていないか確認

2. **BGM生成エラー**
   - MCPツールの設定を確認
   - 生成時間が長い場合はタイムアウトを延長

3. **音声結合エラー**
   - ffmpegが正しくインストールされているか確認
   - 各音声ファイルが正常に生成されているか確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストや問題報告を歓迎します。大きな変更を行う場合は、まずissueを作成して議論してください。

## 関連リンク

- [Aivis Cloud API ドキュメント](https://api.aivis-project.com/docs)
- [Claude Code SDK](https://github.com/anthropic-ai/claude-code)
- [kamuicode MCP](https://github.com/AI-Summoner/ai-summoner)