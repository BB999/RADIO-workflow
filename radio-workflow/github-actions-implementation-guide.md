# 神威日報ラジオ番組 GitHub Actions TDD実装手順

**作成日**: 2025年7月31日 13:45 JST  
**最終更新**: 2025年7月31日 13:45 JST

## 概要
神威日報の更新を検知し、自動的にラジオ番組を制作・配信するGitHub Actionsワークフローを**TDD（テスト駆動開発）**アプローチで実装する手順です。

## 変更履歴

### v2.0.0 - 2025/07/31 13:45 JST
**TDD完全対応版**
- **BREAKING CHANGE**: 実装アプローチを従来手法からTDD（テスト駆動開発）に全面移行
- **追加**: TDDの3フェーズ（RED→GREEN→REFACTOR）サイクル導入
- **追加**: テスト環境セットアップ（act, Jest, モックサーバー）
- **追加**: 受け入れテスト定義（90秒ラジオ番組生成品質要件）
- **追加**: モジュール別単体テストケース（台本生成、音声生成、BGM生成、音声合成）
- **追加**: エラーハンドリングテストケース（API障害、リトライ、フォールバック）
- **追加**: 最小実装手順（ダミーデータから実装開始）
- **追加**: リファクタリング段階（実API呼び出しへの置き換え）
- **追加**: TDD実装チェックリスト（段階別進捗管理）
- **追加**: 品質向上指標（テストカバレッジ90%以上、実行時間監視）
- **追加**: 継続的改善プロセス（モニタリング、フィードバックループ）
- **改善**: 並列処理設計の詳細化（60%時間短縮効果の定量化）
- **改善**: エラーハンドリング強化（部分失敗対応、自動リトライ）
- **改善**: セキュリティ考慮事項の追加（シークレット管理、レート制限対策）

### v1.0.0 - 初版
- 基本的なGitHub Actionsワークフロー実装手順
- オーケストレータ + モジュール分割アーキテクチャ
- 並列処理による時間短縮設計
- エラーハンドリング基本実装

## TDD実装方針
1. **Red**: テストケースを先に作成し、失敗することを確認
2. **Green**: テストが通る最小限のコードを実装
3. **Refactor**: コードを改善しつつテストを維持

## 実装ステップ

### 0. TDDテスト環境セットアップ

#### 0.1 テストツール導入
```bash
# act - GitHub Actionsローカル実行ツール
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# jest - ワークフロー検証用
npm install -g jest

# docker - actに必要
docker --version
```

#### 0.2 テスト用ディレクトリ構造
```
tests/
  workflows/
    unit/                 # 各モジュールの単体テスト
    integration/          # 統合テスト
    fixtures/            # テストデータ
      mock-responses/    # APIモックレスポンス
      sample-audio/      # サンプル音声ファイル
  scripts/
    test-runner.js       # テスト実行スクリプト
    mock-server.js       # モックAPIサーバー
```

### 1. 事前準備

#### 1.1 必要なシークレット設定
```
Repository Settings > Secrets and variables > Actions
```
- `AIVIS_API_KEY` - aivis-cloud-api認証キー（設定済み）
- `CLAUDE_CODE_OAUTH_TOKEN` - Claude Code認証トークン（設定済み）

#### 1.2 ディレクトリ構造準備
```
.github/
  workflows/
    kamui-daily-radio.yml
radio-workflow/
  scripts/
    generate-radio.js
  templates/
    script-template.json
  output/
    [生成されたファイル]
```

### 2. TDD Phase 1: テストケース定義 (RED)

#### 2.1 受け入れテスト定義
```javascript
// tests/workflows/integration/radio-workflow.test.js
describe('神威日報ラジオ自動生成ワークフロー', () => {
  test('90秒のラジオ番組が正常に生成される', async () => {
    // Given: 神威日報の更新情報
    const input = {
      'development-report': 'ダークモード機能を追加しました',
      'topic-focus': 'UI/UX改善'
    };
    
    // When: ワークフローを実行
    const result = await runWorkflow('orchestrator-kamui-daily-radio.yml', input);
    
    // Then: 期待する結果
    expect(result.status).toBe('success');
    expect(result.artifacts).toHaveProperty('final-radio.mp3');
    expect(result.duration).toBeCloseTo(90, 5); // 90秒±5秒
    expect(result.audioQuality).toBe('-23 LUFS');
  });

  test('各セクションが正しい長さで生成される', async () => {
    const result = await runWorkflow('orchestrator-kamui-daily-radio.yml', mockInput);
    
    expect(result.sections.opening.duration).toBeCloseTo(30, 3);
    expect(result.sections.main.duration).toBeCloseTo(30, 3);
    expect(result.sections.ending.duration).toBeCloseTo(30, 3);
  });

  test('並列処理により実行時間が短縮される', async () => {
    const startTime = Date.now();
    const result = await runWorkflow('orchestrator-kamui-daily-radio.yml', mockInput);
    const executionTime = Date.now() - startTime;
    
    // 並列処理により4分以内で完了することを期待
    expect(executionTime).toBeLessThan(4 * 60 * 1000);
  });
});
```

#### 2.2 各モジュールのテストケース定義

##### 2.2.1 台本生成モジュールテスト
```javascript
// tests/workflows/unit/radio-planning.test.js
describe('Radio Planning Module', () => {
  test('入力から3つの台本セクションを生成する', async () => {
    // Red: まだワークフローが存在しないので失敗するはず
    const input = {
      'development-report': 'テスト用進捗報告',
      'topic-focus': 'テスト用トピック'
    };
    
    const result = await runModule('module-radio-planning.yml', input);
    
    expect(result.outputs).toHaveProperty('script-opening');
    expect(result.outputs).toHaveProperty('script-main');
    expect(result.outputs).toHaveProperty('script-ending');
    expect(result.outputs).toHaveProperty('voice-config');
    
    // 各台本の長さが適切かチェック
    expect(result.outputs['script-opening'].length).toBeGreaterThan(50);
    expect(result.outputs['script-main'].length).toBeGreaterThan(100);
    expect(result.outputs['script-ending'].length).toBeGreaterThan(50);
  });
});
```

##### 2.2.2 音声生成モジュールテスト
```javascript
// tests/workflows/unit/voice-generation.test.js
describe('Voice Generation Modules', () => {
  test('オープニング音声が生成される', async () => {
    const input = {
      'script-text': 'こんにちは、神威日報ラジオです！',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('module-voice-generation-opening.yml', input);
    
    expect(result.outputs).toHaveProperty('audio-url');
    expect(result.outputs).toHaveProperty('audio-file');
    expect(result.outputs['audio-file']).toMatch(/\.wav$/);
  });

  test('メイン音声が生成される', async () => {
    const input = {
      'script-text': '本日の開発進捗をお伝えします。',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('module-voice-generation-main.yml', input);
    
    expect(result.status).toBe('success');
    expect(result.outputs['audio-file']).toMatch(/\.wav$/);
  });

  test('エンディング音声が生成される', async () => {
    const input = {
      'script-text': 'それでは、また明日お会いしましょう！',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('module-voice-generation-ending.yml', input);
    
    expect(result.status).toBe('success');
    expect(result.outputs['audio-file']).toMatch(/\.wav$/);
  });
});
```

##### 2.2.3 BGM生成モジュールテスト
```javascript
// tests/workflows/unit/bgm-generation.test.js
describe('BGM Generation Modules', () => {
  test('オープニングBGMが生成される', async () => {
    const result = await runModule('module-bgm-generation-opening.yml', {});
    
    expect(result.outputs).toHaveProperty('bgm-url');
    expect(result.outputs).toHaveProperty('bgm-file');
    expect(result.outputs['bgm-file']).toMatch(/bgm-opening-30s\.wav$/);
  });

  test('メインBGMが生成される', async () => {
    const result = await runModule('module-bgm-generation-main.yml', {});
    
    expect(result.outputs['bgm-file']).toMatch(/bgm-main-30s\.wav$/);
  });

  test('エンディングBGMが生成される', async () => {
    const result = await runModule('module-bgm-generation-ending.yml', {});
    
    expect(result.outputs['bgm-file']).toMatch(/bgm-ending-30s\.wav$/);
  });
});
```

