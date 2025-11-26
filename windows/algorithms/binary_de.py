ALGO_NAME = "2進数デコード"
DESCRIPTION = "入力された2進数文字列をデコードして文字列に変換します。スペースで区切られた2進数を想定。"

def run(text):
    try:
        chars = text.strip().split()
        return ''.join([chr(int(c, 2)) for c in chars])
    except:
        return "無効な2進数"
