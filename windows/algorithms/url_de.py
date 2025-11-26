import urllib.parse

ALGO_NAME = "URLデコード"
DESCRIPTION = "URLエンコードされた文字列をデコードします。"

def run(text):
    try:
        return urllib.parse.unquote(text)
    except:
        return "無効なURL文字列"