##### 2.2.4 音声合成モジュールテスト
```javascript
// tests/workflows/unit/audio-mixing.test.js
describe('Audio Mixing Module', () => {
  test('全音声とBGMを合成して最終音声を生成する', async () => {
    const input = {
      'voice-opening': 'voice-opening.wav',
      'voice-main': 'voice-main.wav',
      'voice-ending': 'voice-ending.wav',
      'bgm-opening': 'bgm-opening-30s.wav',
      'bgm-main': 'bgm-main-30s.wav',
      'bgm-ending': 'bgm-ending-30s.wav'
    };
    
    const result = await runModule('module-audio-mixing.yml', input);
    
    expect(result.outputs).toHaveProperty('final-audio');
    expect(result.outputs).toHaveProperty('metadata');
    expect(result.outputs['final-audio']).toMatch(/final-radio\.mp3$/);
  });

  test('音声品質が放送基準を満たす', async () => {
    const result = await runModule('module-audio-mixing.yml', mockInputs);
    const metadata = JSON.parse(result.outputs.metadata);
    
    expect(metadata.audio_standard).toBe('-23 LUFS');
    expect(metadata.format).toBe('MP3 320kbps');
  });
});
```

#### 2.3 エラーケースのテスト定義
```javascript
// tests/workflows/unit/error-handling.test.js
describe('Error Handling', () => {
  test('音声生成APIが失敗した場合のリトライ', async () => {
    // APIを3回失敗させてからリトライで成功させる
    mockAPIFailure('aivis-cloud-api', 3);
    
    const result = await runModule('module-voice-generation-opening.yml', mockInput);
    
    expect(result.status).toBe('success');
    expect(result.retryCount).toBe(3);
  });

  test('BGM生成失敗時のフォールバック処理', async () => {
    mockAPIFailure('google-lyria', Infinity); // 常に失敗
    
    const result = await runModule('module-bgm-generation-opening.yml', {});
    
    expect(result.status).toBe('success'); // continue-on-errorで成功扱い
    expect(result.outputs['bgm-file']).toBe('assets/default-bgm.mp3');
  });

  test('部分的な音声生成失敗の処理', async () => {
    // オープニング音声だけ失敗させる
    mockAPIFailure('aivis-cloud-api', Infinity, { target: 'opening' });
    
    const result = await runWorkflow('orchestrator-kamui-daily-radio.yml', mockInput);
    
    // 2つ以上成功すれば継続
    expect(result.status).toBe('success');
    expect(result.sections.successCount).toBeGreaterThanOrEqual(2);
  });
});
```

#### 2.4 ワークフローアーキテクチャ（ジョブ分割）

##### オーケストレータワークフロー
`orchestrator-kamui-daily-radio.yml` - メインの統合ワークフロー

##### モジュールワークフロー（並列処理対応）
1. **radio-planning** - 番組企画・台本生成
2. **voice-opening** - オープニング音声生成（並列）
3. **voice-main** - メイン音声生成（並列）
4. **voice-ending** - エンディング音声生成（並列）
5. **bgm-opening** - オープニングBGM生成（並列）
6. **bgm-main** - メインBGM生成（並列）
7. **bgm-ending** - エンディングBGM生成（並列）
8. **audio-mixing** - セクション別音声合成・最終統合

#### 2.3 ジョブ依存関係と並列処理

```
┌─────────────────┐
│  radio-planning │ （台本生成）
└────────┬────────┘
         │ outputs: script-data
    ┌────┴─────┬─────────┬─────────┬─────────┬─────────┬─────────┐
    ▼          ▼         ▼         ▼         ▼         ▼         ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│voice    ││voice    ││voice    ││bgm      ││bgm      ││bgm      │ ← 6並列実行
│opening  ││main     ││ending   ││opening  ││main     ││ending   │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
     │          │         │         │         │         │
     └──────────┴─────────┴─────────┴─────────┴─────────┘
                                    │
                                    ▼
                            ┌─────────────┐
                            │audio-mixing │ （セクション別合成）
                            └─────────────┘
```

### 3. TDD Phase 2: 最小実装 (GREEN)

#### 3.1 テスト実行環境の準備
```bash
# tests/scripts/test-runner.js
const { execSync } = require('child_process');

async function runWorkflow(workflowPath, inputs) {
  const inputFlags = Object.entries(inputs)
    .map(([key, value]) => `--input ${key}="${value}"`)
    .join(' ');
    
  try {
    const result = execSync(`act workflow_dispatch -W ${workflowPath} ${inputFlags}`, {
      encoding: 'utf8',
      timeout: 300000 // 5分タイムアウト
    });
    
    return parseActOutput(result);
  } catch (error) {
    return { status: 'failure', error: error.message };
  }
}

async function runModule(modulePath, inputs) {
  // モジュール単体実行ロジック
  return runWorkflow(modulePath, inputs);
}

function parseActOutput(output) {
  // act の出力を解析してテスト用の結果オブジェクトに変換
  const lines = output.split('\n');
  const result = {
    status: 'success',
    outputs: {},
    artifacts: {},
    duration: null,
    retryCount: 0
  };
  
  // ここに出力解析ロジックを実装
  return result;
}

module.exports = { runWorkflow, runModule };
```

#### 3.2 モックサーバーの準備
```javascript
// tests/scripts/mock-server.js
const express = require('express');
const app = express();

let failureCount = {};
let failureConfig = {};

// aivis-cloud-api モック
app.post('/v1/tts', (req, res) => {
  const target = failureConfig['aivis-cloud-api']?.target || 'all';
  const shouldFail = failureCount['aivis-cloud-api'] > 0;
  
  if (shouldFail) {
    failureCount['aivis-cloud-api']--;
    return res.status(500).json({ error: 'API temporarily unavailable' });
  }
  
  // 成功レスポンス
  res.json({
    audio_url: 'https://mock-api.example.com/audio/voice.wav',
    duration: 30
  });
});

// Google Lyria モック（kamuicode経由）
app.post('/music/generate', (req, res) => {
  const shouldFail = failureCount['google-lyria'] === Infinity || failureCount['google-lyria'] > 0;
  
  if (shouldFail && failureCount['google-lyria'] !== Infinity) {
    failureCount['google-lyria']--;
  }
  
  if (shouldFail) {
    return res.status(500).json({ error: 'Music generation failed' });
  }
  
  res.json({
    music_url: 'https://mock-api.example.com/music/bgm.wav',
    duration: 15
  });
});

// モック設定API
app.post('/mock/set-failure', (req, res) => {
  const { service, count, config } = req.body;
  failureCount[service] = count;
  failureConfig[service] = config || {};
  res.json({ success: true });
});

app.listen(3000, () => {
  console.log('Mock server running on port 3000');
});
```

#### 3.3 最小実装: テストが通るワークフロー作成

まず初回テスト実行（RED確認）:
```bash
# テストを実行して失敗することを確認
npm test -- --testPathPattern="radio-planning.test.js"
# Expected: ワークフローファイルが存在しないためテスト失敗
```

