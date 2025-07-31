# ラジオ番組制作サブエージェント使用ガイド

## 概要
Claude Codeのサブエージェント機能を使用した、5部門連携ラジオ番組制作システムの使用方法を説明します。

## 基本的な使用方法

### 1. 単一部門での使用

#### 番組企画部門の使用例
```bash
# Claude Codeで以下のように実行
Task(
  description="Radio program planning",
  prompt="""
  Use the radio-program-planner agent from /Users/noranekob/cursor/kamuicode-workflow/radio-workflow/agents/radio-program-planner.md to create a morning radio program:
  
  Requirements:
  - Target audience: 20-30代ビジネスパーソン  
  - Duration: 30 minutes
  - Theme: 朝の情報番組
  - Broadcast time: 7:30-8:00 AM weekdays
  
  Output the result as JSON format for the next department.
  """,
  subagent_type="general-purpose"
)
```

#### 台本制作部門の使用例
```bash
Task(
  description="Radio script writing", 
  prompt="""
  Use the radio-script-writer agent from /Users/noranekob/cursor/kamuicode-workflow/radio-workflow/agents/radio-script-writer.md with this planning data:
  
  [企画部門からの出力JSONを貼り付け]
  
  Create detailed radio scripts with timing and sound effect instructions.
  """,
  subagent_type="general-purpose"
)
```

### 2. 完全自動制作フロー

#### Step 1: 初期要件設定
```json
{
  "project_requirements": {
    "program_type": "morning_info_show",
    "duration_minutes": 30,
    "target_audience": "business_professionals_20s_30s", 
    "theme": "daily_business_info",
    "special_requirements": "commute_time_friendly",
    "delivery_format": "mp3_320kbps"
  }
}
```

#### Step 2: 部門別順次実行
```bash
# 1. 番組企画部門
claude code
> Task(description="Program planning", prompt="Use radio-program-planner agent with: [要件JSON]", subagent_type="general-purpose")

# 2. 台本制作部門  
> Task(description="Script writing", prompt="Use radio-script-writer agent with: [企画結果JSON]", subagent_type="general-purpose")

# 3. 音声制作部門
> Task(description="Audio production", prompt="Use radio-audio-producer agent with: [台本結果JSON]", subagent_type="general-purpose")

# 4. 音響編集部門
> Task(description="Sound engineering", prompt="Use radio-sound-engineer agent with: [音声結果JSON]", subagent_type="general-purpose")

# 5. 統合制作部門
> Task(description="Production management", prompt="Use radio-production-manager agent with all department outputs", subagent_type="general-purpose")
```

## 実践的な使用例

### ケース1: 30分朝の情報番組制作

#### 実行コマンド例
```bash
# 企画段階
claude code
> Task(
    description="Morning show planning",
    prompt="""
    Load the radio-program-planner agent specification from radio-workflow/agents/radio-program-planner.md.
    
    Create a program plan for:
    - 30-minute morning information show
    - Target: working professionals in their 20s-30s  
    - Broadcast: weekday 7:30-8:00 AM
    - Content: business news, skill tips, motivation
    
    Provide output in the JSON format specified in the agent documentation.
    """,
    subagent_type="general-purpose"
)
```

#### 期待される出力
```json
{
  "program_concept": "効率的な朝の情報キャッチアップ番組",
  "segments": [
    {"name": "オープニング", "duration": 2},
    {"name": "ビジネスニュース", "duration": 8},
    {"name": "スキルアップ", "duration": 10},
    {"name": "天気・交通", "duration": 5},
    {"name": "モチベーション", "duration": 3},
    {"name": "エンディング", "duration": 2}
  ],
  "target_analysis": {...},
  "differentiation": "短時間で実用的情報を厳選"
}
```

### ケース2: 音声制作でのFAL API活用

```bash
# 音声制作段階
Task(
  description="Audio generation with FAL",
  prompt="""
  Use the radio-audio-producer agent to generate voices using FAL API.
  
  Script data: [台本部門からのJSON]
  
  Create high-quality AI voices for:
  - Main MC: friendly female voice, 20s
  - News announcer: professional neutral voice
  - Weather presenter: warm conversational voice
  
  Use FAL API settings optimized for radio broadcast quality.
  """,
  subagent_type="general-purpose"
)
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. 部門間データ形式不整合
**問題**: 前の部門の出力が次の部門で使用できない
**解決**: 各エージェントファイルのJSON形式例を確認し、正確な形式で出力させる

```bash
# 修正例
prompt="""
Follow the EXACT JSON format specified in the agent documentation.
Include all required_fields listed in the handoff_data section.
"""
```

#### 2. FAL API認証エラー  
**問題**: 音声生成時にAPI認証が失敗する
**解決**: FAL_API_KEYの設定確認

```bash
# 環境変数設定
export FAL_API_KEY="your_fal_api_key_here"
```

#### 3. 音声品質基準未達
**問題**: 音響部門で放送基準に達しない
**解決**: 品質パラメータを明示的に指定

```bash
prompt="""
Ensure final audio meets broadcast standards:
- Loudness: -23 LUFS
- Peak level: -1 dBFS max
- Format: WAV 44.1kHz 16bit
"""
```

## 高度な使用方法

### 1. カスタム制作テンプレート

特定の番組タイプ用のテンプレートを作成可能：

```json
{
  "news_show_template": {
    "segments": ["opening", "main_news", "weather", "closing"],
    "voice_characters": ["anchor", "weather_presenter"],
    "bgm_style": "serious_professional"
  },
  "variety_show_template": {
    "segments": ["opening", "talk", "games", "music", "closing"],
    "voice_characters": ["main_host", "co_host", "guest"],
    "bgm_style": "upbeat_entertaining"
  }
}
```

### 2. 品質管理の自動化

各部門の出力に対して自動品質チェックを実装：

```bash
Task(
  description="Quality check automation",
  prompt="""
  Implement quality gates between departments:
  1. Check required JSON fields completion
  2. Validate technical specifications
  3. Assess content quality scores
  4. Generate quality reports
  
  Only proceed to next department if quality gate passes.
  """,
  subagent_type="general-purpose"
)
```

### 3. 並列制作処理

複数番組の同時制作：

```bash
# 複数番組を並列処理
for program in ["morning_news", "evening_talk", "weekend_variety"]:
    Task(
      description=f"{program} production",
      prompt=f"Create {program} using full 5-department pipeline",
      subagent_type="general-purpose"
    )
```

## ベストプラクティス

### 1. プロンプト設計
- 各エージェントファイルの仕様を正確に参照
- 入出力形式を明確に指定
- エラー時の対処法を含める

### 2. データ管理  
- 部門間のデータフローを文書化
- バックアップ・リカバリ手順を整備
- バージョン管理を実施

### 3. 品質保証
- 各段階での品質チェック実施
- 自動テスト・検証の導入
- 継続的改善プロセスの確立

このガイドに従って、プロレベルのラジオ番組制作を自動化できます。