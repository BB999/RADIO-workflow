# 神威日報ラジオ番組 GitHub Actions TDD実装手順 - 第3部

**最小実装(GREEN Phase)と各モジュール詳細**

## 3. TDD Phase 2: 最小実装 (GREEN)

### 3.1 最小実装: テストが通るワークフロー作成

#### 3.1.1 台本生成モジュール（最小実装）
```yaml
# .github/workflows/module-radio-planning.yml
name: Radio Planning Module (Minimal)
on:
  workflow_call:
    inputs:
      development-report:
        required: true
        type: string
      topic-focus:
        required: false
        type: string
    outputs:
      script-opening:
        value: ${{ jobs.generate.outputs.script-opening }}
      script-main:
        value: ${{ jobs.generate.outputs.script-main }}
      script-ending:
        value: ${{ jobs.generate.outputs.script-ending }}
      voice-config:
        value: ${{ jobs.generate.outputs.voice-config }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      script-opening: ${{ steps.minimal.outputs.script-opening }}
      script-main: ${{ steps.minimal.outputs.script-main }}
      script-ending: ${{ steps.minimal.outputs.script-ending }}
      voice-config: ${{ steps.minimal.outputs.voice-config }}
    steps:
      # 最小実装: 固定テキストを返す（テストを通すため）
      - name: Generate minimal scripts
        id: minimal
        run: |
          echo "script-opening=こんにちは、神威日報ラジオです。本日は${{ inputs.development-report }}について" >> $GITHUB_OUTPUT
          echo "script-main=${{ inputs.development-report }}の詳細をお伝えします。${{ inputs.topic-focus || '' }}" >> $GITHUB_OUTPUT
          echo "script-ending=以上、神威日報ラジオでした。また明日お会いしましょう。" >> $GITHUB_OUTPUT
          echo 'voice-config={"gender":"female","age":"20s"}' >> $GITHUB_OUTPUT
```

テスト実行（GREEN確認）:
```bash
npm test -- --testPathPattern="radio-planning.test.js"
# Expected: テスト成功
```

#### 3.1.2 音声生成モジュール（最小実装）
```yaml
# .github/workflows/module-voice-generation-opening.yml
name: Voice Generation Opening (Minimal)
on:
  workflow_call:
    inputs:
      script-text:
        required: true
        type: string
      voice-config:
        required: true
        type: string
    outputs:
      audio-url:
        value: ${{ jobs.generate.outputs.url }}
      audio-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.minimal.outputs.audio-url }}
      file: ${{ steps.minimal.outputs.audio-file }}
    steps:
      # 最小実装: ダミー音声ファイルを作成
      - name: Generate minimal voice
        id: minimal
        run: |
          # 1秒の無音WAVファイルを生成
          sudo apt-get update && sudo apt-get install -y ffmpeg
          ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 30 -c:a pcm_s16le voice-opening.wav
          
          echo "audio-url=file://$(pwd)/voice-opening.wav" >> $GITHUB_OUTPUT
          echo "audio-file=voice-opening.wav" >> $GITHUB_OUTPUT
```

同様に `module-voice-generation-main.yml` と `module-voice-generation-ending.yml` も作成。

#### 3.1.3 BGM生成モジュール（最小実装）
```yaml
# .github/workflows/module-bgm-generation-opening.yml
name: BGM Generation Opening (Minimal)
on:
  workflow_call:
    outputs:
      bgm-url:
        value: ${{ jobs.generate.outputs.url }}
      bgm-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.minimal.outputs.bgm-url }}
      file: ${{ steps.minimal.outputs.bgm-file }}
    steps:
      # 最小実装: ダミーBGMファイルを生成
      - name: Generate minimal BGM
        id: minimal
        run: |
          sudo apt-get update && sudo apt-get install -y ffmpeg
          # 30秒の簡単なサイン波BGMを生成
          ffmpeg -f lavfi -i "sine=frequency=440:duration=30" -ar 44100 -ac 2 -c:a pcm_s16le bgm-opening-30s.wav
          
          echo "bgm-url=file://$(pwd)/bgm-opening-30s.wav" >> $GITHUB_OUTPUT
          echo "bgm-file=bgm-opening-30s.wav" >> $GITHUB_OUTPUT
```