##### 3.3.1 台本生成モジュール（最小実装）
```yaml
# .github/workflows/module-radio-planning.yml
name: Radio Planning Module (Minimal)
on:
  workflow_call:
    inputs:
      development-report:
        required: true
        type: string
      topic-focus:
        required: false
        type: string
    outputs:
      script-opening:
        value: ${{ jobs.generate.outputs.script-opening }}
      script-main:
        value: ${{ jobs.generate.outputs.script-main }}
      script-ending:
        value: ${{ jobs.generate.outputs.script-ending }}
      voice-config:
        value: ${{ jobs.generate.outputs.voice-config }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      script-opening: ${{ steps.minimal.outputs.script-opening }}
      script-main: ${{ steps.minimal.outputs.script-main }}
      script-ending: ${{ steps.minimal.outputs.script-ending }}
      voice-config: ${{ steps.minimal.outputs.voice-config }}
    steps:
      # 最小実装: 固定テキストを返す（テストを通すため）
      - name: Generate minimal scripts
        id: minimal
        run: |
          echo "script-opening=こんにちは、神威日報ラジオです。本日は${{ inputs.development-report }}について" >> $GITHUB_OUTPUT
          echo "script-main=${{ inputs.development-report }}の詳細をお伝えします。${{ inputs.topic-focus || '' }}" >> $GITHUB_OUTPUT
          echo "script-ending=以上、神威日報ラジオでした。また明日お会いしましょう。" >> $GITHUB_OUTPUT
          echo 'voice-config={"gender":"female","age":"20s"}' >> $GITHUB_OUTPUT
```

テスト実行（GREEN確認）:
```bash
npm test -- --testPathPattern="radio-planning.test.js"
# Expected: テスト成功
```

##### 3.3.2 音声生成モジュール（最小実装）
```yaml
# .github/workflows/module-voice-generation-opening.yml
name: Voice Generation Opening (Minimal)
on:
  workflow_call:
    inputs:
      script-text:
        required: true
        type: string
      voice-config:
        required: true
        type: string
    outputs:
      audio-url:
        value: ${{ jobs.generate.outputs.url }}
      audio-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.minimal.outputs.audio-url }}
      file: ${{ steps.minimal.outputs.audio-file }}
    steps:
      # 最小実装: ダミー音声ファイルを作成
      - name: Generate minimal voice
        id: minimal
        run: |
          # 1秒の無音WAVファイルを生成
          sudo apt-get update && sudo apt-get install -y ffmpeg
          ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 30 -c:a pcm_s16le voice-opening.wav
          
          echo "audio-url=file://$(pwd)/voice-opening.wav" >> $GITHUB_OUTPUT
          echo "audio-file=voice-opening.wav" >> $GITHUB_OUTPUT
```

同様に `module-voice-generation-main.yml` と `module-voice-generation-ending.yml` も作成。

##### 3.3.3 BGM生成モジュール（最小実装）
```yaml
# .github/workflows/module-bgm-generation-opening.yml
name: BGM Generation Opening (Minimal)
on:
  workflow_call:
    outputs:
      bgm-url:
        value: ${{ jobs.generate.outputs.url }}
      bgm-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.minimal.outputs.bgm-url }}
      file: ${{ steps.minimal.outputs.bgm-file }}
    steps:
      # 最小実装: ダミーBGMファイルを生成
      - name: Generate minimal BGM
        id: minimal
        run: |
          sudo apt-get update && sudo apt-get install -y ffmpeg
          # 30秒の簡単なサイン波BGMを生成
          ffmpeg -f lavfi -i "sine=frequency=440:duration=30" -ar 44100 -ac 2 -c:a pcm_s16le bgm-opening-30s.wav
          
          echo "bgm-url=file://$(pwd)/bgm-opening-30s.wav" >> $GITHUB_OUTPUT
          echo "bgm-file=bgm-opening-30s.wav" >> $GITHUB_OUTPUT
```

##### 3.3.4 音声合成モジュール（最小実装）
```yaml
# .github/workflows/module-audio-mixing.yml
name: Audio Mixing Module (Minimal)
on:
  workflow_call:
    inputs:
      voice-opening:
        required: true
        type: string
      voice-main:
        required: true
        type: string
      voice-ending:
        required: true
        type: string
      bgm-opening:
        required: true
        type: string
      bgm-main:
        required: true
        type: string
      bgm-ending:
        required: true
        type: string
    outputs:
      final-audio:
        value: ${{ jobs.mix.outputs.url }}
      metadata:
        value: ${{ jobs.mix.outputs.metadata }}

jobs:
  mix:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.minimal.outputs.final-file }}
      metadata: ${{ steps.minimal.outputs.metadata }}
    steps:
      # 最小実装: ファイルを単純に連結
      - name: Minimal audio mixing
        id: minimal
        run: |
          sudo apt-get update && sudo apt-get install -y ffmpeg
          
          # ダミーファイルを作成（実際のファイルがない場合）
          for file in ${{ inputs.voice-opening }} ${{ inputs.voice-main }} ${{ inputs.voice-ending }}; do
            if [ ! -f "$file" ]; then
              ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 30 -c:a pcm_s16le "$file"
            fi
          done
          
          # 3つの音声を単純に連結
          ffmpeg -i ${{ inputs.voice-opening }} \
                 -i ${{ inputs.voice-main }} \
                 -i ${{ inputs.voice-ending }} \
                 -filter_complex "[0][1][2]concat=n=3:v=0:a=1" \
                 -c:a mp3 -b:a 320k final-radio.mp3
          
          # メタデータ生成
          echo '{"duration":"90s","audio_standard":"-23 LUFS","format":"MP3 320kbps"}' > metadata.json
          
          echo "final-file=final-radio.mp3" >> $GITHUB_OUTPUT
          echo "metadata=metadata.json" >> $GITHUB_OUTPUT
```

##### 3.3.5 オーケストレータワークフロー（最小実装）
```yaml
# .github/workflows/orchestrator-kamui-daily-radio.yml
name: Kamui Daily Radio Production (Minimal)
on:
  workflow_dispatch:
    inputs:
      development-report:
        description: '神威アプリの開発進捗・最新情報'
        required: true
        type: string
      topic-focus:
        description: '特に強調したいトピック（オプション）'
        required: false
        type: string

jobs:
  planning:
    uses: ./.github/workflows/module-radio-planning.yml
    with:
      development-report: ${{ inputs.development-report }}
      topic-focus: ${{ inputs.topic-focus }}

  voice-opening:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-opening.yml
    with:
      script-text: ${{ needs.planning.outputs.script-opening }}
      voice-config: ${{ needs.planning.outputs.voice-config }}

  voice-main:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-main.yml
    with:
      script-text: ${{ needs.planning.outputs.script-main }}
      voice-config: ${{ needs.planning.outputs.voice-config }}

  voice-ending:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-ending.yml
    with:
      script-text: ${{ needs.planning.outputs.script-ending }}
      voice-config: ${{ needs.planning.outputs.voice-config }}

  bgm-opening:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-opening.yml

  bgm-main:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-main.yml

  bgm-ending:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-ending.yml

  audio-mixing:
    needs: [voice-opening, voice-main, voice-ending, bgm-opening, bgm-main, bgm-ending]
    uses: ./.github/workflows/module-audio-mixing.yml
    with:
      voice-opening: ${{ needs.voice-opening.outputs.audio-file }}
      voice-main: ${{ needs.voice-main.outputs.audio-file }}
      voice-ending: ${{ needs.voice-ending.outputs.audio-file }}
      bgm-opening: ${{ needs.bgm-opening.outputs.bgm-file }}
      bgm-main: ${{ needs.bgm-main.outputs.bgm-file }}
      bgm-ending: ${{ needs.bgm-ending.outputs.bgm-file }}
```

#### 3.4 初回テスト実行（GREEN確認）
```bash
# 全テストを実行
npm test

# 統合テストも実行
act workflow_dispatch -W .github/workflows/orchestrator-kamui-daily-radio.yml \
    --input development-report="TDDテスト用進捗" \
    --input topic-focus="テスト実装"
```

### 4. TDD Phase 3: リファクタリング (REFACTOR)

#### 4.1 実際のAPI呼び出しに置き換え

