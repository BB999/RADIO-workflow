# セットアップガイド - AI Radio Audio Generator

## 🚀 クイックセットアップ

### 1. 必要なAPI キーの取得

#### Claude API Key
1. [Anthropic Console](https://console.anthropic.com)にアクセス
2. APIキーを作成・取得

#### aivis-api Key
1. [Aivis Cloud API ダッシュボード](https://api.aivis-project.com/dashboard)にアクセス
2. アカウント作成・ログイン
3. APIキーを作成・取得

#### GitHub Personal Access Token
1. GitHub Settings → Developer settings → Personal access tokens
2. **Fine-grained personal access tokens**を選択
3. 必要な権限を設定：
   - Contents: Read and write
   - Pull requests: Write
   - Actions: Read

### 2. GitHub Secrets設定

リポジトリの**Settings** → **Secrets and variables** → **Actions**で以下を設定：

```yaml
ANTHROPIC_API_KEY: your_claude_api_key_here
AIVIS_API_KEY: your_aivis_api_key_here
PAT_TOKEN: your_github_pat_here
```

### 3. kamuicode MCP設定

`.claude/mcp-kamuicode.json`ファイルを作成：

```json
{
  "mcpServers": {
    "kamuicode": {
      "command": "npx",
      "args": ["kamuicode"],
      "env": {}
    }
  }
}
```

## 🔧 詳細設定

### aivis-api設定確認

#### テスト用curlコマンド
```bash
curl -X POST "https://api.aivis-project.com/v1/tts/synthesize" \
  -H "Authorization: Bearer YOUR_AIVIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_uuid": "a59cb814-0083-4369-8542-f51a29e72af7",
    "text": "テスト音声です",
    "output_format": "wav"
  }' \
  --output test-voice.wav
```

#### 利用可能モデルの確認
```bash
curl -X GET "https://api.aivis-project.com/v1/aivm-models/search" \
  -H "Authorization: Bearer YOUR_AIVIS_API_KEY"
```

### Claude Code SDK設定確認

#### テスト用JavaScriptコード
```javascript
// test-claude.js
const { ClaudeCode } = require('@anthropic-ai/claude-code');

async function testClaude() {
  const claude = new ClaudeCode({
    apiKey: process.env.ANTHROPIC_API_KEY
  });
  
  const response = await claude.prompt("Hello, Claude!");
  console.log(response);
}

testClaude().catch(console.error);
```

実行テスト：
```bash
ANTHROPIC_API_KEY=your_key node test-claude.js
```

### kamuicode MCP接続確認

#### Claude Code からのテスト
```bash
npx claude-code --prompt "kamuicode MCPサーバーに接続して、音楽生成機能をテストしてください"
```

## 🎵 音楽生成設定

### Google Lyria設定
kamuicode MCPを通じてGoogle Lyriaにアクセスします。

#### 音楽生成テスト
```bash
npx claude-code --prompt "Google Lyriaを使って、10秒程度のテスト音楽を生成してください。ジャンル：アンビエント"
```

## 🎤 音声生成設定

### 推奨モデル設定

#### カムイ日報風音声モデル
```json
{
  "model_uuid": "a59cb814-0083-4369-8542-f51a29e72af7",
  "speaking_rate": 1.1,
  "emotional_intensity": 1.2,
  "pitch": 0.0,
  "volume": 1.0,
  "output_format": "wav",
  "output_sampling_rate": 44100,
  "output_audio_channels": "mono"
}
```

### カスタム音声モデル追加

#### AivisHubからのモデル取得
1. [AivisHub](https://aivishub.com)で好みの音声モデルを検索
2. モデルUUIDを取得
3. `voice-style.json`設定を更新

## 🎚️ FFmpeg設定

### Ubuntu/GitHub Actions
```bash
sudo apt update
sudo apt install -y ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

### Windows
1. [FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロード
2. PATHに追加

### 音声合成テスト
```bash
# 音声と音楽の合成テスト
ffmpeg -i voice.wav -i music.wav \
  -filter_complex "[1:a]volume=0.3[bg];[0:a][bg]amix=inputs=2[out]" \
  -map "[out]" output.wav
```

## 🔍 トラブルシューティング

### よくある問題

#### 1. aivis-api接続エラー
```
Error: Unauthorized (401)
```
**解決策**: APIキーを確認し、正しくSecretsに設定されているか確認

#### 2. Claude Code SDK エラー
```
Error: Invalid API key
```
**解決策**: ANTHROPIC_API_KEYが正しく設定されているか確認

#### 3. kamuicode MCP接続失敗
```
Error: Failed to connect to MCP server
```
**解決策**: 
- `.claude/mcp-kamuicode.json`の設定を確認
- `npx kamuicode`が実行可能か確認

#### 4. FFmpeg音声合成エラー
```
Error: Invalid filter graph
```
**解決策**: 
- 入力ファイルの形式を確認
- FFmpegのバージョンを確認（4.0以上推奨）

### ログ確認方法

#### GitHub Actionsログ
1. Actions タブ → 該当のワークフロー実行
2. 各ステップのログを展開して確認
3. エラー箇所の特定

#### ローカルデバッグ
```bash
# Claude Code SDKのデバッグモード
DEBUG=claude-code npx claude-code --prompt "test"

# FFmpegの詳細ログ
ffmpeg -v verbose -i input.wav output.wav
```

## 📋 チェックリスト

設定完了前に以下を確認：

- [ ] ANTHROPIC_API_KEY が設定済み
- [ ] AIVIS_API_KEY が設定済み
- [ ] PAT_TOKEN が設定済み
- [ ] `.claude/mcp-kamuicode.json` が作成済み
- [ ] aivis-api接続テスト成功
- [ ] Claude Code SDK動作確認済み
- [ ] kamuicode MCP接続確認済み
- [ ] FFmpeg動作確認済み
- [ ] ワークフロー実行権限設定済み

## 🎯 最初のテスト実行

全ての設定が完了したら、シンプルな内容でテスト実行：

### テスト入力
- **原稿**: "こんにちは。AI音声生成のテストです。"
- **音楽の雰囲気**: "シンプル、アンビエント"

### 期待される出力
- 台本ファイル作成
- 音声ファイル生成（約5-10秒）
- 音楽ファイル生成（約15-20秒）
- 最終合成音声完成

テスト成功後、本格的な原稿での生成を試してください。

---

💡 **トラブル時は**: Issues に詳細なエラーログと環境情報を投稿してください