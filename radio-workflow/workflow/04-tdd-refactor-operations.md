# 神威日報ラジオ番組 GitHub Actions TDD実装手順 - 第4部

**リファクタリング・エラーハンドリング・運用**

## 4. TDD Phase 3: リファクタリング (REFACTOR)

### 4.1 実際のAPI呼び出しに置き換え

テストが通ることを確認後、実際のAPI呼び出しに置き換え:

#### 4.1.1 台本生成の実装改善
```yaml
# .github/workflows/module-radio-planning.yml (改善版)
- name: Generate radio scripts with Claude
  id: planning
  run: |
    # 元の固定テキストから Claude Code を使った動的生成に変更
    SCRIPT_RESULT=$(npx @anthropic-ai/claude-code -c "
    以下の内容で90秒のラジオ番組台本を生成してください：
    
    【開発進捗・最新情報】
    ${{ inputs.development-report }}
    
    【強調ポイント】
    ${{ inputs.topic-focus || 'なし' }}
    
    各セクション30秒、明るい20代女性MC、分かりやすい解説で。
    JSON形式で{ opening: '...', main: '...', ending: '...' }として出力。
    ")
    
    # JSONから各セクションを抽出
    echo "$SCRIPT_RESULT" | jq -r '.opening' | sed 's/^/script-opening=/' >> $GITHUB_OUTPUT
    echo "$SCRIPT_RESULT" | jq -r '.main' | sed 's/^/script-main=/' >> $GITHUB_OUTPUT
    echo "$SCRIPT_RESULT" | jq -r '.ending' | sed 's/^/script-ending=/' >> $GITHUB_OUTPUT
    echo 'voice-config={"gender":"female","age":"20s"}' >> $GITHUB_OUTPUT
```

#### 4.1.2 音声生成の実装改善
```yaml
# .github/workflows/module-voice-generation-opening.yml (改善版)
- name: Generate voice with aivis-cloud-api
  id: voice
  run: |
    # ダミー音声生成から実際のTTS APIに変更
    RESPONSE=$(curl -X POST https://api.aivis.cloud/v1/tts \
      -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
      -H "Content-Type: application/json" \
      -d '{
        "text": "${{ inputs.script-text }}",
        "voice": "female_20s_bright",
        "format": "wav"
      }')
    
    AUDIO_URL=$(echo "$RESPONSE" | jq -r '.audio_url')
    curl -L "$AUDIO_URL" -o voice-opening.wav
    
    echo "audio-url=$AUDIO_URL" >> $GITHUB_OUTPUT
    echo "audio-file=voice-opening.wav" >> $GITHUB_OUTPUT
```

#### 4.1.3 テスト実行（リファクタリング後）
```bash
# リファクタリング後もテストが成功することを確認
npm test

# 実際のAPI使用時のテスト（モックサーバー使用）
MOCK_API=true npm test
```

### 5. TDD エラーハンドリング実装

#### 5.1 エラーケーステスト（RED）
```javascript
// tests/workflows/unit/error-handling.test.js
test('音声生成API障害時のリトライ動作', async () => {
  // 3回失敗後に成功するよう設定
  await setMockFailure('aivis-cloud-api', 3);
  
  const result = await runModule('module-voice-generation-opening.yml', mockInput);
  
  expect(result.status).toBe('success');
  expect(result.retryAttempts).toBe(4); // 初回 + 3回リトライ
});
```

#### 5.2 リトライ機構実装（GREEN）
```yaml
# リトライ付き音声生成
- name: Generate voice with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 30
    command: |
      RESPONSE=$(curl -X POST https://api.aivis.cloud/v1/tts \
        -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
        -H "Content-Type: application/json" \
        -d '{
          "text": "${{ inputs.script-text }}",
          "voice": "female_20s_bright",
          "format": "wav"
        }')
      
      if [ "$(echo "$RESPONSE" | jq -r '.error')" != "null" ]; then
        echo "API Error: $(echo "$RESPONSE" | jq -r '.error')"
        exit 1
      fi
```

## 6. オーケストレータワークフローの実装

