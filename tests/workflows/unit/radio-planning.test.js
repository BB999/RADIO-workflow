const { runModule } = require('../../scripts/test-runner');

describe('Radio Planning Module', () => {
  test('入力から3つの台本セクションを生成する', async () => {
    // Red: まだワークフローが存在しないので失敗するはず
    const input = {
      'development-report': 'テスト用進捗報告',
      'topic-focus': 'テスト用トピック'
    };
    
    const result = await runModule('.github/workflows/module-radio-planning.yml', input);
    
    expect(result.outputs).toHaveProperty('script-opening');
    expect(result.outputs).toHaveProperty('script-main');
    expect(result.outputs).toHaveProperty('script-ending');
    expect(result.outputs).toHaveProperty('voice-config');
    
    // 各台本の長さが適切かチェック（現実的な最小値に調整）
    expect(result.outputs['script-opening'].length).toBeGreaterThan(20);
    expect(result.outputs['script-main'].length).toBeGreaterThan(20);
    expect(result.outputs['script-ending'].length).toBeGreaterThan(20);
  });

  test('台本の内容に入力データが反映される', async () => {
    const input = {
      'development-report': 'チャット機能の実装',
      'topic-focus': 'リアルタイム通信'
    };
    
    const result = await runModule('.github/workflows/module-radio-planning.yml', input);
    
    // 台本に入力内容が含まれることを確認
    expect(result.outputs['script-opening']).toContain('チャット機能');
    expect(result.outputs['script-main']).toContain('リアルタイム通信');
  });
});