#### 3.1.4 音声合成モジュール（最小実装）
```yaml
# .github/workflows/module-audio-mixing.yml
name: Audio Mixing Module (Minimal)
on:
  workflow_call:
    inputs:
      voice-opening:
        required: true
        type: string
      voice-main:
        required: true
        type: string
      voice-ending:
        required: true
        type: string
      bgm-opening:
        required: true
        type: string
      bgm-main:
        required: true
        type: string
      bgm-ending:
        required: true
        type: string
    outputs:
      final-audio:
        value: ${{ jobs.mix.outputs.url }}
      metadata:
        value: ${{ jobs.mix.outputs.metadata }}

jobs:
  mix:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.minimal.outputs.final-file }}
      metadata: ${{ steps.minimal.outputs.metadata }}
    steps:
      # 最小実装: ファイルを単純に連結
      - name: Minimal audio mixing
        id: minimal
        run: |
          sudo apt-get update && sudo apt-get install -y ffmpeg
          
          # ダミーファイルを作成（実際のファイルがない場合）
          for file in ${{ inputs.voice-opening }} ${{ inputs.voice-main }} ${{ inputs.voice-ending }}; do
            if [ ! -f "$file" ]; then
              ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 30 -c:a pcm_s16le "$file"
            fi
          done
          
          # 3つの音声を単純に連結
          ffmpeg -i ${{ inputs.voice-opening }} \
                 -i ${{ inputs.voice-main }} \
                 -i ${{ inputs.voice-ending }} \
                 -filter_complex "[0][1][2]concat=n=3:v=0:a=1" \
                 -c:a mp3 -b:a 320k final-radio.mp3
          
          # メタデータ生成
          echo '{"duration":"90s","audio_standard":"-23 LUFS","format":"MP3 320kbps"}' > metadata.json
          
          echo "final-file=final-radio.mp3" >> $GITHUB_OUTPUT
          echo "metadata=metadata.json" >> $GITHUB_OUTPUT
```

#### 3.1.5 オーケストレータワークフロー（最小実装）
```yaml
# .github/workflows/orchestrator-kamui-daily-radio.yml
name: Kamui Daily Radio Production (Minimal)
on:
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

  voice-opening:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-opening.yml
    with:
      script-text: ${{ needs.planning.outputs.script-opening }}
      voice-config: ${{ needs.planning.outputs.voice-config }}

  voice-main:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-main.yml
    with:
      script-text: ${{ needs.planning.outputs.script-main }}
      voice-config: ${{ needs.planning.outputs.voice-config }}

  voice-ending:
    needs: planning
    uses: ./.github/workflows/module-voice-generation-ending.yml
    with:
      script-text: ${{ needs.planning.outputs.script-ending }}
      voice-config: ${{ needs.planning.outputs.voice-config }}

  bgm-opening:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-opening.yml

  bgm-main:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-main.yml

  bgm-ending:
    needs: planning
    uses: ./.github/workflows/module-bgm-generation-ending.yml

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
```

### 3.2 初回テスト実行（GREEN確認）
```bash
# 全テストを実行
npm test

# 統合テストも実行
act workflow_dispatch -W .github/workflows/orchestrator-kamui-daily-radio.yml \
    --input development-report="TDDテスト用進捗" \
    --input topic-focus="テスト実装"
```

## 4. 各モジュールの詳細実装（リファクタリング後の最終形）

### 4.1 radio-planning モジュール
**役割**: ユーザー入力の内容から番組台本を生成

```yaml
# module-radio-planning.yml
name: Radio Planning Module
on:
  workflow_call:
    inputs:
      development-report:
        required: true
        type: string
        description: '神威アプリの開発進捗・最新情報'
      topic-focus:
        required: false
        type: string
        description: '特に強調したいトピック'
    outputs:
      script-opening:
        value: ${{ jobs.generate.outputs.script-opening }}
      script-main:
        value: ${{ jobs.generate.outputs.script-main }}
      script-ending:
        value: ${{ jobs.generate.outputs.script-ending }}
      voice-config:
        value: ${{ jobs.generate.outputs.voice-config }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      script-opening: ${{ steps.planning.outputs.script-opening }}
      script-main: ${{ steps.planning.outputs.script-main }}
      script-ending: ${{ steps.planning.outputs.script-ending }}
      voice-config: ${{ steps.planning.outputs.voice-config }}
    steps:
      - name: Generate radio scripts
        id: planning
        uses: docker://ghcr.io/anthropics/claude-code:latest
        with:
          api-key: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          command: |
            以下の内容で90秒のラジオ番組台本を生成してください：
            
            【開発進捗・最新情報】
            ${{ inputs.development-report }}
            
            【強調ポイント】
            ${{ inputs.topic-focus || 'なし' }}
            
            【要件】
            - オープニング: 30秒（明るい挨拶と今日のトピック紹介）
            - メイン: 30秒（内容を分かりやすく解説）
            - エンディング: 30秒（まとめと次回予告）
            - MC: 20代女性、明るく親しみやすい口調
            - ターゲット: 20-30代の技術に興味がある層
```

### 4.2 voice-generation-* モジュール（並列実行）
**役割**: 各セクションの音声を並列生成