```yaml
# orchestrator-kamui-daily-radio.yml
name: Kamui Daily Radio Production
on:
  schedule:
    - cron: '0 22 * * *'  # 毎日朝7時（JST）
  workflow_dispatch:
    inputs:
      development-report:
        description: '神威アプリの開発進捗・最新情報'
        required: true
        type: string
      topic-focus:
        description: '特に強調したいトピック（オプション）'
        required: false
        type: string

jobs:
  planning:
    uses: ./.github/workflows/module-radio-planning.yml
    with:
      development-report: ${{ inputs.development-report }}
      topic-focus: ${{ inputs.topic-focus }}
    secrets: inherit

  voice-opening:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-opening.yml
    with:
      script-text: ${{ needs.planning.outputs.script-opening }}
      voice-config: ${{ needs.planning.outputs.voice-config }}
    secrets: inherit

  voice-main:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-main.yml
    with:
      script-text: ${{ needs.planning.outputs.script-main }}
      voice-config: ${{ needs.planning.outputs.voice-config }}
    secrets: inherit

  voice-ending:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-ending.yml
    with:
      script-text: ${{ needs.planning.outputs.script-ending }}
      voice-config: ${{ needs.planning.outputs.voice-config }}
    secrets: inherit

  bgm-opening:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-opening.yml
    secrets: inherit

  bgm-main:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-main.yml
    secrets: inherit

  bgm-ending:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-ending.yml
    secrets: inherit

  audio-mixing:
    needs: [voice-opening, voice-main, voice-ending, bgm-opening, bgm-main, bgm-ending]
    uses: ./.github/workflows/module-audio-mixing.yml
    with:
      voice-opening: ${{ needs.voice-opening.outputs.audio-file }}
      voice-main: ${{ needs.voice-main.outputs.audio-file }}
      voice-ending: ${{ needs.voice-ending.outputs.audio-file }}
      bgm-opening: ${{ needs.bgm-opening.outputs.bgm-file }}
      bgm-main: ${{ needs.bgm-main.outputs.bgm-file }}
      bgm-ending: ${{ needs.bgm-ending.outputs.bgm-file }}
    secrets: inherit

  publish:
    needs: audio-mixing
    runs-on: ubuntu-latest
    steps:
      - name: Create Release
        uses: actions/create-release@v1
        with:
          tag_name: radio-${{ github.run_id }}
          release_name: 神威日報ラジオ ${{ steps.date.outputs.date }}
          body: |
            ## 🎙️ 神威日報ラジオ
            
            自動生成された本日の番組です。
            
            - 時間: 90秒
            - MC: AI生成（20代女性）
            - 内容: 神威アプリ開発最新情報
```

## 7. エラーハンドリング

### 7.1 リトライ設定
```yaml
# 音声生成でのリトライ実装
- name: Generate voice with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 30
    command: |
      curl -X POST https://api.aivis.cloud/v1/tts \
        -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
        -H "Content-Type: application/json" \
        -d '{
          "text": "${{ inputs.script-text }}",
          "voice": "female_20s_bright",
          "format": "wav"
        }'
```

### 7.2 フォールバック処理
```yaml
# BGM生成失敗時のフォールバック
bgm-generation:
  continue-on-error: true  # 失敗しても続行

audio-mixing:
  if: always()  # BGM生成が失敗してもミキシング実行
  steps:
    - name: Check BGM availability
      run: |
        if [ -z "${{ needs.bgm-generation.outputs.bgm-file }}" ]; then
          echo "Using default BGM"
          echo "bgm-file=assets/default-bgm.mp3" >> $GITHUB_OUTPUT
        fi
```

### 7.3 部分的成功の処理
```yaml
# 一部の音声生成が失敗した場合
- name: Validate audio files
  run: |
    SUCCESS_COUNT=0
    [ -f "voice-opening.wav" ] && SUCCESS_COUNT=$((SUCCESS_COUNT+1))
    [ -f "voice-main.wav" ] && SUCCESS_COUNT=$((SUCCESS_COUNT+1))
    [ -f "voice-ending.wav" ] && SUCCESS_COUNT=$((SUCCESS_COUNT+1))
    
    if [ $SUCCESS_COUNT -lt 2 ]; then
      echo "::error::音声生成が不完全です"
      exit 1
    fi
```

## 8. 環境変数設定

```yaml
env:
  RADIO_DURATION: 90
  SECTION_DURATION: 30
  VOICE_GENDER: female
  VOICE_AGE: 20s
  VOICE_STYLE: bright_energetic
  OUTPUT_FORMAT: mp3
  LOUDNESS_TARGET: -23
```

## 9. 成果物管理

