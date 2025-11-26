ALGO_NAME = "Caesar 暗号"
DESCRIPTION = "Caesar暗号。shiftで文字をシフト。正は前、負は後にシフト。"
VARIABLES = {"shift": 50}  # GUI上で可変。負も可能

def run(text: str) -> str:
    s = VARIABLES.get("shift", 0)
    result = ""
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result += chr((ord(c) - base + s) % 26 + base)
        else:
            result += c
    return result
