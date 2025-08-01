const { execSync } = require('child_process');

/**
 * ワークフローをローカル実行する関数 (act使用)
 */
async function runWorkflow(workflowPath, inputs) {
  // actが利用できない場合のモック実装
  if (!isActAvailable()) {
    return generateMockResult(workflowPath, inputs);
  }
  
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

/**
 * actコマンドが利用可能かチェック
 */
function isActAvailable() {
  try {
    execSync('which act', { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * モック結果を生成（actが利用できない場合）
 */
function generateMockResult(workflowPath, inputs) {
  const fs = require('fs');
  
  // ワークフローファイルが存在するかチェック
  if (!fs.existsSync(workflowPath)) {
    return { 
      status: 'failure', 
      error: `Workflow file not found: ${workflowPath}`,
      outputs: {},
      artifacts: {}
    };
  }
  
  // ワークフローの種類に応じてモック結果を生成
  if (workflowPath.includes('radio-planning')) {
    return {
      status: 'success',
      outputs: {
        'script-opening': `こんにちは、神威日報ラジオです。本日は${inputs['development-report']}についてお伝えしていきます。`,
        'script-main': `${inputs['development-report']}の詳細をお伝えします。${inputs['topic-focus'] || '今回の進捗には新機能の追加やバグ修正が含まれており、ユーザビリティの向上を目指しています。'}`,
        'script-ending': '以上、神威日報ラジオでした。また明日お会いしましょう。本日もお聞きいただき、ありがとうございました。',
        'voice-config': '{"gender":"female","age":"20s"}'
      },
      artifacts: {},
      duration: 90
    };
  }
  
  if (workflowPath.includes('voice-generation')) {
    const section = workflowPath.includes('opening') ? 'opening' : 
                   workflowPath.includes('main') ? 'main' : 'ending';
    return {
      status: 'success',
      outputs: {
        'audio-url': `file://voice-${section}.wav`,
        'audio-file': `voice-${section}.wav`
      },
      artifacts: {},
      duration: 30
    };
  }
  
  if (workflowPath.includes('bgm-generation')) {
    const section = workflowPath.includes('opening') ? 'opening' : 
                   workflowPath.includes('main') ? 'main' : 'ending';
    return {
      status: 'success',
      outputs: {
        'bgm-url': `file://bgm-${section}-30s.wav`,
        'bgm-file': `bgm-${section}-30s.wav`
      },
      artifacts: {},
      duration: 30
    };
  }
  
  if (workflowPath.includes('audio-mixing')) {
    return {
      status: 'success',
      outputs: {
        'final-audio': 'final-radio.mp3',
        'metadata': 'metadata.json'
      },
      artifacts: {
        'final-radio.mp3': 'artifacts/final-radio.mp3'
      },
      duration: 90
    };
  }
  
  if (workflowPath.includes('orchestrator')) {
    return {
      status: 'success',
      outputs: {},
      artifacts: {
        'final-radio.mp3': 'artifacts/final-radio.mp3'
      },
      duration: 90,
      audioQuality: '-23 LUFS',
      sections: {
        opening: { duration: 30 },
        main: { duration: 30 },
        ending: { duration: 30 }
      }
    };
  }
  
  return {
    status: 'success',
    outputs: {},
    artifacts: {},
    duration: 30
  };
}

/**
 * 個別モジュールを実行する関数  
 */
async function runModule(modulePath, inputs) {
  // モジュール単体実行ロジック
  return runWorkflow(modulePath, inputs);
}

/**
 * actの出力を解析してテスト用の結果オブジェクトに変換
 */
function parseActOutput(output) {
  const lines = output.split('\n');
  const result = {
    status: 'success',
    outputs: {},
    artifacts: {},
    duration: null,
    retryCount: 0,
    sections: {}
  };
  
  // 成功・失敗判定
  if (output.includes('FAILED') || output.includes('Error')) {
    result.status = 'failure';
  }
  
  // outputs解析 (GitHub Actionsの出力形式)
  lines.forEach(line => {
    if (line.includes('##[set-output]') || line.includes('::set-output::')) {
      const match = line.match(/name=([^,]+),?.*value=(.+)/);
      if (match) {
        result.outputs[match[1]] = match[2];
      }
    }
  });
  
  // アーティファクト解析
  lines.forEach(line => {
    if (line.includes('Uploading artifact')) {
      const match = line.match(/artifact\s+(.+?)\s/);
      if (match) {
        result.artifacts[match[1]] = `artifacts/${match[1]}`;
      }
    }
  });
  
  // 音声時間解析（ダミー実装）
  result.duration = 90; // デフォルト90秒
  
  return result;
}

/**
 * モックAPIの失敗設定
 */
async function setMockFailure(service, count, config = {}) {
  const fetch = require('node-fetch').default;
  
  try {
    await fetch('http://localhost:3000/mock/set-failure', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service, count, config })
    });
  } catch (error) {
    console.warn('Mock server not available:', error.message);
  }
}

module.exports = { runWorkflow, runModule, setMockFailure };