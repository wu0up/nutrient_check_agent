import re

def extract_translation(text):
    # 使用正則表達式提取<TRANSLATION>和</TRANSLATION>之間的內容
    match = re.search(r'<TRANSLATION>(.*?)</TRANSLATION>', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text