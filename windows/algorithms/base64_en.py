import base64

ALGO_NAME = "Base64 エンコード"
DESCRIPTION = "Base64 エンコードを行います"

def run(text: str) -> str:
    try:
        return base64.b64encode(text.encode()).decode()
    except Exception:
        return ""
