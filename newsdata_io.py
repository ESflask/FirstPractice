# newsdata_io.py

import os
import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

API_KEY = os.getenv("NEWSDATA_IO_API_KEY")
BASE_URL = "https://newsdata.io/api/1/news"


def fetch_full_articles_newsdata(
    query: str,
    page_size: int = 5,
    language: str = "en",
):
    """
    NewsData.io APIから記事を取得し、NewsAPIの形式に合わせた辞書のリストを返す
    """
    if not API_KEY:
        print("[NewsData.io] API key is not set. Skipping fetch.")
        return []

    try:
        params = {
            "apikey": API_KEY,
            "q": query,
            "language": language,
            "size": page_size,
        }

        resp = requests.get(BASE_URL, params=params, timeout=15)

        if not resp.ok:
            try:
                detail = resp.json().get("results", {}).get("message", resp.text)
            except (ValueError, AttributeError):
                detail = resp.text or f"HTTP {resp.status_code}"
            print(f"[NewsData.io] Request failed ({resp.status_code}): {detail}. Returning empty list.")
            return []

        json_data = resp.json()
        articles = json_data.get("results", [])
        
        # NewsAPIの形式に正規化する
        normalized_articles = []
        for article in articles:
            normalized_article = {
                "title": (article.get("title") or "").strip(),
                "description": (article.get("description") or "").strip(),
                "url": (article.get("link") or "").strip(),
                "urlToImage": (article.get("image_url") or "").strip(),
                "publishedAt": (article.get("pubDate") or "").strip(),
                "source": (article.get("source_id") or "").strip(),
            }
            # タイトルとURLがある記事のみ追加
            if normalized_article["title"] and normalized_article["url"]:
                normalized_articles.append(normalized_article)
        
        return normalized_articles

    except requests.exceptions.Timeout:
        print("[NewsData.io] Request timeout. Returning empty list.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[NewsData.io] Request exception: {e}. Returning empty list.")
        return []
    except Exception as e:
        print(f"[NewsData.io] Unexpected error: {e}. Returning empty list.")
        return []

if __name__ == "__main__":
    # テスト用
    test_query = "Tesla AND new AND model"
    print(f"Fetching articles for query: '{test_query}'")
    fetched_articles = fetch_full_articles_newsdata(query=test_query, page_size=5)
    if fetched_articles:
        for idx, article in enumerate(fetched_articles, 1):
            print(f"{idx}. {article['title']} ({article['source']})")
    else:
        print("No articles found.")
