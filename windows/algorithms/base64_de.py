import base64

ALGO_NAME = "Base64 デコード"
DESCRIPTION = "Base64 デコードを行います"

def run(text: str) -> str:
    try:
        return base64.b64decode(text.encode()).decode()
    except Exception:
        return ""
