# Kamuicode Workflow エラー修正ログ

## 2025-08-10: module-input-processing.yml YAMLシンタックスエラー（複数回修正）

### エラー内容（1回目）
```
Invalid workflow file: .github/workflows/orchestrator-kamui-daily-radio.yml#L130
error parsing called workflow
".github/workflows/orchestrator-kamui-daily-radio.yml"
-> "./.github/workflows/module-input-processing.yml" 
: You have an error in your yaml syntax on line 61
```

### エラー内容（2回目）
```
: You have an error in your yaml syntax on line 64
```

### 原因
1. heredoc (`cat << 'EOF'`) 内で GitHub Actions の変数展開 `${{ inputs.development-report }}` を直接使用
2. heredoc内のバッククォート（\`\`\`）がYAMLパーサーを混乱させる
3. YAMLのインデントとheredocの組み合わせによる構文解析エラー

### 最終的な修正内容
```yaml
# 修正前
cat << 'EOF' > input-processing-prompt.txt
開発進捗: ${{ inputs.development-report }}
強調ポイント: ${{ inputs.topic-focus || 'なし' }}
```json
{...}
```
EOF

# 修正後（最終版）
DEVELOPMENT_REPORT="${{ inputs.development-report }}"
TOPIC_FOCUS="${{ inputs.topic-focus }}"

cat << 'PROMPT_EOF' > input-processing-prompt.txt
開発進捗: ${DEVELOPMENT_REPORT}
強調ポイント: ${TOPIC_FOCUS}
PROMPT_EOF

# 変数を置換
sed -i "s|\${DEVELOPMENT_REPORT}|$DEVELOPMENT_REPORT|g" input-processing-prompt.txt
sed -i "s|\${TOPIC_FOCUS}|${TOPIC_FOCUS:-なし}|g" input-processing-prompt.txt
```

### 修正のポイント
1. heredocのタグを`EOF`から`PROMPT_EOF`に変更（予約語との衝突回避）
2. シングルクォート付きheredoc（`'PROMPT_EOF'`）で変数展開を無効化
3. 変数をプレースホルダーとして記述し、sedで後から置換
4. バッククォートを含むマークダウンを安全に処理

### 修正結果
**最初の修正**: ❌ 失敗（line 61エラー）
- heredoc内でGitHub Actions変数を直接使用していた

**2回目の修正**: ❌ 失敗（line 64エラー）  
- heredocのクォートを外したが、バッククォートがパーサーを混乱させた

**3回目の修正**: ❌ 失敗（line 64エラー）
- heredocタグを変更したが、YAMLパーサーがheredoc自体を正しく処理できない

**最終修正（4回目）**: ✅ 成功（期待）
- heredocを完全に廃止
- echoコマンドの連続実行で構築
- シングルクォートで特殊文字をエスケープ
3. デフォルト値は Bashの `${VAR:-default}` 構文を使用

### 教訓
- **GitHub Actions YAMLでheredocは避ける**: パーサーがマルチライン文字列を正しく処理できない場合が多い
- **echoコマンドの連続実行が安全**: 単純だが確実に動作する
- **特殊文字はシングルクォートでエスケープ**: ダブルクォートだと変数展開で問題が起きる
- GitHub Actionsの変数展開とシェルの変数展開は異なるタイミングで発生する
- heredoc内でGitHub Actions変数を使う場合は、事前にシェル変数に格納する
- YAMLファイル内のheredocは特に注意が必要

---

## その他の修正履歴

### 2025-08-10: BGM生成ワークフローのシンタックスエラー
- **問題**: forループの構造不正、不要なelse節、変数参照エラー
- **修正**: ループ構造の修正、インデント調整、`$MCP_CONFIG_ABS_PATH` → `mcp-config.json`

### 2025-08-10: mcp-kamuicode.json依存の削除
- **問題**: ローカルファイル依存でGitHub Actions環境で動作しない
- **修正**: GitHub Secretsから直接環境変数を使用、動的にMCP設定を生成

### 2025-08-10: Gemini CLI統合（7万文字対応）
- **追加**: module-input-processing.yml（Gemini 2.0 Flash使用）
- **修正**: リトライロジック（3回試行）、エラー時は明確に停止

---

## 次回実装時の注意点

1. **heredoc使用時の変数展開**
   - GitHub Actions変数は事前にシェル変数に格納
   - クォートの有無で挙動が変わることに注意

2. **YAMLのインデント**
   - 特にマルチライン文字列では要注意
   - forループなどの制御構造は特にインデントに敏感

3. **エラーハンドリング**
   - APIコールには必ずリトライロジックを実装
   - 失敗時は明確なエラーメッセージで停止

4. **環境変数とSecrets**
   - 機密情報は必ずGitHub Secretsを使用
   - ローカルファイル依存は避ける

5. **デバッグ時のTips**
   - `echo "::group::"` でログをグループ化
   - 変数の内容は早めにログ出力で確認
   - エラー時は詳細なコンテキスト情報を出力