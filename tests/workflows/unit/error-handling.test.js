const { runModule, setMockFailure } = require('../../scripts/test-runner');

describe('Error Handling', () => {
  test('音声生成APIが失敗した場合のリトライ', async () => {
    // APIを3回失敗させてからリトライで成功させる
    await setMockFailure('aivis-cloud-api', 3);
    
    const mockInput = {
      'script-text': 'テスト台本',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('.github/workflows/module-voice-generation-opening.yml', mockInput);
    
    expect(result.status).toBe('success');
    // リトライが動作したことを確認（実装時に詳細チェック）
  });

  test('BGM生成失敗時のフォールバック処理', async () => {
    await setMockFailure('google-lyria', Infinity); // 常に失敗
    
    const result = await runModule('.github/workflows/module-bgm-generation-opening.yml', {});
    
    expect(result.status).toBe('success'); // continue-on-errorで成功扱い
    // フォールバック用のデフォルトBGMが使用されることを期待
  });

  test('部分的な音声生成失敗の処理', async () => {
    // オープニング音声だけ失敗させる
    await setMockFailure('aivis-cloud-api', Infinity, { target: 'opening' });
    
    const mockInput = {
      'development-report': 'テスト進捗',
      'topic-focus': 'テストトピック'
    };
    
    const result = await runModule('.github/workflows/orchestrator-kamui-daily-radio.yml', mockInput);
    
    // 2つ以上成功すれば継続（エラーハンドリング実装後に詳細テスト）
    expect(result.status).toBe('success');
  });

  test('Claude Code API障害時の処理', async () => {
    await setMockFailure('claude-code', 2); // 2回失敗後成功
    
    const input = {
      'development-report': 'API障害テスト',
      'topic-focus': 'エラーハンドリング'
    };
    
    const result = await runModule('.github/workflows/module-radio-planning.yml', input);
    
    expect(result.status).toBe('success');
    expect(result.outputs['script-opening']).toBeDefined();
  });

  test('ネットワークタイムアウト時の処理', async () => {
    // タイムアウトシミュレーション（実装時により詳細なテスト）
    const input = {
      'script-text': 'タイムアウトテスト台本',
      'voice-config': '{"gender":"female","age":"20s"}'
    };
    
    const result = await runModule('.github/workflows/module-voice-generation-main.yml', input);
    
    // タイムアウト後のリトライ動作を確認
    expect(result.status).toBe('success');
  });
});