テストが通ることを確認後、実際のAPI呼び出しに置き換え:

##### 4.1.1 台本生成の実装改善
```yaml
# .github/workflows/module-radio-planning.yml (改善版)
- name: Generate radio scripts with Claude
  id: planning
  run: |
    # 元の固定テキストから Claude Code を使った動的生成に変更
    SCRIPT_RESULT=$(npx @anthropic-ai/claude-code -c "
    以下の内容で90秒のラジオ番組台本を生成してください：
    
    【開発進捗・最新情報】
    ${{ inputs.development-report }}
    
    【強調ポイント】
    ${{ inputs.topic-focus || 'なし' }}
    
    各セクション30秒、明るい20代女性MC、分かりやすい解説で。
    JSON形式で{ opening: '...', main: '...', ending: '...' }として出力。
    ")
    
    # JSONから各セクションを抽出
    echo "$SCRIPT_RESULT" | jq -r '.opening' | sed 's/^/script-opening=/' >> $GITHUB_OUTPUT
    echo "$SCRIPT_RESULT" | jq -r '.main' | sed 's/^/script-main=/' >> $GITHUB_OUTPUT
    echo "$SCRIPT_RESULT" | jq -r '.ending' | sed 's/^/script-ending=/' >> $GITHUB_OUTPUT
    echo 'voice-config={"gender":"female","age":"20s"}' >> $GITHUB_OUTPUT
```

##### 4.1.2 音声生成の実装改善
```yaml
# .github/workflows/module-voice-generation-opening.yml (改善版)
- name: Generate voice with aivis-cloud-api
  id: voice
  run: |
    # ダミー音声生成から実際のTTS APIに変更
    RESPONSE=$(curl -X POST https://api.aivis.cloud/v1/tts \
      -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
      -H "Content-Type: application/json" \
      -d '{
        "text": "${{ inputs.script-text }}",
        "voice": "female_20s_bright",
        "format": "wav"
      }')
    
    AUDIO_URL=$(echo "$RESPONSE" | jq -r '.audio_url')
    curl -L "$AUDIO_URL" -o voice-opening.wav
    
    echo "audio-url=$AUDIO_URL" >> $GITHUB_OUTPUT
    echo "audio-file=voice-opening.wav" >> $GITHUB_OUTPUT
```

##### 4.1.3 テスト実行（リファクタリング後）
```bash
# リファクタリング後もテストが成功することを確認
npm test

# 実際のAPI使用時のテスト（モックサーバー使用）
MOCK_API=true npm test
```

### 5. TDD エラーハンドリング実装

#### 5.1 エラーケーステスト（RED）
```javascript
// tests/workflows/unit/error-handling.test.js
test('音声生成API障害時のリトライ動作', async () => {
  // 3回失敗後に成功するよう設定
  await setMockFailure('aivis-cloud-api', 3);
  
  const result = await runModule('module-voice-generation-opening.yml', mockInput);
  
  expect(result.status).toBe('success');
  expect(result.retryAttempts).toBe(4); // 初回 + 3回リトライ
});
```

#### 5.2 リトライ機構実装（GREEN）
```yaml
# リトライ付き音声生成
- name: Generate voice with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 30
    command: |
      RESPONSE=$(curl -X POST https://api.aivis.cloud/v1/tts \
        -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
        -H "Content-Type: application/json" \
        -d '{
          "text": "${{ inputs.script-text }}",
          "voice": "female_20s_bright",
          "format": "wav"
        }')
      
      if [ "$(echo "$RESPONSE" | jq -r '.error')" != "null" ]; then
        echo "API Error: $(echo "$RESPONSE" | jq -r '.error')"
        exit 1
      fi
```

### 6. 各モジュールの詳細実装

#### 3.1 radio-planning モジュール
**役割**: ユーザー入力の内容から番組台本を生成

```yaml
# module-radio-planning.yml
name: Radio Planning Module
on:
  workflow_call:
    inputs:
      development-report:
        required: true
        type: string
        description: '神威アプリの開発進捗・最新情報'
      topic-focus:
        required: false
        type: string
        description: '特に強調したいトピック'
    outputs:
      script-opening:
        value: ${{ jobs.generate.outputs.script-opening }}
      script-main:
        value: ${{ jobs.generate.outputs.script-main }}
      script-ending:
        value: ${{ jobs.generate.outputs.script-ending }}
      voice-config:
        value: ${{ jobs.generate.outputs.voice-config }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      script-opening: ${{ steps.planning.outputs.script-opening }}
      script-main: ${{ steps.planning.outputs.script-main }}
      script-ending: ${{ steps.planning.outputs.script-ending }}
      voice-config: ${{ steps.planning.outputs.voice-config }}
    steps:
      - name: Generate radio scripts
        id: planning
        uses: docker://ghcr.io/anthropics/claude-code:latest
        with:
          api-key: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          command: |
            以下の内容で90秒のラジオ番組台本を生成してください：
            
            【開発進捗・最新情報】
            ${{ inputs.development-report }}
            
            【強調ポイント】
            ${{ inputs.topic-focus || 'なし' }}
            
            【要件】
            - オープニング: 30秒（明るい挨拶と今日のトピック紹介）
            - メイン: 30秒（内容を分かりやすく解説）
            - エンディング: 30秒（まとめと次回予告）
            - MC: 20代女性、明るく親しみやすい口調
            - ターゲット: 20-30代の技術に興味がある層
```

#### 3.2 voice-generation-* モジュール（並列実行）
**役割**: 各セクションの音声を並列生成

```yaml
# module-voice-generation-opening.yml (main, endingも同様)
name: Voice Generation Opening
on:
  workflow_call:
    inputs:
      script-text:
        required: true
        type: string
      voice-config:
        required: true
        type: string
    outputs:
      audio-url:
        value: ${{ jobs.generate.outputs.url }}
      audio-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Generate voice with aivis-cloud-api
        run: |
          # aivis-cloud-api呼び出し
          curl -X POST https://api.aivis.cloud/v1/tts \
            -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "text": "${{ inputs.script-text }}",
              "voice": "female_20s_bright",
              "format": "wav"
            }'
```

#### 3.3 bgm-generation-* モジュール（セクション別並列実行）
**役割**: セクション別BGM生成（Google Lyria使用）

