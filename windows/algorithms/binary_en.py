ALGO_NAME = "2進数エンコード"
DESCRIPTION = "入力された文字列を2進数文字列に変換します。スペース区切り。"

def run(text):
    return ' '.join([format(ord(c), '08b') for c in text])
