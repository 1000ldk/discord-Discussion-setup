"""
Debate Arena Bot - Discord利用規約完全準拠ディベートBot
教育・娯楽目的の論理的議論支援ツール
"""

import discord
from discord import app_commands
from discord.ui import Button, View
import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json
import re

# 設定インポート
from config import (
    BOT_TOKEN,
    ALLOWED_CHANNEL_IDS,
    DEBATE_TOPICS,
    PROHIBITED_WORDS,
    EVALUATION_CRITERIA,
    MAX_DEBATE_ROUNDS,
    DEFAULT_RECRUIT_TIME,
    DEFAULT_MESSAGE_LIMIT,
    ADMIN_ROLE_NAMES
)

# Intents設定
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Botクライアント
class DebateBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.active_sessions: Dict[int, 'DebateSession'] = {}
        
    async def setup_hook(self):
        await self.tree.sync()
        print("コマンドツリーを同期しました")


bot = DebateBot()


class DebateSession:
    """ディベートセッション管理クラス"""
    
    def __init__(
        self,
        channel: discord.TextChannel,
        recruit_time: int,
        message_limit: int,
        max_chars: int
    ):
        self.channel = channel
        self.recruit_time = recruit_time
        self.message_limit = message_limit
        self.max_chars = max_chars
        
        self.participants: List[discord.Member] = []
        self.debaters: List[discord.Member] = []
        self.topic: str = ""
        self.current_turn: int = 0
        self.debate_log: List[Dict] = []
        self.violations: Dict[int, int] = {}  # user_id: violation_count
        self.is_active: bool = False
        self.is_recruiting: bool = True
        
    def add_participant(self, member: discord.Member) -> bool:
        """参加者を追加"""
        if member not in self.participants:
            self.participants.append(member)
            return True
        return False
    
    def select_debaters(self) -> bool:
        """ランダムで2名のディベーターを選出"""
        if len(self.participants) < 2:
            return False
        self.debaters = random.sample(self.participants, 2)
        return True
    
    def get_current_debater(self) -> Optional[discord.Member]:
        """現在のターンの発言者を取得"""
        if not self.debaters:
            return None
        return self.debaters[self.current_turn % 2]
    
    def add_violation(self, user_id: int) -> int:
        """違反回数を記録"""
        self.violations[user_id] = self.violations.get(user_id, 0) + 1
        return self.violations[user_id]
    
    def log_message(self, author: discord.Member, content: str):
        """発言をログに記録"""
        self.debate_log.append({
            'author_id': author.id,
            'author_name': author.display_name,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'turn': self.current_turn
        })


class ParticipantView(View):
    """参加登録ボタンUI"""
    
    def __init__(self, session: DebateSession):
        super().__init__(timeout=None)
        self.session = session
    
    @discord.ui.button(label="参加する", style=discord.ButtonStyle.primary, custom_id="join_debate")
    async def join_button(self, interaction: discord.Interaction, button: Button):
        # 同意メッセージを表示
        consent_embed = discord.Embed(
            title="📋 参加にあたっての確認事項",
            description=(
                "本ディベートは**娯楽・学習目的**です。\n\n"
                "**以下の行為は禁止されています：**\n"
                "• 人格攻撃・侮辱・誹謗中傷\n"
                "• 実在人物・団体への言及\n"
                "• 政治・宗教・差別的発言\n\n"
                "**重要：**\n"
                "Botによる評価は参考意見であり、\n"
                "正誤や優劣を断定するものではありません。\n\n"
                "上記に同意いただける場合のみ参加してください。"
            ),
            color=discord.Color.blue()
        )
        
        # 既に参加済みかチェック
        if interaction.user in self.session.participants:
            await interaction.response.send_message(
                "✅ 既に参加登録されています。",
                ephemeral=True
            )
            return
        
        # 参加登録
        self.session.add_participant(interaction.user)
        
        await interaction.response.send_message(
            embed=consent_embed,
            ephemeral=True
        )
        
        # 公開メッセージで参加を通知
        await self.session.channel.send(
            f"✅ {interaction.user.mention} が参加登録しました（現在 {len(self.session.participants)} 名）"
        )


def check_prohibited_content(text: str) -> tuple[bool, Optional[str]]:
    """禁止コンテンツチェック"""
    
    # 禁止ワードチェック
    for word in PROHIBITED_WORDS:
        if word in text.lower():
            return False, f"禁止ワード「{word}」が含まれています"
    
    # 人称攻撃パターンチェック
    attack_patterns = [
        r'お前[はが]',
        r'あなた[はが].*?馬鹿',
        r'君[はが].*?無知',
        r'てめー',
        r'貴様'
    ]
    
    for pattern in attack_patterns:
        if re.search(pattern, text):
            return False, "人格攻撃的な表現が含まれています"
    
    return True, None


