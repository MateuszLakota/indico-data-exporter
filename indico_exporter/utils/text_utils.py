import re


def normalize_text(text: str, newline_replacement: str):
    if not text:
        return ""

    text = text.replace("\r\n", newline_replacement)
    text = text.replace("\r", newline_replacement)
    text = text.replace("\n", newline_replacement)

    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()
