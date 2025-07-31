# 神威日報ラジオ番組 GitHub Actions 実装手順

## 概要
神威日報の更新を検知し、自動的にラジオ番組を制作・配信するGitHub Actionsワークフローの実装手順です。

## 実装ステップ

### 1. 事前準備

#### 1.1 必要なシークレット設定
```
Repository Settings > Secrets and variables > Actions
```
- `AIVIS_API_KEY` - aivis-cloud-api認証キー（設定済み）
- `CLAUDE_CODE_OAUTH_TOKEN` - Claude Code認証トークン（設定済み）

#### 1.2 ディレクトリ構造準備
```
.github/
  workflows/
    kamui-daily-radio.yml
radio-workflow/
  scripts/
    generate-radio.js
  templates/
    script-template.json
  output/
    [生成されたファイル]
```

### 2. ワークフロー設計

#### 2.1 トリガー設定
- **定期実行**: 毎日特定時刻（例: 朝7時）
- **手動実行**: workflow_dispatch
- **プッシュ時**: 神威日報更新時

#### 2.2 ワークフローアーキテクチャ（ジョブ分割）

##### オーケストレータワークフロー
`orchestrator-kamui-daily-radio.yml` - メインの統合ワークフロー

##### モジュールワークフロー（並列処理対応）
1. **radio-planning** - 番組企画・台本生成
2. **voice-opening** - オープニング音声生成（並列）
3. **voice-main** - メイン音声生成（並列）
4. **voice-ending** - エンディング音声生成（並列）
5. **bgm-opening** - オープニングBGM生成（並列）
6. **bgm-main** - メインBGM生成（並列）
7. **bgm-ending** - エンディングBGM生成（並列）
8. **audio-mixing** - セクション別音声合成・最終統合

#### 2.3 ジョブ依存関係と並列処理

```
┌─────────────────┐
│  radio-planning │ （台本生成）
└────────┬────────┘
         │ outputs: script-data
    ┌────┴─────┬─────────┬─────────┬─────────┬─────────┬─────────┐
    ▼          ▼         ▼         ▼         ▼         ▼         ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│voice    ││voice    ││voice    ││bgm      ││bgm      ││bgm      │ ← 6並列実行
│opening  ││main     ││ending   ││opening  ││main     ││ending   │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
     │          │         │         │         │         │
     └──────────┴─────────┴─────────┴─────────┴─────────┘
                                    │
                                    ▼
                            ┌─────────────┐
                            │audio-mixing │ （セクション別合成）
                            └─────────────┘
```

### 3. 各モジュールの詳細実装

#### 3.1 radio-planning モジュール
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

#### 3.2 voice-generation-* モジュール（並列実行）
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

#### 3.3 bgm-generation-* モジュール（セクション別並列実行）
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

# module-bgm-generation-main.yml
name: BGM Generation Main
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
      
      - name: Generate Main BGM with Google Lyria
        id: bgm
        env:
          ANTHROPIC_API_KEY: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          # メインBGM生成（30秒、落ち着いたトーク向け）
          npx @anthropic-ai/claude-code \
            --mcp .claude/mcp-kamuicode.json \
            -c "
            kamuicodeを使って以下のメインBGMを生成してください：
            
            【BGM要件】
            - 長さ: 15秒（ループ用ベース音楽）
            - スタイル: 落ち着いたトーク系、情報番組向け
            - 雰囲気: 親しみやすく、話が聞きやすい控えめなBGM
            - 楽器: ソフトシンセ、軽いパーカッション、アンビエント
            - 特徴: ループしやすい構成、話の邪魔にならない音量バランス
            
            【生成設定】
            - モデル: Google Lyria (msc-google-lyria)
            - 品質: 高品質
            - フォーマット: WAV
            
            生成されたBGMのURLとファイルパスを出力してください。
            " > bgm-main-result.txt
          
          # 結果からURLとファイルパスを抽出
          MUSIC_URL=$(grep -oP 'https://[^\s]+\.wav' bgm-main-result.txt | head -1)
          MUSIC_FILE="bgm-main.wav"
          
          # URLからファイルをダウンロード
          if [ ! -z "$MUSIC_URL" ]; then
            curl -L "$MUSIC_URL" -o "$MUSIC_FILE"
            # 30秒までループ拡張（音声品質統一）
            ffmpeg -stream_loop -1 -i "$MUSIC_FILE" -t 30 -ar 44100 -ac 2 -c:a pcm_s16le "bgm-main-30s.wav"
            echo "music-url=$MUSIC_URL" >> $GITHUB_OUTPUT
            echo "music-file=bgm-main-30s.wav" >> $GITHUB_OUTPUT
          else
            echo "::error::メインBGM生成に失敗しました"
            exit 1
          fi