def evaluate_debate(log: List[Dict]) -> Dict:
    """
    ディベート評価関数
    LLM不使用の基本的なヒューリスティック評価
    """
    
    # 各ディベーターのスコアを初期化
    scores = {}
    
    for entry in log:
        author_id = entry['author_id']
        content = entry['content']
        
        if author_id not in scores:
            scores[author_id] = {
                'name': entry['author_name'],
                'consistency': 0,
                'clarity': 0,
                'structure': 0,
                'calmness': 0,
                'total': 0
            }
        
        # 論点の一貫性（文字数で簡易評価）
        if len(content) > 50:
            scores[author_id]['consistency'] += 2
        
        # 主張の明確さ（句点の数で評価）
        scores[author_id]['clarity'] += min(content.count('。'), 5)
        
        # 構造性（接続詞の使用）
        structure_words = ['しかし', 'したがって', 'なぜなら', 'つまり', 'また']
        for word in structure_words:
            if word in content:
                scores[author_id]['structure'] += 1
        
        # 感情的表現の少なさ（感嘆符の少なさ）
        exclamation_count = content.count('!') + content.count('!')
        scores[author_id]['calmness'] += max(10 - exclamation_count * 2, 0)
    
    # 各項目を0-10に正規化
    for author_id in scores:
        max_cons = max(s['consistency'] for s in scores.values())
        max_clar = max(s['clarity'] for s in scores.values())
        max_struct = max(s['structure'] for s in scores.values())
        
        if max_cons > 0:
            scores[author_id]['consistency'] = min(10, (scores[author_id]['consistency'] / max_cons) * 10)
        if max_clar > 0:
            scores[author_id]['clarity'] = min(10, (scores[author_id]['clarity'] / max_clar) * 10)
        if max_struct > 0:
            scores[author_id]['structure'] = min(10, (scores[author_id]['structure'] / max_struct) * 10)
        
        scores[author_id]['calmness'] = min(10, scores[author_id]['calmness'] / len(log) * 2)
        
        # 合計スコア
        scores[author_id]['total'] = (
            scores[author_id]['consistency'] +
            scores[author_id]['clarity'] +
            scores[author_id]['structure'] +
            scores[author_id]['calmness']
        )
    
    return scores


@bot.event
async def on_ready():
    print(f'✅ {bot.user} としてログインしました')
    print(f'Bot ID: {bot.user.id}')
    print('準備完了！')