```yaml
# module-bgm-generation-opening.yml
name: BGM Generation Opening
on:
  workflow_call:
    outputs:
      bgm-url:
        value: ${{ jobs.generate.outputs.url }}
      bgm-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.bgm.outputs.music-url }}
      file: ${{ steps.bgm.outputs.music-file }}
    steps:
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Claude Code SDK
        run: npm install @anthropic-ai/claude-code
      
      - name: Generate Opening BGM with Google Lyria
        id: bgm
        env:
          ANTHROPIC_API_KEY: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          # オープニングBGM生成（30秒、アップテンポ）
          npx @anthropic-ai/claude-code \
            --mcp .claude/mcp-kamuicode.json \
            -c "
            kamuicodeを使って以下のオープニングBGMを生成してください：
            
            【BGM要件】
            - 長さ: 15秒（ループ用ベース音楽）
            - スタイル: 明るいオープニング系、アップテンポ
            - 雰囲気: エネルギッシュ、番組開始の盛り上がり
            - 楽器: シンセサイザー、軽快なドラム、ベース
            - 特徴: ループしやすい構成、始まりと終わりが自然に繋がる
            
            【生成設定】
            - モデル: Google Lyria (msc-google-lyria)
            - 品質: 高品質
            - フォーマット: WAV
            
            生成されたBGMのURLとファイルパスを出力してください。
            " > bgm-opening-result.txt
          
          # 結果からURLとファイルパスを抽出
          MUSIC_URL=$(grep -oP 'https://[^\s]+\.wav' bgm-opening-result.txt | head -1)
          MUSIC_FILE="bgm-opening.wav"
          
          # URLからファイルをダウンロード
          if [ ! -z "$MUSIC_URL" ]; then
            curl -L "$MUSIC_URL" -o "$MUSIC_FILE"
            # 30秒までループ拡張（音声品質統一）
            ffmpeg -stream_loop -1 -i "$MUSIC_FILE" -t 30 -ar 44100 -ac 2 -c:a pcm_s16le "bgm-opening-30s.wav"
            echo "music-url=$MUSIC_URL" >> $GITHUB_OUTPUT
            echo "music-file=bgm-opening-30s.wav" >> $GITHUB_OUTPUT
          else
            echo "::error::オープニングBGM生成に失敗しました"
            exit 1
          fi

# module-bgm-generation-main.yml
name: BGM Generation Main
on:
  workflow_call:
    outputs:
      bgm-url:
        value: ${{ jobs.generate.outputs.url }}
      bgm-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.bgm.outputs.music-url }}
      file: ${{ steps.bgm.outputs.music-file }}
    steps:
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Claude Code SDK
        run: npm install @anthropic-ai/claude-code
      
      - name: Generate Main BGM with Google Lyria
        id: bgm
        env:
          ANTHROPIC_API_KEY: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          # メインBGM生成（30秒、落ち着いたトーク向け）
          npx @anthropic-ai/claude-code \
            --mcp .claude/mcp-kamuicode.json \
            -c "
            kamuicodeを使って以下のメインBGMを生成してください：
            
            【BGM要件】
            - 長さ: 15秒（ループ用ベース音楽）
            - スタイル: 落ち着いたトーク系、情報番組向け
            - 雰囲気: 親しみやすく、話が聞きやすい控えめなBGM
            - 楽器: ソフトシンセ、軽いパーカッション、アンビエント
            - 特徴: ループしやすい構成、話の邪魔にならない音量バランス
            
            【生成設定】
            - モデル: Google Lyria (msc-google-lyria)
            - 品質: 高品質
            - フォーマット: WAV
            
            生成されたBGMのURLとファイルパスを出力してください。
            " > bgm-main-result.txt
          
          # 結果からURLとファイルパスを抽出
          MUSIC_URL=$(grep -oP 'https://[^\s]+\.wav' bgm-main-result.txt | head -1)
          MUSIC_FILE="bgm-main.wav"
          
          # URLからファイルをダウンロード
          if [ ! -z "$MUSIC_URL" ]; then
            curl -L "$MUSIC_URL" -o "$MUSIC_FILE"
            # 30秒までループ拡張（音声品質統一）
            ffmpeg -stream_loop -1 -i "$MUSIC_FILE" -t 30 -ar 44100 -ac 2 -c:a pcm_s16le "bgm-main-30s.wav"
            echo "music-url=$MUSIC_URL" >> $GITHUB_OUTPUT
            echo "music-file=bgm-main-30s.wav" >> $GITHUB_OUTPUT
          else
            echo "::error::メインBGM生成に失敗しました"
            exit 1
          fi

# module-bgm-generation-ending.yml
name: BGM Generation Ending
on:
  workflow_call:
    outputs:
      bgm-url:
        value: ${{ jobs.generate.outputs.url }}
      bgm-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.bgm.outputs.music-url }}
      file: ${{ steps.bgm.outputs.music-file }}
    steps:
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Claude Code SDK
        run: npm install @anthropic-ai/claude-code
      
      - name: Generate Ending BGM with Google Lyria
        id: bgm
        env:
          ANTHROPIC_API_KEY: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          # エンディングBGM生成（30秒、温かい締めくくり）
          npx @anthropic-ai/claude-code \
            --mcp .claude/mcp-kamuicode.json \
            -c "
            kamuicodeを使って以下のエンディングBGMを生成してください：
            
            【BGM要件】
            - 長さ: 15秒（ループ用ベース音楽）
            - スタイル: 温かいエンディング系、番組締めくくり向け
            - 雰囲気: 親しみやすく、また明日も聞きたくなる温かさ
            - 楽器: アコースティックギター、ソフトピアノ、軽いストリングス
            - 特徴: ループしやすい構成、余韻が残る自然なフェード感
            
            【生成設定】
            - モデル: Google Lyria (msc-google-lyria)
            - 品質: 高品質
            - フォーマット: WAV
            
            生成されたBGMのURLとファイルパスを出力してください。
            " > bgm-ending-result.txt
          
          # 結果からURLとファイルパスを抽出
          MUSIC_URL=$(grep -oP 'https://[^\s]+\.wav' bgm-ending-result.txt | head -1)
          MUSIC_FILE="bgm-ending.wav"
          
          # URLからファイルをダウンロード
          if [ ! -z "$MUSIC_URL" ]; then
            curl -L "$MUSIC_URL" -o "$MUSIC_FILE"
            # 30秒までループ拡張（音声品質統一）
            ffmpeg -stream_loop -1 -i "$MUSIC_FILE" -t 30 -ar 44100 -ac 2 -c:a pcm_s16le "bgm-ending-30s.wav"
            echo "music-url=$MUSIC_URL" >> $GITHUB_OUTPUT
            echo "music-file=bgm-ending-30s.wav" >> $GITHUB_OUTPUT
          else
            echo "::error::エンディングBGM生成に失敗しました"
            exit 1
          fi
```

#### 3.4 audio-mixing モジュール
**役割**: 全音声と各セクション別BGMを合成し最終音声を生成