```yaml
# module-voice-generation-opening.yml (main, endingも同様)
name: Voice Generation Opening
on:
  workflow_call:
    inputs:
      script-text:
        required: true
        type: string
      voice-config:
        required: true
        type: string
    outputs:
      audio-url:
        value: ${{ jobs.generate.outputs.url }}
      audio-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Generate voice with aivis-cloud-api
        run: |
          # aivis-cloud-api呼び出し
          curl -X POST https://api.aivis.cloud/v1/tts \
            -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "text": "${{ inputs.script-text }}",
              "voice": "female_20s_bright",
              "format": "wav"
            }'
```

### 4.3 bgm-generation-* モジュール（セクション別並列実行）
**役割**: セクション別BGM生成（Google Lyria使用）

```yaml
# module-bgm-generation-opening.yml
name: BGM Generation Opening
on:
  workflow_call:
    outputs:
      bgm-url:
        value: ${{ jobs.generate.outputs.url }}
      bgm-file:
        value: ${{ jobs.generate.outputs.file }}

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.bgm.outputs.music-url }}
      file: ${{ steps.bgm.outputs.music-file }}
    steps:
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Claude Code SDK
        run: npm install @anthropic-ai/claude-code
      
      - name: Generate Opening BGM with Google Lyria
        id: bgm
        env:
          ANTHROPIC_API_KEY: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          # オープニングBGM生成（30秒、アップテンポ）
          npx @anthropic-ai/claude-code \
            --mcp .claude/mcp-kamuicode.json \
            -c "
            kamuicodeを使って以下のオープニングBGMを生成してください：
            
            【BGM要件】
            - 長さ: 15秒（ループ用ベース音楽）
            - スタイル: 明るいオープニング系、アップテンポ
            - 雰囲気: エネルギッシュ、番組開始の盛り上がり
            - 楽器: シンセサイザー、軽快なドラム、ベース
            - 特徴: ループしやすい構成、始まりと終わりが自然に繋がる
            
            【生成設定】
            - モデル: Google Lyria (msc-google-lyria)
            - 品質: 高品質
            - フォーマット: WAV
            
            生成されたBGMのURLとファイルパスを出力してください。
            " > bgm-opening-result.txt
          
          # 結果からURLとファイルパスを抽出
          MUSIC_URL=$(grep -oP 'https://[^\s]+\.wav' bgm-opening-result.txt | head -1)
          MUSIC_FILE="bgm-opening.wav"
          
          # URLからファイルをダウンロード
          if [ ! -z "$MUSIC_URL" ]; then
            curl -L "$MUSIC_URL" -o "$MUSIC_FILE"
            # 30秒までループ拡張（音声品質統一）
            ffmpeg -stream_loop -1 -i "$MUSIC_FILE" -t 30 -ar 44100 -ac 2 -c:a pcm_s16le "bgm-opening-30s.wav"
            echo "music-url=$MUSIC_URL" >> $GITHUB_OUTPUT
            echo "music-file=bgm-opening-30s.wav" >> $GITHUB_OUTPUT
          else
            echo "::error::オープニングBGM生成に失敗しました"
            exit 1
          fi
```

### 4.4 audio-mixing モジュール
**役割**: 全音声と各セクション別BGMを合成し最終音声を生成

