"""
アルファベットを数字に変換するエンコーダ
A=1, B=2, ..., Z=26（大文字小文字両対応）
記号や数字はそのまま保持
"""

ALGO_NAME = "アルファベット→数字"
DESCRIPTION = "アルファベットを対応する数字に変換します（A=1, B=2,...,Z=26）"

def run(text: str) -> str:
    """
    アルファベットを数字に変換
    大文字・小文字どちらでも同じ数字に変換
    例: ABC → 123, abc → 123
    """
    try:
        result = []
        for char in text:
            if char.isalpha():
                # 大文字小文字を区別せずに変換
                pos = ord(char.upper()) - ord('A') + 1
                result.append(str(pos))
            else:
                # アルファベット以外はそのまま保持
                result.append(char)
        return ''.join(result)
    except Exception:
        return ""
