const { runWorkflow } = require('../../scripts/test-runner');

describe('神威日報ラジオ自動生成ワークフロー', () => {
  const mockInput = {
    'development-report': 'ダークモード機能を追加しました',
    'topic-focus': 'UI/UX改善'
  };

  test('90秒のラジオ番組が正常に生成される', async () => {
    // Given: 神威日報の更新情報
    const input = {
      'development-report': 'ダークモード機能を追加しました',
      'topic-focus': 'UI/UX改善'
    };
    
    // When: ワークフローを実行
    const result = await runWorkflow('.github/workflows/orchestrator-kamui-daily-radio.yml', input);
    
    // Then: 期待する結果
    expect(result.status).toBe('success');
    expect(result.artifacts).toHaveProperty('final-radio.mp3');
    expect(result.duration).toBeCloseTo(90, 5); // 90秒±5秒
    expect(result.audioQuality).toBe('-23 LUFS');
  }, 300000); // 5分タイムアウト

  test('各セクションが正しい長さで生成される', async () => {
    const result = await runWorkflow('.github/workflows/orchestrator-kamui-daily-radio.yml', mockInput);
    
    expect(result.sections.opening.duration).toBeCloseTo(30, 3);
    expect(result.sections.main.duration).toBeCloseTo(30, 3);
    expect(result.sections.ending.duration).toBeCloseTo(30, 3);
  });

  test('並列処理により実行時間が短縮される', async () => {
    const startTime = Date.now();
    const result = await runWorkflow('.github/workflows/orchestrator-kamui-daily-radio.yml', mockInput);
    const executionTime = Date.now() - startTime;
    
    // 並列処理により4分以内で完了することを期待
    expect(executionTime).toBeLessThan(4 * 60 * 1000);
    expect(result.status).toBe('success');
  });
});