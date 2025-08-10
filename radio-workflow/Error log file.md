# Kamuicode Workflow エラー修正ログ

## 2025-08-10: module-input-processing.yml YAMLシンタックスエラー

### エラー内容
```
Invalid workflow file: .github/workflows/orchestrator-kamui-daily-radio.yml#L130
error parsing called workflow
".github/workflows/orchestrator-kamui-daily-radio.yml"
-> "./.github/workflows/module-input-processing.yml" 
: You have an error in your yaml syntax on line 61
```

### 原因
- heredoc (`cat << 'EOF'`) 内で GitHub Actions の変数展開 `${{ inputs.development-report }}` を直接使用していた
- シングルクォート付きheredoc (`'EOF'`) は変数展開を無効にするが、GitHub Actions変数は事前に展開される必要がある

### 修正内容
```yaml
# 修正前
cat << 'EOF' > input-processing-prompt.txt
開発進捗: ${{ inputs.development-report }}
強調ポイント: ${{ inputs.topic-focus || 'なし' }}
EOF

# 修正後
DEVELOPMENT_REPORT="${{ inputs.development-report }}"
TOPIC_FOCUS="${{ inputs.topic-focus }}"

cat << EOF > input-processing-prompt.txt
開発進捗: $DEVELOPMENT_REPORT
強調ポイント: ${TOPIC_FOCUS:-なし}
EOF
```

### 修正のポイント
1. GitHub Actions変数を事前にシェル変数に格納
2. heredocのクォートを削除（`'EOF'` → `EOF`）して変数展開を有効化
3. デフォルト値は Bashの `${VAR:-default}` 構文を使用

### 教訓
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