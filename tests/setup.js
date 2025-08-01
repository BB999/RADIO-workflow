// Jest setup file
const path = require('path');

// テスト実行前の共通セットアップ
beforeAll(async () => {
  console.log('🎙️ ラジオワークフローTDDテスト開始');
  
  // 必要に応じてモックサーバーを起動
  if (process.env.START_MOCK_SERVER) {
    const mockServer = require('./scripts/mock-server');
    // モックサーバーの起動は別プロセスで実行することを推奨
  }
});

afterAll(async () => {
  console.log('🎙️ ラジオワークフローTDDテスト完了');
});

// 各テストケース前の共通処理
beforeEach(() => {
  // テストケースごとの初期化
});

afterEach(() => {
  // テストケースごとのクリーンアップ
});

// カスタムマッチャー（必要に応じて）
expect.extend({
  toBeValidAudioFile(received) {
    const pass = received && (received.endsWith('.wav') || received.endsWith('.mp3'));
    return {
      message: () => `expected ${received} to be a valid audio file`,
      pass
    };
  },
  
  toBeValidDuration(received, expected, tolerance = 5) {
    const pass = Math.abs(received - expected) <= tolerance;
    return {
      message: () => `expected ${received} to be within ${tolerance}s of ${expected}s`,
      pass
    };
  }
});