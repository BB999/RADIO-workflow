# 神威日報ラジオ番組 GitHub Actions TDD実装手順 - 第2部

**TDDテストケース定義 (RED Phase)**

## 2. TDD Phase 1: テストケース定義 (RED)

### 2.1 受け入れテスト定義
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

### 2.2 各モジュールのテストケース定義

#### 2.2.1 台本生成モジュールテスト
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

#### 2.2.2 音声生成モジュールテスト
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

#### 2.2.3 BGM生成モジュールテスト
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

#### 2.2.4 音声合成モジュールテスト
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

### 2.3 エラーケースのテスト定義
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

### 2.4 テスト実行環境の準備
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

### 2.5 モックサーバーの準備
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

### 2.6 初回テスト実行（RED確認）
```bash
# テストを実行して失敗することを確認
npm test -- --testPathPattern="radio-planning.test.js"
# Expected: ワークフローファイルが存在しないためテスト失敗
```

---

**続きは第3部「最小実装(GREEN Phase)と各モジュール詳細」を参照**