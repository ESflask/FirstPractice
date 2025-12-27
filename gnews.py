# gnews.py

import os
import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

API_KEY = os.getenv("GNEWS_API_KEY")
BASE_URL = "https://gnews.io/api/v4/search"


def fetch_full_articles_gnews(
    query: str,
    page_size: int = 5,
    language: str = "en",
):
    """
    GNews APIから記事を取得し、NewsAPIの形式に合わせた辞書のリストを返す
    """
    if not API_KEY:
        print("[GNews] API key is not set. Skipping fetch.")
        return []

    # GNewsの言語コードに変換 (例: ja -> ja, en -> en)
    lang_map = {"ja": "ja", "en": "en"}
    gnews_lang = lang_map.get(language, "en")

    try:
        params = {
            "apikey": API_KEY,
            "q": query,
            "lang": gnews_lang,
            "max": page_size,
            "in": "title",  # GNewsはタイトルでの検索をサポートしている
        }

        resp = requests.get(BASE_URL, params=params, timeout=15)

        if not resp.ok:
            try:
                detail = resp.json().get("errors", resp.text)
            except (ValueError, AttributeError):
                detail = resp.text or f"HTTP {resp.status_code}"
            print(f"[GNews] Request failed ({resp.status_code}): {detail}. Returning empty list.")
            return []

        json_data = resp.json()
        articles = json_data.get("articles", [])
        
        # NewsAPIの形式に正規化する
        normalized_articles = []
        for article in articles:
            normalized_article = {
                "title": (article.get("title") or "").strip(),
                "description": (article.get("description") or "").strip(),
                "url": (article.get("url") or "").strip(),
                "urlToImage": (article.get("image") or "").strip(),
                "publishedAt": (article.get("publishedAt") or "").strip(),
                "source": (article.get("source", {}).get("name") or "").strip(),
            }
            # タイトルとURLがある記事のみ追加
            if normalized_article["title"] and normalized_article["url"]:
                normalized_articles.append(normalized_article)
        
        return normalized_articles

    except requests.exceptions.Timeout:
        print("[GNews] Request timeout. Returning empty list.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[GNews] Request exception: {e}. Returning empty list.")
        return []
    except Exception as e:
        print(f"[GNews] Unexpected error: {e}. Returning empty list.")
        return []

if __name__ == "__main__":
    # テスト用
    test_query = "Tesla AND new AND model"
    print(f"Fetching articles from GNews for query: '{test_query}'")
    fetched_articles = fetch_full_articles_gnews(query=test_query, page_size=5)
    if fetched_articles:
        for idx, article in enumerate(fetched_articles, 1):
            print(f"{idx}. {article['title']} ({article['source']})")
    else:
        print("No articles found.")
