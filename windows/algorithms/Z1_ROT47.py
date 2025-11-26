ALGO_NAME = "ROT47"
DESCRIPTION = "ROT47エンコード／デコード。ASCII 33-126に適用。"

def run(text):
    result = []
    for c in text:
        o = ord(c)
        if 33 <= o <= 126:
            result.append(chr(33 + ((o + 14) % 94)))
        else:
            result.append(c)
    return ''.join(result)
