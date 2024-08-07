import app.src.translation_agent as ta
import re

from difflib import Differ
"""
使用langgraph的原因:
langchain直接call ollamafunction帶image的prompt會報錯

因此拆成3個agent:

"""


def huanik(source_lang, target_lang, source_text, country, max_tokens):

    ta.model_load()

    source_text = re.sub(r'\n+', '\n', source_text)

    init_translation, reflect_translation, final_translation = ta.translate(
        source_lang=source_lang,
        target_lang=target_lang,
        source_text=source_text,
        country=country,
        max_tokens=max_tokens,
    )

    return final_translation
