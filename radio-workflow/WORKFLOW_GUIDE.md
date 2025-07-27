# ラジオワークフロー実行ガイド

## 概要
このワークフローは「神威日報ふりかえりラジオ」を3つのパートに分けて制作します：
1. **オープニング** - 番組の挨拶（15-20秒）
2. **メインコンテンツ** - ニュース内容（30秒）
3. **完全版** - オープニング＋メインの結合

## ワークフローの実行手順

### 1. オープニング作成
```bash
# GitHub Actionsページで「Create Radio Opening」を選択
# 入力項目:
# - opening_theme: オープニングの雰囲気（例：エネルギッシュ、爽やか、ジャズ風）
```

**出力ファイル例:**
```
radio-opening-20250127-123456/
├── planning/
│   ├── opening-script.txt      # オープニング台本
│   ├── voice-style.json        # 音声スタイル設定
│   ├── music-prompt.txt        # 音楽生成プロンプト
│   └── opening-strategy.md     # 制作戦略
├── audio/
│   └── opening-voice.wav       # オープニング音声
├── music/
│   └── opening-music.wav       # オープニング音楽
└── final/
    └── final-opening-audio.wav # 完成したオープニング（重要）
```

### 2. メインコンテンツ作成
```bash
# GitHub Actionsページで「Create Radio Main Content」を選択
# 入力項目:
# - script_content: ラジオの原稿（テキスト形式）
# - music_mood: 音楽の雰囲気（例：リラックス、エネルギッシュ、ジャズ風）
```

**出力ファイル例:**
```
radio-main-20250127-123457/
├── planning/
│   ├── main-script.txt         # メイン台本
│   ├── voice-style.json        # 音声スタイル設定
│   ├── music-prompt.txt        # 音楽生成プロンプト
│   └── main-strategy.md        # 制作戦略
├── audio/
│   └── main-voice.wav          # メイン音声
├── music/
│   └── main-music.wav          # メイン音楽
└── final/
    └── final-main-audio.wav    # 完成したメインコンテンツ（重要）
```

### 3. 完全版ラジオ番組作成
```bash
# GitHub Actionsページで「Create Full Radio Show (Opening + Main)」を選択
# 入力項目:
# - opening_audio_path: radio-opening-20250127-123456/final/final-opening-audio.wav
# - main_audio_path: radio-main-20250127-123457/final/final-main-audio.wav
# - show_title: 神威日報ふりかえりラジオ
```

**重要:** 
- オープニングとメインのPRがmainブランチにマージされている必要があります
- パスは各ワークフローで生成されたフォルダ名を正確に入力してください

**出力ファイル例:**
```
radio-full-20250127-123458/
├── input/                      # 入力ファイルのコピー
│   ├── opening-audio.wav
│   └── main-audio.wav
└── final/
    ├── full-radio-show.wav     # 完成したラジオ番組
    └── show-metadata.txt       # 番組メタデータ
```

## 番組の構成
- **オープニング**: 15-20秒（挨拶、番組タイトル紹介）
- **間**: 0.5秒の無音
- **メインコンテンツ**: 30秒（ニュース内容）
- **フェードアウト**: 2秒

**総時間**: 約50秒

## 注意事項
1. 各ワークフローは独立して実行可能です
2. 完全版を作成する前に、オープニングとメインのPRをマージしてください
3. 音楽の雰囲気は番組全体の統一感を考慮して選択してください
4. 番組タイトルは「神威日報ふりかえりラジオ」で固定されています