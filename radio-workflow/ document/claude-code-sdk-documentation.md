# Claude Code SDK ドキュメント

## 概要

Claude Code SDKは、Claude Codeをプログラム的に統合し、サブプロセスとして実行できるようにするライブラリです。コマンドライン、TypeScript、Pythonインターフェースをサポートし、AI駆動のコーディング支援とツール構築を可能にします。

## 主な機能

- **プログラム的統合** - Claude Codeをサブプロセスとして実行
- **マルチ言語サポート** - TypeScriptとPythonのSDKを提供
- **柔軟な出力形式** - テキスト、JSON、ストリーミングJSONに対応
- **MCP統合** - Model Context Protocolとの統合をサポート
- **カスタマイズ可能** - システムプロンプトやツール権限の細かい制御

## インストール

### TypeScript/JavaScript

```bash
npm install @anthropic-ai/claude-code
```

### Python

```bash
pip install claude-code-sdk
```

## 認証設定

### 1. Anthropic API キー

最も一般的な認証方法：

```bash
# 環境変数を設定
export ANTHROPIC_API_KEY="your-api-key-here"
```

APIキーの取得方法：
1. [Anthropic Console](https://console.anthropic.com)にアクセス
2. 専用のAPIキーを作成
3. 環境変数に設定

### 2. サードパーティプロバイダー

#### Amazon Bedrock

```bash
export CLAUDE_CODE_USE_BEDROCK=1
# AWS認証情報も必要
```

#### Google Vertex AI

```bash
export CLAUDE_CODE_USE_VERTEX=1
# GCP認証情報も必要
```

## 基本的な使用方法

### Python SDK

#### シンプルなクエリ

```python
import anyio
from claude_code_sdk import query, ClaudeCodeOptions

async def main():
    async for message in query(
        prompt="foo.pyについて俳句を書いて",
        options=ClaudeCodeOptions(max_turns=3)
    ):
        print(message)

anyio.run(main)
```

#### ファイル操作を含むタスク

```python
import anyio
from claude_code_sdk import query, ClaudeCodeOptions

async def main():
    prompt = """
    新しいPythonプロジェクトを作成してください：
    - プロジェクト名: my_app
    - requirements.txtを作成
    - 基本的なプロジェクト構造を設定
    """
    
    async for message in query(
        prompt=prompt,
        options=ClaudeCodeOptions(
            max_turns=10,
            allowedTools=["write", "edit", "read", "bash"]
        )
    ):
        print(message)

anyio.run(main)
```

### TypeScript SDK

#### 基本的な使用例

```typescript
import { query, ClaudeCodeOptions } from '@anthropic-ai/claude-code';

async function main() {
    const options: ClaudeCodeOptions = {
        maxTurns: 3
    };
    
    for await (const message of query("READMEファイルを作成して", options)) {
        console.log(message);
    }
}

main();
```

#### 高度な設定

```typescript
import { query, ClaudeCodeOptions } from '@anthropic-ai/claude-code';

async function main() {
    const options: ClaudeCodeOptions = {
        maxTurns: 5,
        allowedTools: ["read", "write", "edit"],
        systemPrompt: "あなたは経験豊富なTypeScript開発者です。",
        outputFormat: "json"
    };
    
    for await (const message of query("TypeScriptの設定を最適化して", options)) {
        console.log(JSON.parse(message));
    }
}

main();
```

## ClaudeCodeOptions 詳細

### 主要なオプション

```python
ClaudeCodeOptions(
    # 最大ターン数（デフォルト: 制限なし）
    max_turns=10,
    
    # 許可するツール（デフォルト: すべて）
    allowedTools=["read", "write", "edit", "bash", "grep"],
    
    # カスタムシステムプロンプト
    system_prompt="特定の指示やコンテキストをここに記述",
    
    # 出力形式（"text", "json", "streaming-json"）
    output_format="text",
    
    # 非対話モード
    print_mode=True,
    
    # 前回の会話を継続
    continue_session=True,
    
    # 特定のセッションを再開
    resume_session="session-id-here"
)
```

### ツール権限の制御

利用可能なツール：
- `read` - ファイル読み取り
- `write` - ファイル書き込み
- `edit` - ファイル編集
- `bash` - シェルコマンド実行
- `grep` - ファイル検索
- `glob` - ファイルパターンマッチング
- `webfetch` - Web取得
- `websearch` - Web検索

```python
# 読み取り専用モード
options = ClaudeCodeOptions(allowedTools=["read", "grep", "glob"])

# ファイル操作のみ
options = ClaudeCodeOptions(allowedTools=["read", "write", "edit"])
```

## 実践的な使用例

### 1. コードレビュー自動化

```python
import anyio
from claude_code_sdk import query, ClaudeCodeOptions

async def review_code(file_path: str):
    prompt = f"""
    {file_path}のコードレビューを実行してください：
    - セキュリティの問題を確認
    - パフォーマンスの改善点を提案
    - ベストプラクティスの違反を指摘
    """
    
    options = ClaudeCodeOptions(
        max_turns=5,
        allowedTools=["read", "grep"],
        system_prompt="経験豊富なコードレビュアーとして行動してください"
    )
    
    async for message in query(prompt, options):
        print(message)

anyio.run(review_code, "src/main.py")
```

### 2. テスト生成

```python
async def generate_tests(source_file: str):
    prompt = f"""
    {source_file}に対するユニットテストを作成してください：
    - pytestを使用
    - エッジケースをカバー
    - モックを適切に使用
    """
    
    options = ClaudeCodeOptions(
        max_turns=10,
        allowedTools=["read", "write", "edit"]
    )
    
    async for message in query(prompt, options):
        print(message)
```

### 3. ドキュメント生成

```typescript
async function generateDocs(projectPath: string) {
    const prompt = `
    ${projectPath}のプロジェクトドキュメントを生成してください：
    - API リファレンス
    - 使用例
    - インストールガイド
    `;
    
    const options: ClaudeCodeOptions = {
        maxTurns: 15,
        allowedTools: ["read", "write", "glob"],
        outputFormat: "json"
    };
    
    for await (const message of query(prompt, options)) {
        const result = JSON.parse(message);
        console.log(result);
    }
}
```

## エラーハンドリング

### Python

```python
import anyio
from claude_code_sdk import query, ClaudeCodeOptions, ClaudeCodeError

async def safe_query():
    try:
        async for message in query("タスクを実行", ClaudeCodeOptions()):
            print(message)
    except ClaudeCodeError as e:
        print(f"エラーが発生しました: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")

anyio.run(safe_query)
```

### TypeScript

```typescript
import { query, ClaudeCodeOptions, ClaudeCodeError } from '@anthropic-ai/claude-code';

async function safeQuery() {
    try {
        for await (const message of query("タスクを実行", {})) {
            console.log(message);
        }
    } catch (error) {
        if (error instanceof ClaudeCodeError) {
            console.error(`Claude Codeエラー: ${error.message}`);
        } else {
            console.error(`予期しないエラー: ${error}`);
        }
    }
}
```

## ベストプラクティス

### 1. 適切なツール権限の設定

```python
# 読み取り専用タスク
read_only_options = ClaudeCodeOptions(
    allowedTools=["read", "grep", "glob"]
)

# ファイル変更を伴うタスク
edit_options = ClaudeCodeOptions(
    allowedTools=["read", "write", "edit", "bash"]
)
```

### 2. ターン数の最適化

```python
# 簡単なタスク
simple_options = ClaudeCodeOptions(max_turns=3)

# 複雑なタスク
complex_options = ClaudeCodeOptions(max_turns=20)
```

### 3. 明確なプロンプト

```python
# 良い例
prompt = """
以下の要件でRESTful APIを作成してください：
- フレームワーク: FastAPI
- データベース: PostgreSQL
- 認証: JWT
- エンドポイント: /users, /posts, /comments
"""

# 悪い例
prompt = "APIを作って"
```

### 4. エラー処理の実装

```python
async def robust_implementation():
    retries = 3
    for attempt in range(retries):
        try:
            async for message in query(prompt, options):
                yield message
            break
        except ClaudeCodeError as e:
            if attempt == retries - 1:
                raise
            await anyio.sleep(2 ** attempt)  # 指数バックオフ
```

## MCP (Model Context Protocol) 統合

### MCP サーバーの設定

```python
options = ClaudeCodeOptions(
    mcp_servers={
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": "your-token"}
        }
    }
)
```

### MCP ツールの使用

```python
prompt = """
MCPを使用してGitHubリポジトリの情報を取得してください：
- リポジトリ: anthropics/claude-code
- 最新のissueを確認
- PRの状態を確認
"""

async for message in query(prompt, options):
    print(message)
```

## パフォーマンスの考慮事項

### 1. ストリーミング出力の活用

```python
# メモリ効率的なストリーミング
options = ClaudeCodeOptions(output_format="streaming-json")

async for chunk in query(prompt, options):
    # チャンクごとに処理
    process_chunk(chunk)
```

### 2. セッションの再利用

```python
# セッションIDを保存
session_id = None
async for message in query(prompt, ClaudeCodeOptions()):
    if hasattr(message, 'session_id'):
        session_id = message.session_id

# 後で再開
options = ClaudeCodeOptions(resume_session=session_id)
```

### 3. 並列処理

```python
import asyncio

async def parallel_tasks():
    tasks = [
        query("タスク1", ClaudeCodeOptions()),
        query("タスク2", ClaudeCodeOptions()),
        query("タスク3", ClaudeCodeOptions())
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

## トラブルシューティング

### よくある問題と解決策

1. **認証エラー**
   ```bash
   # APIキーが設定されているか確認
   echo $ANTHROPIC_API_KEY
   ```

2. **ツール権限エラー**
   ```python
   # 必要なツールが許可されているか確認
   options = ClaudeCodeOptions(
       allowedTools=["read", "write", "edit", "bash"]
   )
   ```

3. **タイムアウト**
   ```python
   # タイムアウトを延長
   options = ClaudeCodeOptions(
       timeout=300  # 5分
   )
   ```

4. **メモリ不足**
   ```python
   # ストリーミング出力を使用
   options = ClaudeCodeOptions(
       output_format="streaming-json",
       max_turns=5  # ターン数を制限
   )
   ```

## まとめ

Claude Code SDKは、AI駆動の開発を既存のワークフローに統合するための強力なツールです。適切な設定とエラーハンドリングにより、コードレビュー、テスト生成、ドキュメント作成などの様々なタスクを自動化できます。SDKの柔軟性により、シンプルなスクリプトから複雑なCI/CDパイプラインまで、幅広い用途に対応可能です。