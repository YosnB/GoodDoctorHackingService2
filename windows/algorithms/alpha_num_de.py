"""
数字をアルファベットに変換するデコーダ
1=A, 2=B, ..., 26=Z
数字はスペース区切りで与えられる
"""

ALGO_NAME = "数字→アルファベット"
DESCRIPTION = "数字を対応するアルファベットに変換します（スペース区切り: 1=A, 2=B,...,26=Z）"

def run(text: str) -> str:
    """
    数字をアルファベットに変換
    入力: スペース区切りの数字（例: "1 2 3"）
    出力: 対応するアルファベット（例: "ABC"）
    
    無効な数字（0, 27以上）は無視
    """
    try:
        result = []
        # スペースで分割
        tokens = text.split()
        
        for token in tokens:
            # 数字かどうかを確認
            if token.isdigit():
                num = int(token)
                # 1～26の範囲内なら変換
                if 1 <= num <= 26:
                    result.append(chr(ord('A') + num - 1))
                # 範囲外は無視
            else:
                # 数字でない場合はそのまま保持
                result.append(token)
        
        return ''.join(result)
    except Exception:
        return ""
