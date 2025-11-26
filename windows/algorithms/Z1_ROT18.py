ALGO_NAME = "ROT18"
DESCRIPTION = "ROT13とROT5を組み合わせたエンコード／デコード。アルファベットと数字に適用。"

def run(text):
    result = []
    for c in text:
        if 'a' <= c <= 'z':
            result.append(chr((ord(c)-97+13)%26 + 97))
        elif 'A' <= c <= 'Z':
            result.append(chr((ord(c)-65+13)%26 + 65))
        elif '0' <= c <= '9':
            result.append(chr((ord(c)-48+5)%10 + 48))
        else:
            result.append(c)
    return ''.join(result)
