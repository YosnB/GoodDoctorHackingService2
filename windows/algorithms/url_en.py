import urllib.parse

ALGO_NAME = "URLエンコード"
DESCRIPTION = "文字列をURLエンコードします。"

def run(text):
    return urllib.parse.quote(text)