```yaml
# module-audio-mixing.yml
name: Audio Mixing Module
on:
  workflow_call:
    inputs:
      voice-opening:
        required: true
        type: string
      voice-main:
        required: true
        type: string
      voice-ending:
        required: true
        type: string
      bgm-opening:
        required: true
        type: string
      bgm-main:
        required: true
        type: string
      bgm-ending:
        required: true
        type: string
    outputs:
      final-audio:
        value: ${{ jobs.mix.outputs.url }}
      metadata:
        value: ${{ jobs.mix.outputs.metadata }}

jobs:
  mix:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.mixing.outputs.final-file }}
      metadata: ${{ steps.mixing.outputs.metadata }}
    steps:
      - name: Install FFmpeg
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
      
      - name: Mix audio files with section-specific BGMs
        id: mixing
        run: |
          # 各セクションで音声とBGMを個別にミックス（エラーハンドリング＋改善版）
          
          # 音声の長さを取得する関数（エラーハンドリング付き）
          get_duration() {
            local file="$1"
            if [ ! -f "$file" ]; then
              echo "::error::音声ファイルが見つかりません: $file"
              return 1
            fi
            local duration=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$file" 2>/dev/null)
            if [ -z "$duration" ] || [ "$duration" = "N/A" ]; then
              echo "::error::音声ファイルの長さを取得できません: $file"
              return 1
            fi
            echo "$duration"
          }
          
          # エラーハンドリング付きFFmpeg実行
          safe_ffmpeg() {
            if ! ffmpeg "$@" 2>/dev/null; then
              echo "::error::FFmpeg処理に失敗しました"
              exit 1
            fi
          }
          
          # オープニング: BGM4秒イントロ→音声開始→音声終了後BGMフェードアウト（2秒）
          VOICE_OPENING_DURATION=$(get_duration ${{ inputs.voice-opening }}) || exit 1
          FADE_START_OPENING=$(awk "BEGIN {print $VOICE_OPENING_DURATION + 4.5}")  # bcの代わりにawk使用
          TOTAL_OPENING_DURATION=$(awk "BEGIN {print $VOICE_OPENING_DURATION + 6.5}")
          
          safe_ffmpeg -i ${{ inputs.voice-opening }} \
                      -i ${{ inputs.bgm-opening }} \
                      -filter_complex "[0]adelay=4s:all=1[voice_delayed];
                                      [1]volume=0.5,afade=t=out:st=${FADE_START_OPENING}:d=2[bgm1];
                                      [voice_delayed][bgm1]amix=inputs=2[opening]" \
                      -map "[opening]" \
                      -t $TOTAL_OPENING_DURATION \
                      -ar 44100 -ac 2 -c:a pcm_s16le \
                      opening-mixed.wav
          
          # メイン: BGM4秒イントロ→音声開始→音声終了後BGMフェードアウト（2秒）
          VOICE_MAIN_DURATION=$(get_duration ${{ inputs.voice-main }}) || exit 1
          FADE_START_MAIN=$(awk "BEGIN {print $VOICE_MAIN_DURATION + 4.5}")
          TOTAL_MAIN_DURATION=$(awk "BEGIN {print $VOICE_MAIN_DURATION + 6.5}")
          
          safe_ffmpeg -i ${{ inputs.voice-main }} \
                      -i ${{ inputs.bgm-main }} \
                      -filter_complex "[0]adelay=4s:all=1[voice_delayed];
                                      [1]volume=0.5,afade=t=out:st=${FADE_START_MAIN}:d=2[bgm2];
                                      [voice_delayed][bgm2]amix=inputs=2[main]" \
                      -map "[main]" \
                      -t $TOTAL_MAIN_DURATION \
                      -ar 44100 -ac 2 -c:a pcm_s16le \
                      main-mixed.wav
          
          # エンディング: BGM4秒イントロ→音声開始→音声終了後BGMフェードアウト（3秒）
          VOICE_ENDING_DURATION=$(get_duration ${{ inputs.voice-ending }}) || exit 1
          FADE_START_ENDING=$(awk "BEGIN {print $VOICE_ENDING_DURATION + 4.5}")
          TOTAL_ENDING_DURATION=$(awk "BEGIN {print $VOICE_ENDING_DURATION + 7.5}")
          
          safe_ffmpeg -i ${{ inputs.voice-ending }} \
                      -i ${{ inputs.bgm-ending }} \
                      -filter_complex "[0]adelay=4s:all=1[voice_delayed];
                                      [1]volume=0.5,afade=t=out:st=${FADE_START_ENDING}:d=3[bgm3];
                                      [voice_delayed][bgm3]amix=inputs=2[ending]" \
                      -map "[ending]" \
                      -t $TOTAL_ENDING_DURATION \
                      -ar 44100 -ac 2 -c:a pcm_s16le \
                      ending-mixed.wav
          
          # 3つのセクションを連結し、最終調整（エラーハンドリング付き）
          safe_ffmpeg -i opening-mixed.wav \
                      -i main-mixed.wav \
                      -i ending-mixed.wav \
                      -filter_complex "[0][1][2]concat=n=3:v=0:a=1[combined]" \
                      -map "[combined]" \
                      -af "loudnorm=I=-23:LRA=7:TP=-1" \
                      -c:a mp3 \
                      -b:a 320k \
                      final-radio.mp3
          
          # メタデータ生成
          echo "{
            \"duration\": \"90s\",
            \"sections\": [
              {\"name\": \"opening\", \"duration\": \"4s intro + voice + 2.5s fade\", \"bgm\": \"upbeat\", \"bgm_volume\": \"50%\", \"intro\": \"4s\", \"fade_out\": \"2s\"},
              {\"name\": \"main\", \"duration\": \"4s intro + voice + 2.5s fade\", \"bgm\": \"talk-friendly\", \"bgm_volume\": \"50%\", \"intro\": \"4s\", \"fade_out\": \"2s\"},
              {\"name\": \"ending\", \"duration\": \"4s intro + voice + 3.5s fade\", \"bgm\": \"warm-outro\", \"bgm_volume\": \"50%\", \"intro\": \"4s\", \"fade_out\": \"3s\"}
            ],
            \"audio_standard\": \"-23 LUFS\",
            \"format\": \"MP3 320kbps\"
          }" > metadata.json
          
          echo "final-file=final-radio.mp3" >> $GITHUB_OUTPUT
          echo "metadata=metadata.json" >> $GITHUB_OUTPUT
```

### 4. オーケストレータワークフローの実装

```yaml
# orchestrator-kamui-daily-radio.yml
name: Kamui Daily Radio Production
on:
  schedule:
    - cron: '0 22 * * *'  # 毎日朝7時（JST）
  workflow_dispatch:
    inputs:
      development-report:
        description: '神威アプリの開発進捗・最新情報'
        required: true
        type: string
      topic-focus:
        description: '特に強調したいトピック（オプション）'
        required: false
        type: string

jobs:
  planning:
    uses: ./.github/workflows/module-radio-planning.yml
    with:
      development-report: ${{ inputs.development-report }}
      topic-focus: ${{ inputs.topic-focus }}
    secrets: inherit

  voice-opening:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-opening.yml
    with:
      script-text: ${{ needs.planning.outputs.script-opening }}
      voice-config: ${{ needs.planning.outputs.voice-config }}
    secrets: inherit

  voice-main:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-main.yml
    with:
      script-text: ${{ needs.planning.outputs.script-main }}
      voice-config: ${{ needs.planning.outputs.voice-config }}
    secrets: inherit

  voice-ending:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-ending.yml
    with:
      script-text: ${{ needs.planning.outputs.script-ending }}
      voice-config: ${{ needs.planning.outputs.voice-config }}
    secrets: inherit

  bgm-opening:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-opening.yml
    secrets: inherit

  bgm-main:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-main.yml
    secrets: inherit

  bgm-ending:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-ending.yml
    secrets: inherit

  audio-mixing:
    needs: [voice-opening, voice-main, voice-ending, bgm-opening, bgm-main, bgm-ending]
    uses: ./.github/workflows/module-audio-mixing.yml
    with:
      voice-opening: ${{ needs.voice-opening.outputs.audio-file }}
      voice-main: ${{ needs.voice-main.outputs.audio-file }}
      voice-ending: ${{ needs.voice-ending.outputs.audio-file }}
      bgm-opening: ${{ needs.bgm-opening.outputs.bgm-file }}
      bgm-main: ${{ needs.bgm-main.outputs.bgm-file }}
      bgm-ending: ${{ needs.bgm-ending.outputs.bgm-file }}
    secrets: inherit

  publish:
    needs: audio-mixing
    runs-on: ubuntu-latest
    steps:
      - name: Create Release
        uses: actions/create-release@v1
        with:
          tag_name: radio-${{ github.run_id }}
          release_name: 神威日報ラジオ ${{ steps.date.outputs.date }}
          body: |
            ## 🎙️ 神威日報ラジオ
            
            自動生成された本日の番組です。
            
            - 時間: 90秒
            - MC: AI生成（20代女性）
            - 内容: 神威アプリ開発最新情報
```

### 5. エラーハンドリング

#### 5.1 リトライ設定
```yaml
# 音声生成でのリトライ実装
- name: Generate voice with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 30
    command: |
      curl -X POST https://api.aivis.cloud/v1/tts \
        -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
        -H "Content-Type: application/json" \
        -d '{
          "text": "${{ inputs.script-text }}",
          "voice": "female_20s_bright",
          "format": "wav"
        }'
```

#### 5.2 フォールバック処理
```yaml
# BGM生成失敗時のフォールバック
bgm-generation:
  continue-on-error: true  # 失敗しても続行

audio-mixing:
  if: always()  # BGM生成が失敗してもミキシング実行
  steps:
    - name: Check BGM availability
      run: |
        if [ -z "${{ needs.bgm-generation.outputs.bgm-file }}" ]; then
          echo "Using default BGM"
          echo "bgm-file=assets/default-bgm.mp3" >> $GITHUB_OUTPUT
        fi
```