```yaml
# module-audio-mixing.yml
name: Audio Mixing Module
on:
  workflow_call:
    inputs:
      voice-opening:
        required: true
        type: string
      voice-main:
        required: true
        type: string
      voice-ending:
        required: true
        type: string
      bgm-opening:
        required: true
        type: string
      bgm-main:
        required: true
        type: string
      bgm-ending:
        required: true
        type: string
    outputs:
      final-audio:
        value: ${{ jobs.mix.outputs.url }}
      metadata:
        value: ${{ jobs.mix.outputs.metadata }}

jobs:
  mix:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.mixing.outputs.final-file }}
      metadata: ${{ steps.mixing.outputs.metadata }}
    steps:
      - name: Install FFmpeg
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
      
      - name: Mix audio files with section-specific BGMs
        id: mixing
        run: |
          # 各セクションで音声とBGMを個別にミックス（エラーハンドリング＋改善版）
          
          # 音声の長さを取得する関数（エラーハンドリング付き）
          get_duration() {
            local file="$1"
            if [ ! -f "$file" ]; then
              echo "::error::音声ファイルが見つかりません: $file"
              return 1
            fi
            local duration=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$file" 2>/dev/null)
            if [ -z "$duration" ] || [ "$duration" = "N/A" ]; then
              echo "::error::音声ファイルの長さを取得できません: $file"
              return 1
            fi
            echo "$duration"
          }
          
          # エラーハンドリング付きFFmpeg実行
          safe_ffmpeg() {
            if ! ffmpeg "$@" 2>/dev/null; then
              echo "::error::FFmpeg処理に失敗しました"
              exit 1
            fi
          }
          
          # オープニング: BGM4秒イントロ→音声開始→音声終了後BGMフェードアウト（2秒）
          VOICE_OPENING_DURATION=$(get_duration ${{ inputs.voice-opening }}) || exit 1
          FADE_START_OPENING=$(awk "BEGIN {print $VOICE_OPENING_DURATION + 4.5}")  # bcの代わりにawk使用
          TOTAL_OPENING_DURATION=$(awk "BEGIN {print $VOICE_OPENING_DURATION + 6.5}")
          
          safe_ffmpeg -i ${{ inputs.voice-opening }} \
                      -i ${{ inputs.bgm-opening }} \
                      -filter_complex "[0]adelay=4s:all=1[voice_delayed];
                                      [1]volume=0.5,afade=t=out:st=${FADE_START_OPENING}:d=2[bgm1];
                                      [voice_delayed][bgm1]amix=inputs=2[opening]" \
                      -map "[opening]" \
                      -t $TOTAL_OPENING_DURATION \
                      -ar 44100 -ac 2 -c:a pcm_s16le \
                      opening-mixed.wav
          
          # メイン: BGM4秒イントロ→音声開始→音声終了後BGMフェードアウト（2秒）
          VOICE_MAIN_DURATION=$(get_duration ${{ inputs.voice-main }}) || exit 1
          FADE_START_MAIN=$(awk "BEGIN {print $VOICE_MAIN_DURATION + 4.5}")
          TOTAL_MAIN_DURATION=$(awk "BEGIN {print $VOICE_MAIN_DURATION + 6.5}")
          
          safe_ffmpeg -i ${{ inputs.voice-main }} \
                      -i ${{ inputs.bgm-main }} \
                      -filter_complex "[0]adelay=4s:all=1[voice_delayed];
                                      [1]volume=0.5,afade=t=out:st=${FADE_START_MAIN}:d=2[bgm2];
                                      [voice_delayed][bgm2]amix=inputs=2[main]" \
                      -map "[main]" \
                      -t $TOTAL_MAIN_DURATION \
                      -ar 44100 -ac 2 -c:a pcm_s16le \
                      main-mixed.wav
          
          # エンディング: BGM4秒イントロ→音声開始→音声終了後BGMフェードアウト（3秒）
          VOICE_ENDING_DURATION=$(get_duration ${{ inputs.voice-ending }}) || exit 1
          FADE_START_ENDING=$(awk "BEGIN {print $VOICE_ENDING_DURATION + 4.5}")
          TOTAL_ENDING_DURATION=$(awk "BEGIN {print $VOICE_ENDING_DURATION + 7.5}")
          
          safe_ffmpeg -i ${{ inputs.voice-ending }} \
                      -i ${{ inputs.bgm-ending }} \
                      -filter_complex "[0]adelay=4s:all=1[voice_delayed];
                                      [1]volume=0.5,afade=t=out:st=${FADE_START_ENDING}:d=3[bgm3];
                                      [voice_delayed][bgm3]amix=inputs=2[ending]" \
                      -map "[ending]" \
                      -t $TOTAL_ENDING_DURATION \
                      -ar 44100 -ac 2 -c:a pcm_s16le \
                      ending-mixed.wav
          
          # 3つのセクションを連結し、最終調整（エラーハンドリング付き）
          safe_ffmpeg -i opening-mixed.wav \
                      -i main-mixed.wav \
                      -i ending-mixed.wav \
                      -filter_complex "[0][1][2]concat=n=3:v=0:a=1[combined]" \
                      -map "[combined]" \
                      -af "loudnorm=I=-23:LRA=7:TP=-1" \
                      -c:a mp3 \
                      -b:a 320k \
                      final-radio.mp3
          
          # メタデータ生成
          echo "{
            \"duration\": \"90s\",
            \"sections\": [
              {\"name\": \"opening\", \"duration\": \"4s intro + voice + 2.5s fade\", \"bgm\": \"upbeat\", \"bgm_volume\": \"50%\", \"intro\": \"4s\", \"fade_out\": \"2s\"},
              {\"name\": \"main\", \"duration\": \"4s intro + voice + 2.5s fade\", \"bgm\": \"talk-friendly\", \"bgm_volume\": \"50%\", \"intro\": \"4s\", \"fade_out\": \"2s\"},
              {\"name\": \"ending\", \"duration\": \"4s intro + voice + 3.5s fade\", \"bgm\": \"warm-outro\", \"bgm_volume\": \"50%\", \"intro\": \"4s\", \"fade_out\": \"3s\"}
            ],
            \"audio_standard\": \"-23 LUFS\",
            \"format\": \"MP3 320kbps\"
          }" > metadata.json
          
          echo "final-file=final-radio.mp3" >> $GITHUB_OUTPUT
          echo "metadata=metadata.json" >> $GITHUB_OUTPUT
```

---

**続きは第4部「リファクタリング・エラーハンドリング・運用」を参照**