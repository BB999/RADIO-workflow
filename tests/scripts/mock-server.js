const express = require('express');
const app = express();

app.use(express.json());

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
    duration: 30,
    status: 'success'
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
    duration: 15,
    status: 'success'
  });
});

// Claude Code モック
app.post('/claude/generate', (req, res) => {
  const shouldFail = failureCount['claude-code'] > 0;
  
  if (shouldFail) {
    failureCount['claude-code']--;
    return res.status(500).json({ error: 'Claude API error' });
  }
  
  // 台本生成レスポンス
  res.json({
    opening: 'こんにちは、神威日報ラジオです。本日は' + req.body.development_report + 'について',
    main: req.body.development_report + 'の詳細をお伝えします。' + (req.body.topic_focus || ''),
    ending: '以上、神威日報ラジオでした。また明日お会いしましょう。',
    voice_config: '{"gender":"female","age":"20s"}'
  });
});

// モック設定API
app.post('/mock/set-failure', (req, res) => {
  const { service, count, config } = req.body;
  failureCount[service] = count;
  failureConfig[service] = config || {};
  res.json({ success: true, service, count });
});

// モック状態確認API
app.get('/mock/status', (req, res) => {
  res.json({
    failureCount,
    failureConfig
  });
});

// 全リセットAPI
app.post('/mock/reset', (req, res) => {
  failureCount = {};
  failureConfig = {};
  res.json({ success: true, message: 'All mocks reset' });
});

const PORT = process.env.MOCK_PORT || 3000;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Mock server running on port ${PORT}`);
    console.log('Available endpoints:');
    console.log('  POST /v1/tts - aivis-cloud-api mock');
    console.log('  POST /music/generate - Google Lyria mock');
    console.log('  POST /claude/generate - Claude Code mock');
    console.log('  POST /mock/set-failure - Set failure simulation');
    console.log('  GET /mock/status - Check mock status');
    console.log('  POST /mock/reset - Reset all mocks');
  });
}

module.exports = app;