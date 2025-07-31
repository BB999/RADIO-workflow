# Aivis Cloud API Documentation

## 概要

Aivis Cloud API は、高品質な AI 音声合成を提供するクラウド API サービスです。リアルタイムストリーミング対応で、業界最速クラスの音声生成を実現します。

### 主な特徴
- ⚡ 高速音声生成：15文字を0.3秒以下、230文字を0.7秒以下で生成
- 🎧 リアルタイムストリーミング：生成と同時に音声データを配信
- 🎯 SSML対応：細かな音声制御が可能
- 🌐 ブラウザ直接対応：CORS対応でフロントエンドから直接利用可能

### リンク
- [Redoc](https://api.aivis-project.com/docs): 美しく整理された API 仕様書
- [Swagger UI](https://api.aivis-project.com/docs/swagger): インタラクティブな API Playground
- [リアルタイム音声合成デモ](https://api.aivis-project.com/demo): ストリーミング生成をリアルタイムで体験
- [AivisHub](https://aivishub.com): AI 音声合成モデルの共有プラットフォーム
- [Aivis Project 公式サイト](https://aivis-project.com)

## API エンドポイント

### ベース URL
```
https://api.aivis-project.com/v1
```

## 認証

すべての API リクエストには API キーが必要です。

```
Authorization: Bearer YOUR_API_KEY
```

API キーは [Aivis Cloud API ダッシュボード](https://api.aivis-project.com/dashboard) から取得できます。

## Text-to-Speech API

### POST /tts/synthesize

テキストから音声を合成します。

#### 最小限のリクエスト例

```json
{
    "model_uuid": "a59cb814-0083-4369-8542-f51a29e72af7",
    "text": "こんにちは！"
}
```

#### 完全なリクエスト例

```json
{
    "model_uuid": "a59cb814-0083-4369-8542-f51a29e72af7",
    "text": "こんにちは！<break time=\"0.8s\"/>あらゆる現実を、すべて自分のほうへねじ曲げたのだ。",
    "use_ssml": true,
    "output_format": "mp3",
    "speaker_uuid": "optional-speaker-uuid",
    "style_id": 0,
    "emotional_intensity": 1.0,
    "speaking_rate": 1.0,
    "pitch": 0.0,
    "volume": 1.0,
    "tempo_dynamics": 1.0,
    "leading_silence_seconds": 0.1,
    "trailing_silence_seconds": 0.1,
    "line_break_silence_seconds": 0.4,
    "output_sampling_rate": 44100,
    "output_audio_channels": "mono",
    "output_bitrate": 128
}
```

### リクエストパラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|----------|---|-----|----------|------|
| model_uuid | string (UUID) | ✓ | - | 音声合成モデルのUUID |
| text | string | ✓ | - | 合成するテキスト |
| use_ssml | boolean | - | true | SSMLタグの解釈を有効化 |
| output_format | string | - | "mp3" | 出力形式: wav, flac, mp3, aac, opus |
| speaker_uuid | string (UUID) | - | - | 複数話者モデルでの話者UUID |
| style_id | integer | - | 0 | スタイルID (0-31) |
| style_name | string | - | - | スタイル名（style_idと併用不可） |
| emotional_intensity | number | - | 1.0 | 感情表現の強さ (0.0-2.0) |
| speaking_rate | number | - | 1.0 | 話速 (0.5-2.0) |
| pitch | number | - | 0.0 | ピッチ (-1.0-1.0) |
| volume | number | - | 1.0 | 音量 (0.0-2.0) |
| tempo_dynamics | number | - | 1.0 | テンポの緩急 (0.0-2.0) |
| leading_silence_seconds | number | - | 0.1 | 音声先頭の無音時間 |
| trailing_silence_seconds | number | - | 0.1 | 音声末尾の無音時間 |
| line_break_silence_seconds | number | - | 0.4 | 改行での無音時間 |
| output_sampling_rate | integer | - | 44100 | サンプリングレート (Hz) |
| output_audio_channels | string | - | "mono" | mono または stereo |
| output_bitrate | integer | - | 128 | ビットレート (kbps) |

### 音声形式の選択

| 形式 | Content-Type | 特徴 | 推奨用途 |
|-----|--------------|------|---------|
| wav | audio/wav | 無圧縮・最高音質 | 音質重視の用途 |
| flac | audio/flac | 可逆圧縮 | 高音質保存 |
| mp3 | audio/mpeg | 汎用性最高 | ブラウザリアルタイム再生 |
| aac | audio/aac | MP3より高圧縮率 | ファイルサイズ重視 |
| opus | audio/ogg | 最高圧縮効率 | 低遅延ストリーミング（iOS 18.4+） |

### レスポンスヘッダー

| ヘッダー | 説明 |
|---------|------|
| Content-Disposition | 推奨ファイル名 |
| X-Aivis-Billing-Mode | 課金モード（PayAsYouGo, Subscription） |
| X-Aivis-Character-Count | 使用文字数 |
| X-Aivis-Credits-Remaining | 残りクレジット（従量課金時） |
| X-Aivis-Credits-Used | 消費クレジット（従量課金時） |
| X-Aivis-Rate-Limit-Remaining | レート制限残り（定額プラン時） |

## SSML サポート

### 対応タグ

#### 1. break タグ（無音区間）
```xml
<break time="0.5s" />
<break time="500ms" />
<break strength="medium" />
```

#### 2. sub タグ（読み方指定）
```xml
<sub alias="ヤオヨロズ">八百万</sub>の神
<sub alias="World Wide Web Consortium">W3C</sub>
```

#### 3. prosody タグ（話速・ピッチ・音量）
```xml
<prosody rate="110%">速く話す</prosody>
<prosody pitch="+20%">高い声で</prosody>
<prosody volume="loud">大きな声で</prosody>
<prosody rate="90%" pitch="-10%" volume="soft">ゆっくり低く小さく</prosody>
```

#### 4. aivis:emotion タグ（感情表現）
```xml
<aivis:emotion style="Happy" intensity="1.5">嬉しいです！</aivis:emotion>
<aivis:emotion style="2" intensity="0.8">スタイルIDでも指定可能</aivis:emotion>
```

#### 5. p/s タグ（段落・文の区切り）
```xml
<p>これは段落です。</p>
<p>次の段落です。</p>
<s>これは文です。</s>
<s>次の文です。</s>
```

## ブラウザでのストリーミング再生例

```javascript
(async () => {
    const res = await fetch('https://api.aivis-project.com/v1/tts/synthesize', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer YOUR_API_KEY',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model_uuid: 'a59cb814-0083-4369-8542-f51a29e72af7',
            text: 'リアルタイムストリーミング音声合成のデモです。',
            output_format: 'mp3'
        })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    // MediaSource でストリーミング再生
    const mediaSource = self.MediaSource ? new self.MediaSource() : new self.ManagedMediaSource();
    const audio = new Audio(URL.createObjectURL(mediaSource));
    audio.play().catch(console.error);

    mediaSource.addEventListener('sourceopen', async () => {
        const sb = mediaSource.addSourceBuffer('audio/mpeg');
        const reader = res.body.getReader();

        const waitForIdle = () =>
            sb.updating ? new Promise(r => sb.addEventListener('updateend', r, {once: true})) : Promise.resolve();

        for (;;) {
            const { value, done } = await reader.read();
            if (done) {
                await waitForIdle();
                mediaSource.endOfStream();
                break;
            }
            await waitForIdle();
            sb.appendBuffer(value);
        }
    });
})();
```

## Models API

### GET /aivm-models/search

公開モデルを検索します。

#### クエリパラメータ
- `keyword`: 検索キーワード
- `tags[]`: タグフィルタ
- `categories[]`: カテゴリフィルタ
- `voice_timbres[]`: 声質フィルタ
- `license_types[]`: ライセンスタイプフィルタ
- `sort`: 並び順（download, like, recent）
- `page`: ページ番号
- `limit`: 取得件数（1-30）

### GET /aivm-models/{aivm_model_uuid}

指定モデルの詳細情報を取得します。

### GET /aivm-models/{aivm_model_uuid}/download

モデルファイルをダウンロードします。

#### クエリパラメータ
- `model_type`: AIVM または AIVMX

## Users API

### GET /users/me

ログイン中ユーザーの情報を取得します。

### GET /users/{handle}

指定ユーザーの公開情報を取得します。

## Payment API

### GET /payment/api-keys

API キー一覧を取得します。

### GET /payment/subscriptions

サブスクリプション一覧を取得します。

### GET /payment/usage-summary

API 使用量サマリーを取得します。

#### クエリパラメータ
- `start_date`: 開始日（YYYY-MM-DD）
- `end_date`: 終了日（YYYY-MM-DD）

## エラーレスポンス

```json
{
    "status_code": 422,
    "detail": "エラーの詳細"
}
```

## 注意事項

- モデルアップロード後、反映まで最大5分かかります
- 1行400文字を超える場合は自動分割されます
- SSMLタグで音声生成が分割されます
- ストリーミング時、最初のチャンクが`{`で始まる場合はエラーレスポンス

## 開発中の機能

- ユーザー辞書 API
- 読み/アクセント調整用 g2p API
- Python/JavaScript 公式クライアントライブラリ