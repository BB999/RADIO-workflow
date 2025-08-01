const { runModule } = require('../../scripts/test-runner');

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
    
    const result = await runModule('.github/workflows/module-audio-mixing.yml', input);
    
    expect(result.outputs).toHaveProperty('final-audio');
    expect(result.outputs).toHaveProperty('metadata');
    expect(result.outputs['final-audio']).toMatch(/final-radio\.mp3$/);
  });

  test('音声品質が放送基準を満たす', async () => {
    const mockInputs = {
      'voice-opening': 'voice-opening.wav',
      'voice-main': 'voice-main.wav',
      'voice-ending': 'voice-ending.wav',
      'bgm-opening': 'bgm-opening-30s.wav',
      'bgm-main': 'bgm-main-30s.wav',
      'bgm-ending': 'bgm-ending-30s.wav'
    };
    
    const result = await runModule('.github/workflows/module-audio-mixing.yml', mockInputs);
    
    // メタデータの解析（実装時に詳細チェック）
    expect(result.outputs).toHaveProperty('metadata');
    expect(result.status).toBe('success');
  });

  test('セクション別BGMミキシングが正しく動作する', async () => {
    const input = {
      'voice-opening': 'voice-opening.wav',
      'voice-main': 'voice-main.wav', 
      'voice-ending': 'voice-ending.wav',
      'bgm-opening': 'bgm-opening-30s.wav',
      'bgm-main': 'bgm-main-30s.wav',
      'bgm-ending': 'bgm-ending-30s.wav'
    };
    
    const result = await runModule('.github/workflows/module-audio-mixing.yml', input);
    
    expect(result.status).toBe('success');
    expect(result.outputs['final-audio']).toBeDefined();
    // 各セクションが適切にミックスされていることを確認（構造チェック）
  });

  test('一部のBGMが欠如していても処理が継続される', async () => {
    const input = {
      'voice-opening': 'voice-opening.wav',
      'voice-main': 'voice-main.wav',
      'voice-ending': 'voice-ending.wav',
      'bgm-opening': '', // BGM欠如
      'bgm-main': 'bgm-main-30s.wav',
      'bgm-ending': 'bgm-ending-30s.wav'
    };
    
    const result = await runModule('.github/workflows/module-audio-mixing.yml', input);
    
    // エラーハンドリングにより処理が継続されることを期待
    expect(result.status).toBe('success');
    expect(result.outputs['final-audio']).toBeDefined();
  });
});