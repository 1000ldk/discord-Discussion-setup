# 📚 Debate Arena Bot

Discord利用規約完全準拠のディベート（模擬討論）Bot

claude から請求があるためAIの仕様について変更いたします。

## 🎯 概要

**Debate Arena Bot**は、論理的思考力と議論構成力を鍛えるための教育・娯楽用Discord Botです。

### 特徴

✅ **完全規約準拠** - Discordの利用規約・コミュニティガイドラインに完全準拠
✅ **ハラスメント防止** - 人格攻撃・誹謗中傷を自動検出・防止
✅ **教育目的** - 論理的思考の訓練ツールとして設計
✅ **非対立的** - 「勝ち負け」ではなく「構成評価」を提供

### ❌ このBotが行わないこと

- レスバ・論破の助長
- 人格・能力の評価
- 勝敗の断定的宣言
- 政治・宗教・差別的議題の扱い

---

## 🚀 セットアップ

### 1. 必要要件

- Python 3.9以上
- Discord Botアカウント（Discord Developer Portalで作成）

### 2. インストール

```bash
# リポジトリをクローン
git clone <repository_url>
cd discord-Discussion-setup

# 依存パッケージをインストール
pip install -r requirements.txt

# 環境変数ファイルを作成
cp .env.example .env
```

### 3. Discord Bot設定

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 「New Application」をクリック
3. Bot設定：
   - `Bot` タブで「Add Bot」
   - `MESSAGE CONTENT INTENT`を有効化
   - `SERVER MEMBERS INTENT`を有効化
4. Botトークンをコピー
5. `.env`ファイルに以下を記載：

```
DISCORD_BOT_TOKEN=あなたのBotトークン
```

### 4. Bot招待

OAuth2 URL Generatorで以下を選択：
- **Scopes:** `bot`, `applications.commands`
- **Bot Permissions:** 
  - Send Messages
  - Embed Links
  - Read Message History
  - Use Slash Commands

生成されたURLでBotをサーバーに招待。

### 5. 起動

```bash
python bot.py
```

---

## 📖 使い方

### 管理者コマンド

#### `/debate` - ディベートセッション作成

```
/debate recruit_time:5 message_limit:5 max_chars:500
```

**パラメータ:**
- `recruit_time`: 募集時間（分）
- `message_limit`: 1人あたりの発言回数制限
- `max_chars`: 1発言あたりの最大文字数

#### `/debate_stop` - 強制終了

進行中のディベートを管理者権限で終了します。

### 参加者の流れ

1. 管理者がセッションを作成
2. 「参加する」ボタンをクリック
3. 同意事項を確認
4. 募集終了後、ランダムで2名が選出される
5. 指定された議題でディベート開始
6. 交互に発言
7. 終了後、構成評価が表示される

---

## ⚙️ 設定カスタマイズ

`config.py`で以下をカスタマイズ可能：

### 議題追加

```python
DEBATE_TOPICS: List[str] = [
    "あなたのオリジナル議題",
    # ...
]
```

### 禁止ワード追加

```python
PROHIBITED_WORDS: List[str] = [
    'サーバー固有の禁止語',
    # ...
]
```

### 管理者ロール設定

```python
ADMIN_ROLE_NAMES: List[str] = [
    'あなたのサーバーの管理者ロール名',
]
```

---

## 🛡️ 安全性保証

### 実装済みの安全機能

✅ **禁止ワードフィルター** - 攻撃的表現を自動検出
✅ **人称攻撃検出** - 「お前は」等のパターンをブロック
✅ **3ストライク制** - 違反3回で自動終了
✅ **議題の厳選** - 安全な議題のみ使用
✅ **断定的評価の排除** - 「勝ち」「負け」を使用しない

### 評価の透明性

Botの評価は以下の基準で行われます：

- **論点の一貫性** - 主張のブレの少なさ
- **主張の明確さ** - 論点の明瞭さ
- **反論の構造性** - 論理的な構成
- **感情的表現の少なさ** - 冷静な議論

**重要:** これらは参考意見であり、正誤や優劣を示すものではありません。

---

## 📊 コマンド一覧

| コマンド | 説明 | 権限 |
|---------|------|------|
| `/debate` | セッション作成 | 管理者 |
| `/debate_stop` | 強制終了 | 管理者 |
| `/debate_help` | ヘルプ表示 | 全員 |

---

## 🚫 禁止事項

以下の行為は自動検出され、警告・セッション終了の対象となります：

- 人格攻撃・侮辱・誹謗中傷
- 実在人物・団体への言及
- 政治・宗教・差別的発言
- 議題からの逸脱
- 感情的な罵倒

---

## 🔧 トラブルシューティング

### Botが起動しない

- `.env`ファイルにBotトークンが正しく設定されているか確認
- `discord.py`が正しくインストールされているか確認

### スラッシュコマンドが表示されない

- BotにOAuth2スコープ`applications.commands`が付与されているか確認
- Bot再招待またはDiscordクライアント再起動

### 権限エラー

- Botに必要な権限（Send Messages, Embed Links等）が付与されているか確認

---

## 📝 ライセンス

本プロジェクトはMITライセンスの下で公開されています。

---

## ⚠️ 免責事項

本Botは教育・娯楽目的で提供されています。
Botによる評価は参考意見であり、絶対的な正誤や優劣を示すものではありません。

ユーザーの行動に起因する問題について、開発者は一切の責任を負いません。
各サーバーの管理者は、適切な運用ルールを設定してください。

---

## 🤝 貢献

バグ報告・機能提案は大歓迎です。
Issueまたはプルリクエストをお送りください。

---

## 📧 お問い合わせ

質問や問題があれば、Issueを作成してください。

---

**Debate Arena Bot v1.0** - 論理的思考を楽しく鍛えよう 🎯
