import os

import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

AUTH_KEY = os.getenv("DEEPL_AUTH_KEY", "REDACTED_DEEPL_KEY")
BASE_URL = "https://api-free.deepl.com/v2/translate"


def translate_to_ja(text):
    """DeepLで受け取った英語テキストを日本語に翻訳"""
    if not text:
        return ""

    payload = {"auth_key": AUTH_KEY, "text": text, "target_lang": "JA"}
    try:
        resp = requests.post(BASE_URL, data=payload, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"[translate_to_ja] DeepL request failed: {exc}")
        return ""

    translations = resp.json().get("translations", [])
    if not translations:
        return ""
    return translations[0].get("text", "")


def translate_to_en(text):
    """DeepLで受け取った日本語テキストを英語に翻訳"""
    if not text:
        return ""

    payload = {"auth_key": AUTH_KEY, "text": text, "target_lang": "EN"}
    try:
        resp = requests.post(BASE_URL, data=payload, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"[translate_to_en] DeepL request failed: {exc}")
        return ""

    translations = resp.json().get("translations", [])
    if not translations:
        return ""
    return translations[0].get("text", "")


if __name__ == "__main__":
    print("Test JA→EN:", translate_to_en("こんにちは、私の名前は太郎です"))
    print("Test EN→JA:", translate_to_ja("Hello my name is taro nice to meet you"))
