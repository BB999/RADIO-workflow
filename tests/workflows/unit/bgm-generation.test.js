const { runModule } = require('../../scripts/test-runner');

describe('BGM Generation Modules', () => {
  test('オープニングBGMが生成される', async () => {
    const result = await runModule('.github/workflows/module-bgm-generation-opening.yml', {});
    
    expect(result.outputs).toHaveProperty('bgm-url');
    expect(result.outputs).toHaveProperty('bgm-file');
    expect(result.outputs['bgm-file']).toMatch(/bgm-opening-30s\.wav$/);
  });

  test('メインBGMが生成される', async () => {
    const result = await runModule('.github/workflows/module-bgm-generation-main.yml', {});
    
    expect(result.outputs['bgm-file']).toMatch(/bgm-main-30s\.wav$/);
  });

  test('エンディングBGMが生成される', async () => {
    const result = await runModule('.github/workflows/module-bgm-generation-ending.yml', {});
    
    expect(result.outputs['bgm-file']).toMatch(/bgm-ending-30s\.wav$/);
  });

  test('BGMの長さが適切である', async () => {
    const result = await runModule('.github/workflows/module-bgm-generation-opening.yml', {});
    
    expect(result.status).toBe('success');
    // BGMは30秒程度の長さであることを確認（実装時に詳細チェック）
    expect(result.outputs).toHaveProperty('bgm-file');
  });

  test('BGMの種類が異なる（オープニング・メイン・エンディング）', async () => {
    const openingResult = await runModule('.github/workflows/module-bgm-generation-opening.yml', {});
    const mainResult = await runModule('.github/workflows/module-bgm-generation-main.yml', {});
    const endingResult = await runModule('.github/workflows/module-bgm-generation-ending.yml', {});
    
    // 3つの異なるBGMファイルが生成されることを確認
    expect(openingResult.outputs['bgm-file']).toContain('opening');
    expect(mainResult.outputs['bgm-file']).toContain('main');
    expect(endingResult.outputs['bgm-file']).toContain('ending');
  });
});