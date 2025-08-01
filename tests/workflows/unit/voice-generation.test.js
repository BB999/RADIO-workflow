const { runModule } = require('../../scripts/test-runner');

describe('Voice Generation Modules', () => {
  test('オープニング音声が生成される', async () => {
    const input = {
      'script-text': 'こんにちは、神威日報ラジオです！',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('.github/workflows/module-voice-generation-opening.yml', input);
    
    expect(result.outputs).toHaveProperty('audio-url');
    expect(result.outputs).toHaveProperty('audio-file');
    expect(result.outputs['audio-file']).toMatch(/\.wav$/);
  });

  test('メイン音声が生成される', async () => {
    const input = {
      'script-text': '本日の開発進捗をお伝えします。',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('.github/workflows/module-voice-generation-main.yml', input);
    
    expect(result.status).toBe('success');
    expect(result.outputs['audio-file']).toMatch(/\.wav$/);
  });

  test('エンディング音声が生成される', async () => {
    const input = {
      'script-text': 'それでは、また明日お会いしましょう！',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('.github/workflows/module-voice-generation-ending.yml', input);
    
    expect(result.status).toBe('success');
    expect(result.outputs['audio-file']).toMatch(/\.wav$/);
  });

  test('音声生成で適切な時間の音声が生成される', async () => {
    const input = {
      'script-text': 'テスト用の台本です。約30秒程度の音声が生成される予定です。',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('.github/workflows/module-voice-generation-opening.yml', input);
    
    expect(result.status).toBe('success');
    // 実際の音声時間は後で検証（今は構造チェックのみ）
    expect(result.outputs).toHaveProperty('audio-file');
  });
});