# module-bgm-generation-ending.yml
name: BGM Generation Ending
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
      
      - name: Generate Ending BGM with Google Lyria
        id: bgm
        env:
          ANTHROPIC_API_KEY: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          # エンディングBGM生成（30秒、温かい締めくくり）
          npx @anthropic-ai/claude-code \
            --mcp .claude/mcp-kamuicode.json \
            -c "
            kamuicodeを使って以下のエンディングBGMを生成してください：
            
            【BGM要件】
            - 長さ: 15秒（ループ用ベース音楽）
            - スタイル: 温かいエンディング系、番組締めくくり向け
            - 雰囲気: 親しみやすく、また明日も聞きたくなる温かさ
            - 楽器: アコースティックギター、ソフトピアノ、軽いストリングス
            - 特徴: ループしやすい構成、余韻が残る自然なフェード感
            
            【生成設定】
            - モデル: Google Lyria (msc-google-lyria)
            - 品質: 高品質
            - フォーマット: WAV
            
            生成されたBGMのURLとファイルパスを出力してください。
            " > bgm-ending-result.txt
          
          # 結果からURLとファイルパスを抽出
          MUSIC_URL=$(grep -oP 'https://[^\s]+\.wav' bgm-ending-result.txt | head -1)
          MUSIC_FILE="bgm-ending.wav"
          
          # URLからファイルをダウンロード
          if [ ! -z "$MUSIC_URL" ]; then
            curl -L "$MUSIC_URL" -o "$MUSIC_FILE"
            # 30秒までループ拡張（音声品質統一）
            ffmpeg -stream_loop -1 -i "$MUSIC_FILE" -t 30 -ar 44100 -ac 2 -c:a pcm_s16le "bgm-ending-30s.wav"
            echo "music-url=$MUSIC_URL" >> $GITHUB_OUTPUT
            echo "music-file=bgm-ending-30s.wav" >> $GITHUB_OUTPUT
          else
            echo "::error::エンディングBGM生成に失敗しました"
            exit 1
          fi
