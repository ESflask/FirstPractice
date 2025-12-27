import os
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY", "eec9d227dcdf47b9bfa9b53a9f8d4042")
BASE_URL = "https://newsapi.org/v2/everything"


def _default_time_range(days_back: int = 7) -> tuple[str, str]:
    """Return ISO8601 strings covering the last `days_back` days."""
    to_dt = datetime.now(timezone.utc)
    from_dt = to_dt - timedelta(days=days_back)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return from_dt.strftime(fmt), to_dt.strftime(fmt)


def fetch_articles(
    query="(Apple)",
    from_ts: str | None = None,
    to_ts: str | None = None,
    page_size: int = 5,
    field: str = "title",
):
    """
    ニュース記事を取得し、指定フィールドのリストを返す
    エラー時（レート制限、ネットワークエラーなど）は空リストを返す
    """
    try:
        if not from_ts or not to_ts:
            default_from, default_to = _default_time_range()
            from_ts = from_ts or default_from
            to_ts = to_ts or default_to

        params = {
            "q": query,
            "from": from_ts,
            "to": to_ts,
            "sortBy": "relevancy",
            "pageSize": page_size,
            "apiKey": API_KEY,
        }
        
        resp = requests.get(BASE_URL, params=params, timeout=10)
        
        # すべてのHTTPエラーをraise_for_status()の前にチェックして空リストを返す
        if not resp.ok:
            try:
                detail = resp.json().get("message", resp.text)
            except (ValueError, AttributeError):
                detail = resp.text or f"HTTP {resp.status_code}"
            
            if resp.status_code == 429:
                print(f"[NewsAPI] Rate limit exceeded (429): {detail}. Returning empty list.")
            elif resp.status_code >= 500:
                print(f"[NewsAPI] Server error ({resp.status_code}): {detail}. Returning empty list.")
            else:
                print(f"[NewsAPI] Request failed ({resp.status_code}): {detail}. Returning empty list.")
            return []
        
        # レスポンスのパース
        try:
            json_data = resp.json()
        except ValueError as e:
            print(f"[NewsAPI] Failed to parse JSON response: {e}. Returning empty list.")
            return []
        
        articles = json_data.get("articles", [])
        values = []
        for article in articles:
            text = article.get(field) or ""
            if text.strip():
                values.append(text.strip())
        return values
        
    except requests.exceptions.Timeout:
        print(f"[NewsAPI] Request timeout. Returning empty list.")
        return []
    except requests.exceptions.ConnectionError as e:
        print(f"[NewsAPI] Connection error: {e}. Returning empty list.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[NewsAPI] Request exception: {e}. Returning empty list.")
        return []
    except Exception as e:
        print(f"[NewsAPI] Unexpected error: {e}. Returning empty list.")
        return []


def fetch_full_articles(
    query="(Apple)",
    from_ts: str | None = None,
    to_ts: str | None = None,
    page_size: int = 5,
):
    """
    ニュース記事を取得し、記事全体（タイトル、説明、URLなど）のリストを返す
    エラー時（レート制限、ネットワークエラーなど）は空リストを返す
    """
    try:
        params = {
            "q": query,
            "sortBy": "publishedAt",  # 最新の記事順に並べる
            "pageSize": page_size,
            "apiKey": API_KEY,
        }
        
        # 日時範囲が指定されている場合のみ追加
        if from_ts:
            params["from"] = from_ts
        if to_ts:
            params["to"] = to_ts
        
        resp = requests.get(BASE_URL, params=params, timeout=10)
        
        # すべてのHTTPエラーをraise_for_status()の前にチェックして空リストを返す
        if not resp.ok:
            try:
                detail = resp.json().get("message", resp.text)
            except (ValueError, AttributeError):
                detail = resp.text or f"HTTP {resp.status_code}"
            
            if resp.status_code == 429:
                print(f"[NewsAPI] Rate limit exceeded (429): {detail}. Returning empty list.")
            elif resp.status_code >= 500:
                print(f"[NewsAPI] Server error ({resp.status_code}): {detail}. Returning empty list.")
            else:
                print(f"[NewsAPI] Request failed ({resp.status_code}): {detail}. Returning empty list.")
            return []
        
        # レスポンスのパース
        try:
            json_data = resp.json()
        except ValueError as e:
            print(f"[NewsAPI] Failed to parse JSON response: {e}. Returning empty list.")
            return []
        
        articles = json_data.get("articles", [])
        result = []
        for article in articles:
            article_data = {
                "title": (article.get("title") or "").strip(),
                "description": (article.get("description") or "").strip(),
                "url": (article.get("url") or "").strip(),
                "urlToImage": (article.get("urlToImage") or "").strip(),
                "publishedAt": (article.get("publishedAt") or "").strip(),
                "source": (article.get("source", {}).get("name") or "").strip(),
            }
            # タイトルまたは説明がある記事のみ追加
            if article_data["title"] or article_data["description"]:
                result.append(article_data)
        return result
        
    except requests.exceptions.Timeout:
        print(f"[NewsAPI] Request timeout. Returning empty list.")
        return []
    except requests.exceptions.ConnectionError as e:
        print(f"[NewsAPI] Connection error: {e}. Returning empty list.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[NewsAPI] Request exception: {e}. Returning empty list.")
        return []
    except Exception as e:
        print(f"[NewsAPI] Unexpected error: {e}. Returning empty list.")
        return []


async def fetch_full_articles_async(
    query="(Apple)",
    from_ts: str | None = None,
    to_ts: str | None = None,
    page_size: int = 5,
):
    """
    ニュース記事を取得し、記事全体（タイトル、説明、URLなど）のリストを返す (Async)
    """
    try:
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": API_KEY,
        }
        
        if from_ts:
            params["from"] = from_ts
        if to_ts:
            params["to"] = to_ts
            
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(BASE_URL, params=params, timeout=10)
                
                if resp.status_code != 200:
                    detail = resp.text
                    print(f"[NewsAPI] Request failed ({resp.status_code}): {detail}. Returning empty list.")
                    return []
                    
                json_data = resp.json()
                
            except httpx.RequestError as e:
                print(f"[NewsAPI] Async request error: {e}. Returning empty list.")
                return []
            except ValueError as e:
                print(f"[NewsAPI] Failed to parse JSON response: {e}. Returning empty list.")
                return []
        
        articles = json_data.get("articles", [])
        result = []
        for article in articles:
            article_data = {
                "title": (article.get("title") or "").strip(),
                "description": (article.get("description") or "").strip(),
                "url": (article.get("url") or "").strip(),
                "urlToImage": (article.get("urlToImage") or "").strip(),
                "publishedAt": (article.get("publishedAt") or "").strip(),
                "source": (article.get("source", {}).get("name") or "").strip(),
            }
            if article_data["title"] or article_data["description"]:
                result.append(article_data)
        return result
        
    except Exception as e:
        print(f"[NewsAPI] Unexpected error in async fetch: {e}. Returning empty list.")
        return []


if __name__ == "__main__":
    for idx, title in enumerate(fetch_articles(page_size=15), start=1):
        print(f"{idx}. {title}")
