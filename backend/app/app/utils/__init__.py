# import os
# from typing import List

# from huggingface_hub import snapshot_download
# from loguru import logger
# from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


# def load_t5_small_pipe():
#     model_path = "t5-small"
#     logger.info(f"loading... {model_path}")

#     tokenizer = AutoTokenizer.from_pretrained(model_path)
#     model = AutoModelForSeq2SeqLM.from_pretrained(
#         model_path,
#         low_cpu_mem_usage=True,
#     )
#     return pipeline(
#         "translation_en_to_zh-TW",
#         model=model,
#         tokenizer=tokenizer,
#         framework="pt",
#     )


# t5_pipe = load_t5_small_pipe()
