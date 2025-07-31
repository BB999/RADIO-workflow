# ラジオ番組制作部門間連携システム

## システム概要
Claude Codeサブエージェントを活用した、完全自動化ラジオ番組制作システムです。
5つの専門部門が順次連携し、プロレベルの番組制作を実現します。

## 制作フロー設計

### 1. 基本制作フロー
```
[統合制作部門] ← 最終統合・品質管理
      ↑
[番組企画部門] → [台本制作部門] → [音声制作部門] → [音響編集部門]
      ↓              ↓              ↓              ↓
   企画JSON      台本JSON       音声ファイル    完成音声
```

### 2. データフロー仕様

#### Phase 1: 企画→台本
```json
{
  "handoff_data": {
    "from": "radio-program-planner",
    "to": "radio-script-writer", 
    "data_format": "program_structure_json",
    "required_fields": [
      "program_concept",
      "segments",
      "target_analysis", 
      "time_allocation"
    ]
  }
}
```

#### Phase 2: 台本→音声
```json
{
  "handoff_data": {
    "from": "radio-script-writer",
    "to": "radio-audio-producer",
    "data_format": "script_package_json", 
    "required_fields": [
      "scripts",
      "voice_characters",
      "timing_notes",
      "sound_cues"
    ]
  }
}
```

#### Phase 3: 音声→音響
```json
{
  "handoff_data": {
    "from": "radio-audio-producer", 
    "to": "radio-sound-engineer",
    "data_format": "audio_package_json",
    "required_fields": [
      "voice_tracks",
      "voice_profiles", 
      "quality_report",
      "technical_specs"
    ]
  }
}
```

#### Phase 4: 音響→統合
```json
{
  "handoff_data": {
    "from": "radio-sound-engineer",
    "to": "radio-production-manager",
    "data_format": "final_audio_package_json",
    "required_fields": [
      "final_audio",
      "technical_report",
      "asset_usage",
      "quality_metrics"
    ]
  }
}
```

### 3. 品質ゲートシステム

各部門間で品質チェックを実施し、基準を満たした場合のみ次工程に進行。

```python
class QualityGate:
    def __init__(self, department_name):
        self.department = department_name
        self.quality_standards = self.load_standards()
    
    def validate_output(self, output_data):
        """部門成果物の品質チェック"""
        checks = [
            self.check_required_fields(output_data),
            self.check_format_compliance(output_data),
            self.check_content_quality(output_data),
            self.check_technical_specs(output_data)
        ]
        return all(checks)
    
    def generate_quality_report(self, output_data):
        """品質レポート生成"""
        return {
            "department": self.department,
            "quality_score": self.calculate_score(output_data),
            "passed_checks": self.get_passed_checks(output_data),
            "issues": self.identify_issues(output_data),
            "recommendation": self.get_recommendations(output_data)
        }
```

## サブエージェント実行システム

### 1. Claude Code Task実行例

```python
# 番組企画部門の実行
planning_task = Task(
    description="Radio program planning",
    prompt=f"""
    Use the radio-program-planner agent to create a program concept for:
    - Target: {target_audience}
    - Duration: {program_duration}
    - Theme: {program_theme}
    
    Follow the radio-program-planner.md specifications exactly.
    """,
    subagent_type="general-purpose"
)

# 台本制作部門の実行  
script_task = Task(
    description="Radio script writing",
    prompt=f"""
    Use the radio-script-writer agent with the following planning data:
    {planning_result}
    
    Create detailed scripts following radio-script-writer.md specifications.
    """,
    subagent_type="general-purpose"
)
```

### 2. 自動化スクリプト

```python
class RadioProductionPipeline:
    def __init__(self):
        self.departments = {
            "planning": "radio-program-planner",
            "script": "radio-script-writer", 
            "audio": "radio-audio-producer",
            "sound": "radio-sound-engineer",
            "integration": "radio-production-manager"
        }
        self.current_data = {}
        
    async def execute_full_production(self, initial_requirements):
        """完全自動制作実行"""
        try:
            # Phase 1: 企画
            planning_result = await self.run_department("planning", initial_requirements)
            self.validate_and_store("planning", planning_result)
            
            # Phase 2: 台本  
            script_result = await self.run_department("script", planning_result)
            self.validate_and_store("script", script_result)
            
            # Phase 3: 音声
            audio_result = await self.run_department("audio", script_result)
            self.validate_and_store("audio", audio_result)
            
            # Phase 4: 音響
            sound_result = await self.run_department("sound", audio_result)
            self.validate_and_store("sound", sound_result)
            
            # Phase 5: 統合
            final_result = await self.run_department("integration", {
                "planning": planning_result,
                "script": script_result, 
                "audio": audio_result,
                "sound": sound_result
            })
            
            return final_result
            
        except Exception as e:
            return self.handle_production_error(e)
    
    async def run_department(self, dept_name, input_data):
        """個別部門実行"""
        agent_spec = self.load_agent_spec(self.departments[dept_name])
        
        task = Task(
            description=f"Radio {dept_name} department", 
            prompt=self.build_agent_prompt(agent_spec, input_data),
            subagent_type="general-purpose"
        )
        
        result = await task.execute()
        return self.parse_department_output(result)
```

### 3. エラーハンドリング・リトライ

```python
class ProductionErrorHandler:
    def __init__(self):
        self.max_retries = 3
        self.fallback_strategies = {}
    
    def handle_department_failure(self, department, error, input_data):
        """部門失敗時の対応"""
        if error.type == "quality_gate_failure":
            return self.retry_with_feedback(department, error.feedback, input_data)
        elif error.type == "technical_failure":
            return self.fallback_production(department, input_data)
        else:
            return self.escalate_to_manager(department, error)
    
    def retry_with_feedback(self, department, feedback, input_data):
        """フィードバック付きリトライ"""
        enhanced_prompt = self.add_feedback_to_prompt(
            self.departments[department], 
            feedback,
            input_data
        )
        return self.run_department_with_prompt(department, enhanced_prompt)
```

## 設定・設定管理

### 1. 制作設定ファイル
```json
{
  "production_config": {
    "quality_standards": {
      "audio_loudness": -23,
      "peak_level": -1,
      "minimum_duration_accuracy": 0.95
    },
    "department_timeouts": {
      "planning": 300,
      "script": 600,
      "audio": 1200, 
      "sound": 900,
      "integration": 300
    },
    "retry_policies": {
      "max_retries": 3,
      "backoff_multiplier": 2,
      "quality_gate_retry": true
    }
  }
}
```

### 2. 部門間通信プロトコル
```
データ形式: JSON
エラー通知: structured_error_json
品質チェック: quality_gate_result_json  
進捗レポート: department_progress_json
```

このシステムにより、完全自動化されたプロレベルのラジオ番組制作が実現されます。