### 9.1 アーティファクト保存
```yaml
# 各音声ファイルを保存
- name: Upload voice artifacts
  uses: actions/upload-artifact@v3
  with:
    name: voice-files-${{ github.run_id }}
    path: |
      output/voice-opening.wav
      output/voice-main.wav
      output/voice-ending.wav
    retention-days: 30

# 最終音声を保存
- name: Upload final radio
  uses: actions/upload-artifact@v3
  with:
    name: radio-${{ github.run_id }}
    path: output/radio-final.mp3
    retention-days: 90
```

### 9.2 リリース作成
```yaml
- name: Create Release with audio
  uses: softprops/action-gh-release@v1
  with:
    tag_name: radio-${{ github.run_id }}
    name: 神威日報ラジオ - ${{ steps.date.outputs.date }}
    files: |
      output/radio-final.mp3
      output/metadata.json
    body: |
      ## 🎙️ 神威日報ラジオ
      
      ### 番組情報
      - 放送日: ${{ steps.date.outputs.date }}
      - 時間: 90秒
      - MC: AI生成（20代女性）
      
      ### 内容
      神威アプリの最新開発情報をお届けします。
```

## 10. モニタリング・通知

### 10.1 ワークフロー実行サマリー
```yaml
- name: Generate workflow summary
  if: always()
  run: |
    cat >> $GITHUB_STEP_SUMMARY << EOF
    ## 🎙️ ラジオ番組制作結果
    
    | ステップ | 状態 | 所要時間 |
    |---------|------|----------|
    | 台本生成 | ${{ needs.planning.result }} | ${{ needs.planning.outputs.duration }} |
    | 音声生成(開始) | ${{ needs.voice-opening.result }} | - |
    | 音声生成(本編) | ${{ needs.voice-main.result }} | - |
    | 音声生成(終了) | ${{ needs.voice-ending.result }} | - |
    | BGM生成 | ${{ needs.bgm-generation.result }} | - |
    | 音声合成 | ${{ needs.audio-mixing.result }} | - |
    
    ### 📊 統計情報
    - 総実行時間: ${{ steps.total-time.outputs.duration }}
    - 生成ファイルサイズ: ${{ steps.file-size.outputs.size }}
    - 音声品質: -23 LUFS (放送基準)
    EOF
```

### 10.2 通知設定
```yaml
# Discord/Slack通知
- name: Send notification
  if: success()
  env:
    WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK }}
  run: |
    curl -X POST $WEBHOOK_URL \
      -H "Content-Type: application/json" \
      -d '{
        "content": "🎙️ 神威日報ラジオが生成されました！",
        "embeds": [{
          "title": "番組リンク",
          "url": "${{ needs.publish.outputs.release-url }}",
          "color": 5814783
        }]
      }'
```

## 11. セキュリティ考慮事項

### 11.1 シークレット管理
```yaml
permissions:
  contents: write  # リリース作成に必要
  pull-requests: write  # PR作成に必要

# シークレットのマスキング
- name: Mask sensitive data
  run: |
    echo "::add-mask::${{ secrets.AIVIS_API_KEY }}"
    echo "::add-mask::${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}"
```

### 11.2 APIレート制限対策
```yaml
# レート制限を考慮した実行
- name: Rate limit check
  run: |
    # API呼び出し前にレート制限チェック
    RATE_LIMIT=$(curl -s -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
      https://api.aivis.cloud/v1/rate-limit)
    echo "Current rate limit: $RATE_LIMIT"
```

## 12. テスト方法

### 12.1 ローカルテスト（act使用）
```bash
# 全体フローのテスト
act -j planning -s AIVIS_API_KEY=$AIVIS_API_KEY \
    -s CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN

# 特定モジュールのテスト
act -W .github/workflows/module-voice-generation-opening.yml \
    --input script-text="テスト台本" \
    --input voice-config='{"gender":"female","age":"20s"}'
```

### 12.2 ドライランモード
```yaml
# workflow_dispatchでドライランオプション追加
on:
  workflow_dispatch:
    inputs:
      dry-run:
        description: 'Dry run mode'
        type: boolean
        default: false

jobs:
  voice-generation:
    steps:
      - name: Generate voice (or mock)
        run: |
          if [[ "${{ inputs.dry-run }}" == "true" ]]; then
            echo "DRY RUN: Skipping API call"
            echo "audio-file=mock-audio.wav" >> $GITHUB_OUTPUT
          else
            # 実際のAPI呼び出し
          fi
```

---

**続きは第5部「チェックリスト・品質管理・まとめ」を参照**