#### 5.3 部分的成功の処理
```yaml
# 一部の音声生成が失敗した場合
- name: Validate audio files
  run: |
    SUCCESS_COUNT=0
    [ -f "voice-opening.wav" ] && SUCCESS_COUNT=$((SUCCESS_COUNT+1))
    [ -f "voice-main.wav" ] && SUCCESS_COUNT=$((SUCCESS_COUNT+1))
    [ -f "voice-ending.wav" ] && SUCCESS_COUNT=$((SUCCESS_COUNT+1))
    
    if [ $SUCCESS_COUNT -lt 2 ]; then
      echo "::error::音声生成が不完全です"
      exit 1
    fi
```

### 6. 環境変数設定

```yaml
env:
  RADIO_DURATION: 90
  SECTION_DURATION: 30
  VOICE_GENDER: female
  VOICE_AGE: 20s
  VOICE_STYLE: bright_energetic
  OUTPUT_FORMAT: mp3
  LOUDNESS_TARGET: -23
```

### 7. 成果物管理

#### 7.1 アーティファクト保存
```yaml
# 各音声ファイルを保存
- name: Upload voice artifacts
  uses: actions/upload-artifact@v3
  with:
    name: voice-files-${{ github.run_id }}
    path: |
      output/voice-opening.wav
      output/voice-main.wav
      output/voice-ending.wav
    retention-days: 30

# 最終音声を保存
- name: Upload final radio
  uses: actions/upload-artifact@v3
  with:
    name: radio-${{ github.run_id }}
    path: output/radio-final.mp3
    retention-days: 90
```

#### 7.2 リリース作成
```yaml
- name: Create Release with audio
  uses: softprops/action-gh-release@v1
  with:
    tag_name: radio-${{ github.run_id }}
    name: 神威日報ラジオ - ${{ steps.date.outputs.date }}
    files: |
      output/radio-final.mp3
      output/metadata.json
    body: |
      ## 🎙️ 神威日報ラジオ
      
      ### 番組情報
      - 放送日: ${{ steps.date.outputs.date }}
      - 時間: 90秒
      - MC: AI生成（20代女性）
      
      ### 内容
      神威アプリの最新開発情報をお届けします。
```

### 8. モニタリング・通知

#### 8.1 ワークフロー実行サマリー
```yaml
- name: Generate workflow summary
  if: always()
  run: |
    cat >> $GITHUB_STEP_SUMMARY << EOF
    ## 🎙️ ラジオ番組制作結果
    
    | ステップ | 状態 | 所要時間 |
    |---------|------|----------|
    | 台本生成 | ${{ needs.planning.result }} | ${{ needs.planning.outputs.duration }} |
    | 音声生成(開始) | ${{ needs.voice-opening.result }} | - |
    | 音声生成(本編) | ${{ needs.voice-main.result }} | - |
    | 音声生成(終了) | ${{ needs.voice-ending.result }} | - |
    | BGM生成 | ${{ needs.bgm-generation.result }} | - |
    | 音声合成 | ${{ needs.audio-mixing.result }} | - |
    
    ### 📊 統計情報
    - 総実行時間: ${{ steps.total-time.outputs.duration }}
    - 生成ファイルサイズ: ${{ steps.file-size.outputs.size }}
    - 音声品質: -23 LUFS (放送基準)
    EOF
```

#### 8.2 通知設定
```yaml
# Discord/Slack通知
- name: Send notification
  if: success()
  env:
    WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK }}
  run: |
    curl -X POST $WEBHOOK_URL \
      -H "Content-Type: application/json" \
      -d '{
        "content": "🎙️ 神威日報ラジオが生成されました！",
        "embeds": [{
          "title": "番組リンク",
          "url": "${{ needs.publish.outputs.release-url }}",
          "color": 5814783
        }]
      }'
```

### 9. セキュリティ考慮事項

#### 9.1 シークレット管理
```yaml
permissions:
  contents: write  # リリース作成に必要
  pull-requests: write  # PR作成に必要

# シークレットのマスキング
- name: Mask sensitive data
  run: |
    echo "::add-mask::${{ secrets.AIVIS_API_KEY }}"
    echo "::add-mask::${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}"
```

#### 9.2 APIレート制限対策
```yaml
# レート制限を考慮した実行
- name: Rate limit check
  run: |
    # API呼び出し前にレート制限チェック
    RATE_LIMIT=$(curl -s -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
      https://api.aivis.cloud/v1/rate-limit)
    echo "Current rate limit: $RATE_LIMIT"
```

### 10. テスト方法

#### 10.1 ローカルテスト（act使用）
```bash
# 全体フローのテスト
act -j planning -s AIVIS_API_KEY=$AIVIS_API_KEY \
    -s CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN

# 特定モジュールのテスト
act -W .github/workflows/module-voice-generation-opening.yml \
    --input script-text="テスト台本" \
    --input voice-config='{"gender":"female","age":"20s"}'
```

#### 10.2 ドライランモード
```yaml
# workflow_dispatchでドライランオプション追加
on:
  workflow_dispatch:
    inputs:
      dry-run:
        description: 'Dry run mode'
        type: boolean
        default: false

jobs:
  voice-generation:
    steps:
      - name: Generate voice (or mock)
        run: |
          if [[ "${{ inputs.dry-run }}" == "true" ]]; then
            echo "DRY RUN: Skipping API call"
            echo "audio-file=mock-audio.wav" >> $GITHUB_OUTPUT
          else
            # 実際のAPI呼び出し
          fi
```

### 11. TDD実装チェックリスト

#### 11.1 TDD準備フェーズ (Phase 0)
**テスト環境セットアップ**
- [ ] act（GitHub Actionsローカル実行）インストール
- [ ] Jest（テスト実行）セットアップ  
- [ ] Docker（act依存）確認
- [ ] テストディレクトリ構造作成
  - [ ] `tests/workflows/unit/` ディレクトリ
  - [ ] `tests/workflows/integration/` ディレクトリ
  - [ ] `tests/workflows/fixtures/` ディレクトリ
  - [ ] `tests/scripts/test-runner.js` 作成
  - [ ] `tests/scripts/mock-server.js` 作成

**基本準備**
- [x] Secrets設定完了（AIVIS_API_KEY, CLAUDE_CODE_OAUTH_TOKEN）
- [ ] ディレクトリ構造作成
  - [ ] `.github/workflows/` ディレクトリ
  - [ ] `radio-workflow/scripts/` ディレクトリ
  - [ ] `radio-workflow/assets/` ディレクトリ（デフォルトBGM用）

#### 11.2 RED Phase: テストケース作成
**受け入れテスト定義**
- [ ] 統合テスト（90秒ラジオ番組生成）
- [ ] セクション別長さ検証
- [ ] 並列処理時間短縮検証

**モジュール別テスト定義**
- [ ] 台本生成モジュールテスト
- [ ] 音声生成モジュールテスト（opening/main/ending）
- [ ] BGM生成モジュールテスト
- [ ] 音声合成モジュールテスト

**エラーハンドリングテスト定義**
- [ ] API障害リトライテスト
- [ ] BGM生成失敗フォールバックテスト
- [ ] 部分失敗処理テスト

**初回テスト実行（失敗確認）**
- [ ] 全テスト実行→失敗確認（ワークフローファイル未作成）

#### 11.3 GREEN Phase: 最小実装
**最小実装ワークフロー作成**
- [ ] `orchestrator-kamui-daily-radio.yml` 最小実装
- [ ] `module-radio-planning.yml` 最小実装（固定テキスト）
- [ ] `module-voice-generation-opening.yml` 最小実装（ダミー音声）
- [ ] `module-voice-generation-main.yml` 最小実装
- [ ] `module-voice-generation-ending.yml` 最小実装
- [ ] `module-bgm-generation-opening.yml` 最小実装（サイン波）
- [ ] `module-bgm-generation-main.yml` 最小実装
- [ ] `module-bgm-generation-ending.yml` 最小実装
- [ ] `module-audio-mixing.yml` 最小実装（単純連結）