```

#### 3.4 audio-mixing モジュール
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

### 4. オーケストレータワークフローの実装

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

### 5. エラーハンドリング

#### 5.1 リトライ設定
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

#### 5.2 フォールバック処理
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

#### 5.3 部分的成功の処理
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

### 6. 環境変数設定

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

### 7. 成果物管理

#### 7.1 アーティファクト保存
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

#### 7.2 リリース作成
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

### 8. モニタリング・通知

#### 8.1 ワークフロー実行サマリー
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

#### 8.2 通知設定
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

### 9. セキュリティ考慮事項

#### 9.1 シークレット管理
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

#### 9.2 APIレート制限対策
```yaml
# レート制限を考慮した実行
- name: Rate limit check
  run: |
    # API呼び出し前にレート制限チェック
    RATE_LIMIT=$(curl -s -H "Authorization: Bearer ${{ secrets.AIVIS_API_KEY }}" \
      https://api.aivis.cloud/v1/rate-limit)
    echo "Current rate limit: $RATE_LIMIT"
```

### 10. テスト方法

#### 10.1 ローカルテスト（act使用）
```bash
# 全体フローのテスト
act -j planning -s AIVIS_API_KEY=$AIVIS_API_KEY \
    -s CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN

# 特定モジュールのテスト
act -W .github/workflows/module-voice-generation-opening.yml \
    --input script-text="テスト台本" \
    --input voice-config='{"gender":"female","age":"20s"}'
```

#### 10.2 ドライランモード
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

### 11. 実装チェックリスト

#### 11.1 準備フェーズ
- [x] Secrets設定完了（AIVIS_API_KEY, CLAUDE_CODE_OAUTH_TOKEN）
- [ ] ディレクトリ構造作成
  - [ ] `.github/workflows/` ディレクトリ
  - [ ] `radio-workflow/scripts/` ディレクトリ
  - [ ] `radio-workflow/assets/` ディレクトリ（デフォルトBGM用）

#### 11.2 モジュール実装
- [ ] `orchestrator-kamui-daily-radio.yml` 作成
- [ ] `module-radio-planning.yml` 作成
- [ ] `module-voice-generation-opening.yml` 作成
- [ ] `module-voice-generation-main.yml` 作成
- [ ] `module-voice-generation-ending.yml` 作成
- [ ] `module-bgm-generation.yml` 作成
- [ ] `module-audio-mixing.yml` 作成

#### 11.3 スクリプト実装
- [ ] aivis-cloud-api呼び出しスクリプト
- [ ] FFmpeg音声合成スクリプト
- [ ] メタデータ生成スクリプト

#### 11.4 テスト・検証
- [ ] 各モジュール単体テスト
- [ ] 統合フローテスト（ドライラン）
- [ ] 実API呼び出しテスト
- [ ] エラーハンドリング検証

#### 11.5 本番展開
- [ ] mainブランチへマージ
- [ ] 初回手動実行で動作確認
- [ ] 定期実行スケジュール有効化
- [ ] 監視・通知設定確認

## 12. 実装優先順位

### Phase 1: 基本機能実装（MVP）
1. **orchestrator-kamui-daily-radio.yml** - メインワークフロー
2. **module-radio-planning.yml** - 台本生成（Claude Code使用）
3. **module-voice-generation-*.yml** - 音声生成（aivis-cloud-api）
4. **module-audio-mixing.yml** - 基本的な音声結合

### Phase 2: 品質向上
1. **module-bgm-generation.yml** - BGM追加
2. エラーハンドリング強化
3. リトライ機構実装
4. 音声品質調整（-23 LUFS）

### Phase 3: 運用最適化
1. 監視・通知システム
2. アーティファクト管理
3. リリース自動化
4. パフォーマンス最適化

## 13. 並列処理による時間短縮効果

### 逐次処理の場合（従来）
```
台本生成(2分) → 音声1(1分) → 音声2(1分) → 音声3(1分) → BGM1(1分) → BGM2(1分) → BGM3(1分) → 合成(1分) = 10分
```

### 並列処理の場合（本設計）
```
台本生成(2分) → [音声1,2,3 + BGM1,2,3 並列](1分) → 合成(1分) = 4分
```

**約60%の時間短縮を実現**

### BGM効果の向上
- **オープニング**: エネルギッシュなアップテンポBGM（50%音量）
- **メイン**: 話しやすい控えめなトーク向けBGM（50%音量）
- **エンディング**: 温かい締めくくりBGM（50%音量）
- **ループ機能**: 15秒ベース音楽を30秒までシームレスループ

## 14. 今後の拡張可能性

### 機能拡張案
1. **多言語対応**: 英語版、中国語版の同時生成
2. **音声バリエーション**: 男性MC版、デュアルMC版
3. **動的時間調整**: 内容に応じて30秒～5分の可変長
4. **インタラクティブ要素**: リスナー投稿の自動読み上げ

### 技術的拡張
1. **キャッシュ最適化**: 頻出フレーズの音声キャッシュ
2. **分散処理**: 複数ランナーでの並列実行
3. **AI最適化**: プロンプトエンジニアリング改善
4. **品質自動評価**: 音声品質の自動スコアリング