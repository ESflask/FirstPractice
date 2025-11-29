from datetime import datetime, timedelta, timezone
import os
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
    """ニュース記事を取得し、指定フィールドのリストを返す"""
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
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        try:
            detail = resp.json().get("message", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(
            f"NewsAPI request failed ({resp.status_code}): {detail}"
        ) from exc

    articles = resp.json().get("articles", [])
    values = []
    for article in articles:
        text = article.get(field) or ""
        if text.strip():
            values.append(text.strip())
    return values


def fetch_full_articles(
    query="(Apple)",
    from_ts: str | None = None,
    to_ts: str | None = None,
    page_size: int = 5,
):
    """ニュース記事を取得し、記事全体（タイトル、説明、URLなど）のリストを返す"""
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
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        try:
            detail = resp.json().get("message", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(
            f"NewsAPI request failed ({resp.status_code}): {detail}"
        ) from exc

    articles = resp.json().get("articles", [])
    result = []
    for article in articles:
        article_data = {
            "title": article.get("title", "").strip(),
            "description": article.get("description", "").strip(),
            "url": article.get("url", "").strip(),
            "urlToImage": article.get("urlToImage", "").strip(),  # 画像のURL（住所）を取得
            "publishedAt": article.get("publishedAt", "").strip(),
            "source": article.get("source", {}).get("name", "").strip(),
        }
        # タイトルまたは説明がある記事のみ追加
        if article_data["title"] or article_data["description"]:
            result.append(article_data)
    return result


if __name__ == "__main__":
    for idx, title in enumerate(fetch_articles(page_size=15), start=1):
        print(f"{idx}. {title}")