@bot.tree.command(name="debate", description="ディベートセッションを作成します（管理者のみ）")
@app_commands.describe(
    recruit_time="募集時間（分）",
    message_limit="1人あたりの発言回数制限",
    max_chars="1発言あたりの最大文字数"
)
async def create_debate(
    interaction: discord.Interaction,
    recruit_time: int = DEFAULT_RECRUIT_TIME,
    message_limit: int = DEFAULT_MESSAGE_LIMIT,
    max_chars: int = 500
):
    """ディベートセッション作成コマンド"""
    
    # 権限チェック
    has_permission = False
    if interaction.user.guild_permissions.administrator:
        has_permission = True
    else:
        for role in interaction.user.roles:
            if role.name in ADMIN_ROLE_NAMES:
                has_permission = True
                break
    
    if not has_permission:
        await interaction.response.send_message(
            "❌ このコマンドは管理者または指定ロールのみ実行可能です。",
            ephemeral=True
        )
        return
    
    # チャンネルチェック
    if ALLOWED_CHANNEL_IDS and interaction.channel_id not in ALLOWED_CHANNEL_IDS:
        await interaction.response.send_message(
            "❌ このチャンネルではディベートを開催できません。",
            ephemeral=True
        )
        return
    
    # 既存セッションチェック
    if interaction.channel_id in bot.active_sessions:
        await interaction.response.send_message(
            "⚠️ このチャンネルでは既にディベートセッションが進行中です。",
            ephemeral=True
        )
        return
    
    # セッション作成
    session = DebateSession(
        channel=interaction.channel,
        recruit_time=recruit_time,
        message_limit=message_limit,
        max_chars=max_chars
    )
    
    bot.active_sessions[interaction.channel_id] = session
    
    # 募集メッセージ
    recruit_embed = discord.Embed(
        title="🎯 Debate Arena - 参加者募集",
        description=(
            f"**募集時間:** {recruit_time}分\n"
            f"**発言制限:** {message_limit}回/人\n"
            f"**最大文字数:** {max_chars}文字/発言\n\n"
            "下のボタンから参加登録してください。\n"
            "参加者の中からランダムで2名が選出されます。"
        ),
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(
        embed=recruit_embed,
        view=ParticipantView(session)
    )
    
    # 募集時間終了後の処理
    await asyncio.sleep(recruit_time * 60)
    
    # セッションが削除されていないかチェック
    if interaction.channel_id not in bot.active_sessions:
        return
    
    session = bot.active_sessions[interaction.channel_id]
    session.is_recruiting = False
    
    # 参加者が2名未満の場合
    if len(session.participants) < 2:
        await interaction.channel.send(
            "⚠️ 参加者が2名未満のため、ディベートを開始できませんでした。"
        )
        del bot.active_sessions[interaction.channel_id]
        return
    
    # ディベーター選出
    session.select_debaters()
    session.topic = random.choice(DEBATE_TOPICS)
    session.is_active = True
    
    # 開始メッセージ
    start_embed = discord.Embed(
        title="⚔️ ディベート開始！",
        description=(
            f"**議題:** {session.topic}\n\n"
            f"**ディベーター:**\n"
            f"🔵 Side A: {session.debaters[0].mention}\n"
            f"🔴 Side B: {session.debaters[1].mention}\n\n"
            f"最初の発言者は {session.get_current_debater().mention} です。\n"
            "交互に発言してください。\n\n"
            "**注意事項:**\n"
            "• 人格攻撃は禁止です\n"
            "• 議題から逸脱しないでください\n"
            "• 違反3回で強制終了となります"
        ),
        color=discord.Color.gold()
    )
    
    await interaction.channel.send(embed=start_embed)


@bot.event
async def on_message(message: discord.Message):
    """メッセージ監視（ディベート進行）"""
    
    # Bot自身のメッセージは無視
    if message.author.bot:
        return
    
    # セッションチェック
    if message.channel.id not in bot.active_sessions:
        return
    
    session = bot.active_sessions[message.channel.id]
    
    # セッションが非アクティブなら無視
    if not session.is_active:
        return
    
    # 発言者が現在のターンのディベーターか確認
    current_debater = session.get_current_debater()
    if message.author != current_debater:
        # ディベーター以外の場合は警告
        if message.author in session.debaters:
            await message.channel.send(
                f"⚠️ {message.author.mention} さん、現在は {current_debater.mention} のターンです。"
            )
        return
    
    # 文字数チェック
    if len(message.content) > session.max_chars:
        await message.channel.send(
            f"⚠️ {message.author.mention} 発言が文字数制限（{session.max_chars}文字）を超えています。"
        )
        return
    
    # 禁止コンテンツチェック
    is_safe, reason = check_prohibited_content(message.content)
    
    if not is_safe:
        violation_count = session.add_violation(message.author.id)
        
        if violation_count >= 3:
            # 3回目の違反で強制終了
            end_embed = discord.Embed(
                title="🚫 ディベート強制終了",
                description=(
                    f"{message.author.mention} が規約違反を3回行ったため、\n"
                    "ディベートを強制終了しました。\n\n"
                    "**勝敗判定は行いません。**"
                ),
                color=discord.Color.red()
            )
            await message.channel.send(embed=end_embed)
            del bot.active_sessions[message.channel.id]
            return
        
        elif violation_count == 2:
            await message.channel.send(
                f"⚠️ **警告（{violation_count}/3）:** {message.author.mention}\n"
                f"理由: {reason}\n"
                "この発言は無効化されました。次回の違反でセッション終了となります。"
            )
            await message.delete()
            return
        
        else:
            await message.channel.send(
                f"⚠️ **警告（{violation_count}/3）:** {message.author.mention}\n"
                f"理由: {reason}"
            )
            return
    
    # ログに記録
    session.log_message(message.author, message.content)
    
    # ターンを進める
    session.current_turn += 1
    
    # 発言回数チェック
    author_turn_count = sum(1 for entry in session.debate_log if entry['author_id'] == message.author.id)
    
    if author_turn_count >= session.message_limit:
        # 両者が制限に達したかチェック
        other_debater = session.debaters[1] if message.author == session.debaters[0] else session.debaters[0]
        other_turn_count = sum(1 for entry in session.debate_log if entry['author_id'] == other_debater.id)
        
        if other_turn_count >= session.message_limit:
            # ディベート終了
            await end_debate(session)
            return
        else:
            await message.channel.send(
                f"ℹ️ {message.author.mention} は発言制限に達しました。\n"
                f"{other_debater.mention} の最終発言をお待ちください。"
            )
    
    # 次のターンを通知
    next_debater = session.get_current_debater()
    if next_debater:
        remaining = session.message_limit - sum(
            1 for entry in session.debate_log if entry['author_id'] == next_debater.id
        )
        await message.channel.send(
            f"💬 次の発言者: {next_debater.mention} （残り{remaining}回）"
        )


async def end_debate(session: DebateSession):
    """ディベート終了処理"""
    
    session.is_active = False
    
    # 評価実行
    scores = evaluate_debate(session.debate_log)
    
    # 結果Embed作成
    result_embed = discord.Embed(
        title="📊 ディベート終了 - 評価結果",
        description=(
            "以下は構成評価です。正誤や優劣を示すものではありません。\n"
            "Botによる参考意見としてご覧ください。"
        ),
        color=discord.Color.purple()
    )
    
    # 各ディベーターのスコアを表示
    for i, debater in enumerate(session.debaters):
        score_data = scores.get(debater.id, {})
        
        side_label = "🔵 Side A" if i == 0 else "🔴 Side B"
        
        result_embed.add_field(
            name=f"{side_label}: {debater.display_name}",
            value=(
                f"論点の一貫性: {score_data.get('consistency', 0):.1f}/10\n"
                f"主張の明確さ: {score_data.get('clarity', 0):.1f}/10\n"
                f"反論の構造性: {score_data.get('structure', 0):.1f}/10\n"
                f"冷静な表現: {score_data.get('calmness', 0):.1f}/10\n"
                f"**総合: {score_data.get('total', 0):.1f}/40**"
            ),
            inline=False
        )
    
    # 総評（断定的表現を避ける）
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]['total'], reverse=True)
    
    if len(sorted_scores) >= 2:
        diff = sorted_scores[0][1]['total'] - sorted_scores[1][1]['total']
        winner_name = sorted_scores[0][1]['name']
        
        if diff < 3:
            conclusion = "両者ほぼ互角の評価となりました。"
        else:
            conclusion = f"総合的な構成評価では**{winner_name}側**がやや高いスコアでした。"
    else:
        conclusion = "評価を完了しました。"
    
    result_embed.add_field(
        name="📝 総評",
        value=conclusion,
        inline=False
    )
    
    result_embed.set_footer(text="お疲れ様でした！論理的思考の練習にご活用ください。")
    
    await session.channel.send(embed=result_embed)
    
    # セッション削除
    if session.channel.id in bot.active_sessions:
        del bot.active_sessions[session.channel.id]


