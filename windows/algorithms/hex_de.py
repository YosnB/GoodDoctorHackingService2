ALGO_NAME = "16進数デコード"
DESCRIPTION = "16進数文字列をデコードして文字列に変換します。スペース区切りまたは連続16進数も対応。"

def run(text):
    try:
        text = text.replace(' ', '')
        return bytes.fromhex(text).decode('utf-8', errors='replace')
    except:
        return "無効な16進数"