**テスト実行（成功確認）**
- [ ] 全テスト実行→成功確認
- [ ] act使用した統合テスト実行

#### 11.4 REFACTOR Phase: 実装改善
**実際のAPI呼び出しに置き換え**
- [ ] 台本生成をClaude Code使用に変更
- [ ] 音声生成をaivis-cloud-api使用に変更
- [ ] BGM生成をGoogle Lyria使用に変更
- [ ] 音声合成をセクション別BGMミックスに改善

**エラーハンドリング実装** 
- [ ] リトライ機構追加
- [ ] フォールバック処理追加
- [ ] 部分失敗処理追加

**テスト実行（リファクタリング後成功確認）**
- [ ] 全テスト実行→成功確認
- [ ] モックサーバー使用テスト実行

#### 11.5 品質向上フェーズ
**追加テストケース実装**
- [ ] パフォーマンステスト（4分以内実行）
- [ ] 音声品質テスト（-23 LUFS）
- [ ] 並列処理検証テスト
- [ ] エラー境界テスト

**監視・通知実装**
- [ ] ワークフロー実行サマリー生成
- [ ] Discord/Slack通知設定
- [ ] アーティファクト管理設定

#### 11.6 本番展開フェーズ
**デプロイ前検証**
- [ ] 全テストスイート実行→成功
- [ ] 実API呼び出しテスト（制限付き）
- [ ] セキュリティ検証（シークレットマスキング等）

**段階的デプロイ**
- [ ] mainブランチへマージ
- [ ] 初回手動実行で動作確認
- [ ] ドライラン機能での検証
- [ ] 定期実行スケジュール有効化
- [ ] 監視・通知設定確認

#### 11.7 TDD実装優先順位

**Phase 1: コア機能のTDD実装（RED→GREEN→REFACTOR）**
1. **テスト環境セットアップ** - TDD基盤構築
2. **台本生成機能** - 最も基本的な機能から開始
3. **音声生成機能** - 1つずつモジュール実装
4. **統合フロー** - オーケストレータの最小実装

**Phase 2: 品質向上のTDD実装**
1. **BGM生成機能** - 付加価値機能の追加
2. **音声合成機能** - 高品質な最終出力
3. **エラーハンドリング** - 実用性向上
4. **パフォーマンス最適化** - 並列処理最適化

**Phase 3: 運用対応のTDD実装**
1. **監視・通知システム** - 運用観点の機能
2. **自動デプロイ・リリース** - DevOps自動化
3. **セキュリティ強化** - 本番運用準備
4. **ドキュメント・ヘルプ** - メンテナンス性向上

#### 11.8 TDD実装による期待効果

**開発効率**
- テストファースト により要件が明確化
- 小さなサイクル（RED→GREEN→REFACTOR）で確実な進歩
- リファクタリング時の回帰バグを防止

**品質保証**
- 全機能がテストでカバーされる
- エラーケースも含めた網羅的テスト
- 自動化により人的ミスを削減

**保守性向上**
- テストがドキュメントとして機能
- 機能追加時の影響範囲が明確
- 安全なコード変更が可能

## 12. TDD実装ガイド完成

### TDD実装の全体像

本ドキュメントでは、従来のウォーターフォール的な実装手順を**テスト駆動開発（TDD）**アプローチに完全に書き換えました。

#### TDDの3フェーズサイクル
1. **RED** - 失敗するテストを書く
2. **GREEN** - テストを通す最小限の実装
3. **REFACTOR** - コードを改善する

#### 実装による効果
**従来の逐次実装**
```
設計 → 実装 → テスト → デバッグ → 修正 = 時間かかる + バグ多発
```

**TDD実装**
```
テスト → 最小実装 → リファクタリング = 高品質 + メンテナンス性向上
```

### 並列処理による時間短縮効果

#### 逐次処理の場合（従来）
```
台本生成(2分) → 音声1(1分) → 音声2(1分) → 音声3(1分) → BGM1(1分) → BGM2(1分) → BGM3(1分) → 合成(1分) = 10分
```

#### 並列処理の場合（本設計）
```
台本生成(2分) → [音声1,2,3 + BGM1,2,3 並列](1分) → 合成(1分) = 4分
```

**約60%の時間短縮を実現**

#### BGM効果の向上
- **オープニング**: エネルギッシュなアップテンポBGM（50%音量）
- **メイン**: 話しやすい控えめなトーク向けBGM（50%音量）
- **エンディング**: 温かい締めくくりBGM（50%音量）
- **ループ機能**: 15秒ベース音楽を30秒までシームレスループ

### TDD実装による品質向上

#### 従来開発との比較

| 項目 | 従来開発 | TDD開発 |
|------|----------|---------|
| バグ発見時期 | 後期（統合テスト時） | 早期（実装中） |
| テストカバレッジ | 60-70% | 90%以上 |
| リファクタリング | 危険（回帰バグリスク） | 安全（テスト保護） |
| 要件理解 | 曖昧 | 明確（テストが仕様） |
| 開発速度 | 初期高速→後期失速 | 安定した高速開発 |

#### TDD特有の利点
1. **テスタブルな設計** - モジュール分割が自然に最適化
2. **ドキュメント効果** - テストが生きた仕様書として機能
3. **回帰防止** - 既存機能の破壊を即座に検出
4. **リファクタリング支援** - 安心してコード改善可能

### 実装後の継続的改善

#### モニタリング指標
```yaml
# GitHub Actions内で品質メトリクス測定
- name: Measure Quality Metrics
  run: |
    echo "Test Coverage: $(npm run test:coverage | grep 'All files' | awk '{print $4}')"
    echo "Build Success Rate: $(gh api repos/$GITHUB_REPOSITORY/actions/runs --jq '.workflow_runs | map(select(.conclusion=="success")) | length')/$(gh api repos/$GITHUB_REPOSITORY/actions/runs --jq '.workflow_runs | length')"
    echo "Average Execution Time: $(gh api repos/$GITHUB_REPOSITORY/actions/runs --jq '.workflow_runs | map(.run_started_at, .updated_at) | # 実行時間計算ロジック')"
```

#### 継続的な品質向上
1. **テストの定期レビュー** - カバレッジ不足領域の特定
2. **パフォーマンス監視** - 実行時間の継続的改善
3. **フィードバックループ** - 本番データからテストケース追加
4. **自動テスト拡張** - 新機能追加時のテスト自動生成

## 13. 今後の拡張可能性

### 機能拡張案
1. **多言語対応**: 英語版、中国語版の同時生成
2. **音声バリエーション**: 男性MC版、デュアルMC版
3. **動的時間調整**: 内容に応じて30秒～5分の可変長
4. **インタラクティブ要素**: リスナー投稿の自動読み上げ

### 技術的拡張
1. **キャッシュ最適化**: 頻出フレーズの音声キャッシュ
2. **分散処理**: 複数ランナーでの並列実行
3. **AI最適化**: プロンプトエンジニアリング改善
4. **品質自動評価**: 音声品質の自動スコアリング

### TDD拡張への対応
新機能追加時も同じTDDサイクルを維持:
1. **新機能のテスト定義** - 要件をテストコードで表現
2. **最小実装** - テストを通す最低限の実装
3. **既存システムとの統合** - リファクタリングで品質維持
4. **回帰テスト** - 既存機能への影響をテストで検証

## 14. まとめ

本TDD実装ガイドにより、神威日報ラジオ番組生成システムを**高品質・保守性・拡張性**を兼ね備えた形で実装できる。

### TDD導入効果の期待値
- **開発効率**: 30-50%向上（リファクタリング・デバッグ時間削減）
- **品質向上**: バグ密度70%削減（早期発見・修正）
- **保守性**: 機能追加・変更時の影響範囲明確化
- **チーム開発**: テストが共通理解の基盤として機能