@bot.tree.command(name="debate_stop", description="進行中のディベートを強制終了します（管理者のみ）")
async def stop_debate(interaction: discord.Interaction):
    """ディベート強制終了コマンド"""
    
    # 権限チェック
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ このコマンドは管理者のみ実行可能です。",
            ephemeral=True
        )
        return
    
    # セッションチェック
    if interaction.channel_id not in bot.active_sessions:
        await interaction.response.send_message(
            "ℹ️ このチャンネルで進行中のディベートはありません。",
            ephemeral=True
        )
        return
    
    # セッション削除
    del bot.active_sessions[interaction.channel_id]
    
    await interaction.response.send_message(
        "🛑 ディベートを強制終了しました。"
    )


@bot.tree.command(name="debate_help", description="Debate Arena Botの使い方を表示します")
async def show_help(interaction: discord.Interaction):
    """ヘルプコマンド"""
    
    help_embed = discord.Embed(
        title="📚 Debate Arena Bot - 使い方",
        description="論理的思考力を鍛える教育・娯楽用ディベートBotです",
        color=discord.Color.blue()
    )
    
    help_embed.add_field(
        name="🎯 コマンド一覧",
        value=(
            "`/debate` - ディベートセッションを作成（管理者のみ）\n"
            "`/debate_stop` - 進行中のディベートを強制終了（管理者のみ）\n"
            "`/debate_help` - このヘルプを表示"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="📋 参加方法",
        value=(
            "1. 管理者が `/debate` でセッションを作成\n"
            "2. 「参加する」ボタンをクリック\n"
            "3. 募集終了後、ランダムで2名が選出されます"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="⚠️ 禁止事項",
        value=(
            "• 人格攻撃・侮辱・誹謗中傷\n"
            "• 実在人物・団体への言及\n"
            "• 政治・宗教・差別的発言\n"
            "• 議題からの逸脱"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="📊 評価について",
        value=(
            "Botは議論の構造を評価しますが、\n"
            "**正誤や優劣を断定するものではありません**。\n"
            "参考意見としてご活用ください。"
        ),
        inline=False
    )
    
    help_embed.set_footer(text="Debate Arena Bot v1.0 - 規約準拠版")
    
    await interaction.response.send_message(embed=help_embed)


# Bot起動
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
