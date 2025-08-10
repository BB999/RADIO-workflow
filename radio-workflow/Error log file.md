# Kamuicode Workflow エラー修正ログ

## 📝 エラーログの書き方

### 基本フォーマット
```markdown
## YYYY-MM-DD: [ファイル名] [エラータイプ]

### エラー内容
```
具体的なエラーメッセージ
```

### 原因
1. 原因1の詳細説明
2. 原因2の詳細説明

### 修正内容
```yaml/bash/javascript
# 修正前のコード例
old_code_here

# 修正後のコード例  
new_code_here
```

### 修正のポイント
- 重要なポイント1
- 重要なポイント2

### 修正結果
✅ 成功 / ❌ 失敗 - 結果の説明

### 教訓
次回同じエラーを避けるための学習内容
```

### エラー分類
- **YAMLシンタックスエラー**: GitHub Actions YAML構文問題
- **APIエラー**: 外部API呼び出し失敗
- **依存関係エラー**: パッケージ・ファイル不足
- **環境エラー**: 環境変数・設定問題
- **論理エラー**: コードロジックの問題

### 重要な記録項目
1. **エラーメッセージ**: 完全なエラー出力
2. **再現手順**: エラーが発生した状況
3. **修正コード**: before/afterの明確な比較
4. **試行回数**: 何回目の修正で成功したか
5. **学習内容**: 今後のための教訓

---

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

**4回目の修正**: ✅ 成功
- heredocを完全に廃止（プロンプト部分）
- echoコマンドの連続実行で構築
- シングルクォートで特殊文字をエスケープ

**5回目の修正（line 194エラー）**: ✅ 成功（期待）
- JSONファイル保存部分のheredocも廃止
- GitHub Outputsのheredocタグを`GITHUB_OUTPUT_EOF`に変更
- すべてのheredocを排除
3. デフォルト値は Bashの `${VAR:-default}` 構文を使用

### 教訓
- **GitHub Actions YAMLでheredocは避ける**: パーサーがマルチライン文字列を正しく処理できない場合が多い
- **echoコマンドの連続実行が安全**: 単純だが確実に動作する
- **特殊文字はシングルクォートでエスケープ**: ダブルクォートだと変数展開で問題が起きる
- GitHub Actionsの変数展開とシェルの変数展開は異なるタイミングで発生する
- heredoc内でGitHub Actions変数を使う場合は、事前にシェル変数に格納する
- YAMLファイル内のheredocは特に注意が必要

---

## 2025-08-10: module-radio-planning.yml YAMLシンタックスエラー

### エラー内容
```
Invalid workflow file: .github/workflows/module-radio-planning.yml#L269
You have an error in your yaml syntax on line 269
```

### 原因
- 複数行の文字列を変数に代入する際、改行がYAMLパーサーを混乱させた
- `CONTENT_SOURCE="【タイトル】\n$VARIABLE"` の形式が問題

### 修正内容
```bash
# 修正前
CONTENT_SOURCE="【Gemini処理済み構造化情報】
$PROCESSED_SUMMARY"

# 修正後
CONTENT_SOURCE=$(printf "【Gemini処理済み構造化情報】\n%s" "$PROCESSED_SUMMARY")
```

### 修正結果
✅ 成功 - `printf`コマンドで安全に複数行文字列を構築

---

## 2025-08-10: Gemini CLI パッケージ名エラー

### エラー内容
```
npm error code E404
npm error 404 Not Found - GET https://registry.npmjs.org/@google-ai%2fgenerativelanguage-cli - Not found
npm error 404  '@google-ai/generativelanguage-cli@*' is not in this registry.
```

### 原因
- Gemini CLIパッケージ（`@google-ai/generativelanguage-cli`）は存在しない
- Gemini APIは直接REST APIを使用する必要がある

### 修正内容
```yaml
# 修正前
- name: Install Gemini CLI
  run: |
    npm install -g @google-ai/generativelanguage-cli

# 修正後
- name: Setup Gemini API
  run: |
    echo "✅ Gemini API を直接使用します（追加パッケージ不要）"
```

### 修正結果
✅ 成功 - Gemini APIをcurlで直接呼び出す方式に変更

---

## 2025-08-10: Gemini APIレスポンスのJSONパースエラー

### エラー内容
```
Error: ❌ Gemini APIから有効なJSON形式の応答を受信できませんでした
```

### 原因
- Gemini APIが返すJSONがマークダウンのコードブロック（\`\`\`json）で囲まれている
- jqコマンドがコードブロックを含んだままパースしようとして失敗

### 修正内容
```bash
# 修正前
if echo "$PROCESSED_CONTENT" | jq . > /dev/null 2>&1; then

# 修正後
# マークダウンのコードブロックを削除
CLEANED_CONTENT=$(echo "$PROCESSED_CONTENT" | sed 's/^```json//' | sed 's/^```$//' | sed '/^$/d')
if echo "$CLEANED_CONTENT" | jq . > /dev/null 2>&1; then
```

### 修正結果
✅ 成功（期待）- コードブロックを除去してからJSONパース

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