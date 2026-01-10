# 📋 Debate Arena Bot - セットアップガイド

このガイドでは、Debate Arena Botを最初から起動するまでの手順を詳しく説明します。

---

## 🎯 事前準備

### 必要なもの

1. **Pythonの環境**
   - Python 3.9以上
   - pipパッケージマネージャー

2. **Discordアカウント**
   - Discord Developer Portalへのアクセス権

3. **Discord サーバー**
   - Botをテストするためのサーバー（管理者権限）

---

## 📦 ステップ1: プロジェクトのダウンロード

```bash
# プロジェクトをダウンロード
cd C:\書類\discord-Discussion-setup

# 依存パッケージをインストール
pip install -r requirements.txt
```

---

## 🤖 ステップ2: Discord Botの作成

### 2-1. Discord Developer Portalにアクセス

1. [https://discord.com/developers/applications](https://discord.com/developers/applications) にアクセス
2. 「New Application」ボタンをクリック
3. アプリケーション名を入力（例: `Debate Arena Bot`）
4. 「Create」をクリック

### 2-2. Botユーザーの作成

1. 左メニューから「Bot」を選択
2. 「Add Bot」をクリック
3. 「Yes, do it!」で確認

### 2-3. Bot設定

**重要な設定項目:**

1. **TOKEN**
   - 「Reset Token」をクリック
   - 表示されたトークンをコピー（後で使用）
   - ⚠️ トークンは絶対に公開しないでください

2. **Privileged Gateway Intents**
   - ✅ `MESSAGE CONTENT INTENT` を有効化
   - ✅ `SERVER MEMBERS INTENT` を有効化
   - 「Save Changes」をクリック

---

## 🔐 ステップ3: 環境変数の設定

### 3-1. .envファイルの作成

プロジェクトフォルダに `.env` ファイルを作成：

```bash
# Windowsの場合
copy .env.example .env

# またはテキストエディタで新規作成
```

### 3-2. トークンの設定

`.env` ファイルを開いて以下のように編集：

```
DISCORD_BOT_TOKEN=先ほどコピーしたBotトークンをここに貼り付け
```

例：
```

```

---

## 🔗 ステップ4: BotをDiscordサーバーに招待

### 4-1. OAuth2 URLの生成

1. Discord Developer Portalの左メニューから「OAuth2」→「URL Generator」を選択

2. **SCOPES**で以下を選択：
   - ✅ `bot`
   - ✅ `applications.commands`

3. **BOT PERMISSIONS**で以下を選択：
   - ✅ `Send Messages`
   - ✅ `Send Messages in Threads`
   - ✅ `Embed Links`
   - ✅ `Attach Files`
   - ✅ `Read Message History`
   - ✅ `Use Slash Commands`
   - ✅ `Manage Messages`（オプション：違反メッセージ削除用）

4. 一番下に生成されたURLをコピー

### 4-2. サーバーに招待

1. コピーしたURLをブラウザで開く
2. Botを追加したいサーバーを選択
3. 「認証」をクリック
4. reCAPTCHAを完了

✅ Botがサーバーに追加されました！

---

## ▶️ ステップ5: Botの起動

### 5-1. 起動コマンド

```bash
python bot.py
```

### 5-2. 起動確認

以下のようなメッセージが表示されれば成功：

```
✅ Debate Arena Bot#1234 としてログインしました
Bot ID: 1234567890123456789
準備完了!
```

---

## 🎮 ステップ6: 動作確認

### 6-1. 管理者ロールの設定（オプション）

デフォルトでは「Debate Admin」または「モデレーター」ロールがコマンド実行可能です。

カスタマイズする場合は `config.py` を編集：

```python
ADMIN_ROLE_NAMES: List[str] = [
    'あなたのサーバーの管理者ロール名',
]
```

### 6-2. テストディベートの実行

1. Discordサーバーでスラッシュコマンドを入力：

```
/debate
```

2. パラメータを設定（またはデフォルトのまま）：
   - `recruit_time`: 1（テスト用に短く設定）
   - `message_limit`: 3
   - `max_chars`: 500

3. 「参加する」ボタンをクリック（複数のアカウントで）

4. 募集時間終了後、自動的にディベート開始

---

## ⚙️ ステップ7: カスタマイズ（オプション）

### 議題のカスタマイズ

`config.py`の`DEBATE_TOPICS`リストを編集：

```python
DEBATE_TOPICS: List[str] = [
    "あなたのオリジナル議題1",
    "あなたのオリジナル議題2",
    # ...
]
```

### 禁止ワードの追加

サーバー固有の禁止語がある場合：

```python
PROHIBITED_WORDS: List[str] = [
    # 既存の禁止語
    'サーバー固有の禁止語',
]
```

### チャンネル制限

特定のチャンネルのみでBotを動作させる場合：

1. Discordで対象チャンネルのIDをコピー
   - 開発者モードを有効化（設定 → 詳細設定 → 開発者モード）
   - チャンネル右クリック → IDをコピー

2. `config.py`を編集：

```python
ALLOWED_CHANNEL_IDS: List[int] = [
    123456789012345678,  # コピーしたチャンネルID
]
```

---

## 🐛 トラブルシューティング

### エラー: `discord.errors.LoginFailure`

**原因:** Botトークンが正しくない

**解決策:**
- `.env`ファイルのトークンを確認
- Discord Developer Portalでトークンを再生成

### エラー: `discord.errors.Forbidden`

**原因:** Botに必要な権限がない

**解決策:**
- Bot招待時に必要な権限をすべて選択
- サーバーのロール設定を確認

### スラッシュコマンドが表示されない

**原因:** コマンド同期の遅延

**解決策:**
- Bot再起動
- Discordクライアント再起動
- 1時間ほど待つ（Discord側の同期待ち）

### モジュールが見つからないエラー

**原因:** 依存パッケージ未インストール

**解決策:**
```bash
pip install -r requirements.txt
```

---

## 🎉 完了！

これで Debate Arena Bot が稼働しています。

### 次のステップ

- サーバーメンバーに使い方を周知
- `/debate_help` コマンドで使い方を確認
- 議題や設定をサーバーに合わせてカスタマイズ

---

## 📞 サポート

問題が解決しない場合：

1. `README.md`のトラブルシューティングセクションを確認
2. GitHubリポジトリでIssueを作成
3. ログファイル（存在する場合）を確認

---

**楽しいディベートライフを！** 🎯
