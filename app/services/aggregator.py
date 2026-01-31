import os
from concurrent.futures import ThreadPoolExecutor
from app.services.deepl import translate_to_en, translate_to_ja
from app.services.gnews import fetch_full_articles_gnews
from app.services.newsapi import fetch_full_articles
from app.services.newsdata import fetch_full_articles_newsdata

# 翻訳処理を並列実行するためのスレッドプール
executor = ThreadPoolExecutor(max_workers=5)

def _translate_article(article_lang_tuple):
    """個々の記事を翻訳するヘルパー関数"""
    article, lang = article_lang_tuple
    try:
        if lang == "ja":
            # 英語→日本語に翻訳
            title_ja = translate_to_ja(article["title"])
            description_ja = translate_to_ja(article["description"])
            return {
                "title_en": article["title"],
                "title_ja": title_ja,
                "description_en": article["description"],
                "description_ja": description_ja,
                "url": article["url"],
                "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"],
                "source": article["source"],
                "lang": "ja",
            }
        else:
            # 日本語→英語に翻訳
            title_en = translate_to_en(article["title"])
            description_en = translate_to_en(article["description"])
            return {
                "title_en": title_en,
                "title_ja": article["title"],
                "description_en": description_en,
                "description_ja": article["description"],
                "url": article["url"],
                "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"],
                "source": article["source"],
                "lang": "en",
            }
    except Exception as e:
        print(f"[_translate_article] Error processing article: {e}")
        # エラー時も元の形式で返す
        return {
            "title_en": article.get("title", ""),
            "title_ja": article.get("title", ""),
            "description_en": article.get("description", ""),
            "description_ja": article.get("description", ""),
            "url": article.get("url", ""),
            "urlToImage": article.get("urlToImage", ""),
            "publishedAt": article.get("publishedAt", ""),
            "source": article.get("source", ""),
            "lang": lang,
        }


def get_translated_articles(query="Apple", page_size=10, lang="ja"):
    """
    ニュース記事を取得し、言語に応じて翻訳する（複数API並列対応、厳密なタイトル検索）
    """
    print(f"[get_translated_articles] Received query: '{query}'")

    # 1. 複数キーワードをAND条件に変換
    keywords = query.split()
    api_query = " AND ".join(f'"{k}"' for k in keywords)
    print(f"[get_translated_articles] Formatted API query: '{api_query}'")

    # 2. 各APIへのリクエストを並列で実行
    # executorを使って各APIのフェッチ処理をサブミット
    with ThreadPoolExecutor(max_workers=3) as api_executor:
        futures = []
        # NewsAPIは英語記事に強いため、lang="ja"の時に使用
        if lang == "ja":
            print("[get_translated_articles] Submitting fetch from NewsAPI...")
            futures.append(
                api_executor.submit(
                    fetch_full_articles, query=api_query, page_size=page_size
                )
            )

        # NewsData.ioは多言語対応
        newsdata_lang = "ja" if lang == "en" else "en"
        print(
            f"[get_translated_articles] Submitting fetch from NewsData.io with lang='{newsdata_lang}'..."
        )
        futures.append(
            api_executor.submit(
                fetch_full_articles_newsdata,
                query=api_query,
                page_size=page_size,
                language=newsdata_lang,
            )
        )

        # GNewsも多言語対応
        gnews_lang = "ja" if lang == "en" else "en"
        print(
            f"[get_translated_articles] Submitting fetch from GNews with lang='{gnews_lang}'..."
        )
        futures.append(
            api_executor.submit(
                fetch_full_articles_gnews,
                query=api_query,
                page_size=page_size,
                language=gnews_lang,
            )
        )

        # 全てのAPIからの結果を待つ
        all_results = [future.result() for future in futures]

    # 結果を結合
    combined_articles = []
    for result_list in all_results:
        combined_articles.extend(result_list)

    print(f"[get_translated_articles] Total articles fetched: {len(combined_articles)}")

    # 3. 記事を結合し、URLで重複を排除
    all_articles = []
    seen_urls = set()

    for article in combined_articles:
        url = article.get("url")
        if url and url not in seen_urls:
            all_articles.append(article)
            seen_urls.add(url)

    print(
        f"[get_translated_articles] Combined and deduplicated: {len(all_articles)} articles."
    )

    # 4. 厳密なタイトル検索
    filtered_articles = []
    lower_keywords = [k.lower() for k in keywords]
    for article in all_articles:
        title_lower = (article.get("title") or "").lower()
        if all(k in title_lower for k in lower_keywords):
            filtered_articles.append(article)

    print(
        f"[get_translated_articles] Filtered by title: {len(filtered_articles)} articles remain."
    )

    if not filtered_articles:
        return []

    # 5. 翻訳処理を並列実行 (既存のexecutorを使用)
    print(
        f"[get_translated_articles] Translating {len(filtered_articles)} articles in parallel..."
    )
    tasks = [(article, lang) for article in filtered_articles]
    result_articles = list(executor.map(_translate_article, tasks))

    print(
        f"[get_translated_articles] Returning {len(result_articles)} translated articles."
    )
    return result_articles
