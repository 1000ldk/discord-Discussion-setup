"""
ユーティリティ関数群
"""

import re
from typing import Optional, List
from datetime import datetime, timedelta


def sanitize_text(text: str) -> str:
    """
    テキストをサニタイズ
    Discord特殊文字のエスケープなど
    """
    # Discordメンション防止
    text = text.replace('@everyone', '@\u200beveryone')
    text = text.replace('@here', '@\u200bhere')
    
    return text


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    テキストを指定文字数で切り詰め
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def format_timestamp(dt: datetime) -> str:
    """
    タイムスタンプをフォーマット
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def calculate_time_remaining(start_time: datetime, duration_minutes: int) -> str:
    """
    残り時間を計算して文字列で返す
    """
    end_time = start_time + timedelta(minutes=duration_minutes)
    remaining = end_time - datetime.now()
    
    if remaining.total_seconds() <= 0:
        return "終了"
    
    minutes = int(remaining.total_seconds() // 60)
    seconds = int(remaining.total_seconds() % 60)
    
    return f"{minutes}分{seconds}秒"


def extract_mentions(text: str) -> List[str]:
    """
    テキストからメンションを抽出
    """
    pattern = r'<@!?(\d+)>'
    return re.findall(pattern, text)


def count_characters_without_whitespace(text: str) -> int:
    """
    空白文字を除いた文字数をカウント
    """
    return len(re.sub(r'\s', '', text))


def is_url(text: str) -> bool:
    """
    URLかどうかを判定
    """
    url_pattern = r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+'
    return bool(re.match(url_pattern, text))


def validate_debate_message(text: str, max_chars: int) -> tuple[bool, Optional[str]]:
    """
    ディベートメッセージの妥当性を検証
    
    Returns:
        (is_valid, error_message)
    """
    # 空メッセージチェック
    if not text or text.isspace():
        return False, "空のメッセージは送信できません"
    
    # 文字数チェック
    if len(text) > max_chars:
        return False, f"文字数制限（{max_chars}文字）を超えています"
    
    # 最低文字数チェック
    if len(text) < 10:
        return False, "メッセージが短すぎます（最低10文字）"
    
    return True, None


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """
    キーワードを強調表示
    """
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f'**{keyword}**', text)
    
    return text


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    読了時間を計算（秒）
    """
    # 日本語の場合は文字数ベース
    char_count = len(text)
    # 1分あたり400-600文字と仮定
    reading_time_seconds = (char_count / 500) * 60
    
    return int(reading_time_seconds)


def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """
    プログレスバーを作成
    """
    if total == 0:
        return "█" * length
    
    filled = int((current / total) * length)
    empty = length - filled
    
    return "█" * filled + "░" * empty


def format_score(score: float, max_score: float = 10.0) -> str:
    """
    スコアをフォーマット
    """
    percentage = (score / max_score) * 100
    
    if percentage >= 80:
        emoji = "🟢"
    elif percentage >= 60:
        emoji = "🟡"
    elif percentage >= 40:
        emoji = "🟠"
    else:
        emoji = "🔴"
    
    return f"{emoji} {score:.1f}/{max_score:.1f}"
