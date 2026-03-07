import os

import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

AUTH_KEY = os.getenv("DEEPL_AUTH_KEY", "REDACTED_DEEPL_KEY")
BASE_URL = "https://api-free.deepl.com/v2/translate"


def _get_deepl_url(auth_key):
    """APIキーの末尾に応じてFree版かPro版のエンドポイントを返す"""
    if auth_key.endswith(":fx"):
        return "https://api-free.deepl.com/v2/translate"
    return "https://api.deepl.com/v2/translate"

class DeepLFatalError(Exception):
    """DeepLの認証エラーや利用制限などの致命的なエラー"""
    pass

def _request_translation(text, target_lang):
    """DeepL APIにリクエストを送信する共通関数"""
    if not text:
        return ""
    
    auth_key = os.getenv("DEEPL_AUTH_KEY", "REDACTED_DEEPL_KEY")
    url = _get_deepl_url(auth_key)
    
    headers = {
        "Authorization": f"DeepL-Auth-Key {auth_key}"
    }
    
    payload = {
        "text": text,
        "target_lang": target_lang
    }
    
    try:
        resp = requests.post(url, headers=headers, data=payload, timeout=10)
        
        # 403 Forbidden や 456 Quota Exceeded は致命的エラーとして扱う
        if resp.status_code in [403, 456]:
            print(f"[DeepL] Fatal Error {resp.status_code}: {resp.text}")
            raise DeepLFatalError(f"DeepL API is unavailable (Status: {resp.status_code})")
            
        resp.raise_for_status()
        translations = resp.json().get("translations", [])
        return translations[0].get("text", "") if translations else ""
    except requests.exceptions.RequestException as exc:
        print(f"[DeepL] Request failed ({target_lang}): {exc}")
        return ""

def translate_to_ja(text):
    """DeepLで日本語に翻訳"""
    return _request_translation(text, "JA")

def translate_to_en(text):
    """DeepLで英語に翻訳"""
    return _request_translation(text, "EN")


if __name__ == "__main__":
    print("Test JA→EN:", translate_to_en("こんにちは、私の名前は太郎です"))
    print("Test EN→JA:", translate_to_ja("Hello my name is taro nice to meet you"))
