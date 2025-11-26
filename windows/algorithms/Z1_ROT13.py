ALGO_NAME = "ROT13"
DESCRIPTION = "ROT13エンコード／デコード。アルファベットのみ対象。"

def run(text):
    result = []
    for c in text:
        if 'a' <= c <= 'z':
            result.append(chr((ord(c)-97+13)%26 + 97))
        elif 'A' <= c <= 'Z':
            result.append(chr((ord(c)-65+13)%26 + 65))
        else:
            result.append(c)
    return ''.join(result)
