ALGO_NAME = "16進数エンコード"
DESCRIPTION = "文字列を16進数に変換します。スペース区切り。"

def run(text):
    return ' '.join([format(ord(c), '02x') for c in text])
