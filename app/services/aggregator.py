import os
from concurrent.futures import ThreadPoolExecutor
from app.services.deepl import translate_to_en, translate_to_ja
from app.services.gnews import fetch_full_articles_gnews
from app.services.newsapi import fetch_full_articles
from app.services.newsdata import fetch_full_articles_newsdata

# 翻訳処理を並列実行するためのスレッドプール
executor = ThreadPoolExecutor(max_workers=5)

# 翻訳キャッシュ
translation_cache = {}

def _translate_article(article_tuple):
    """個々の記事を翻訳するヘルパー関数"""
    article, target_lang = article_tuple
    source_lang = article.get("language", "en") # デフォルトは英語とみなす
    url = article.get("url")

    # キャッシュチェック
    cache_key = f"{url}_{target_lang}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]

    try:
        # すでにターゲット言語の場合は翻訳不要
        if source_lang == target_lang:
            result = {
                "title_en": article["title"] if target_lang == "en" else "",
                "title_ja": article["title"] if target_lang == "ja" else "",
                "description_en": article["description"] if target_lang == "en" else "",
                "description_ja": article["description"] if target_lang == "ja" else "",
                "url": article["url"],
                "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"],
                "source": article["source"],
                "lang": target_lang,
            }
            translation_cache[cache_key] = result
            return result

        if target_lang == "ja":
            # 英語(または他)→日本語に翻訳
            # 空文字やNoneのチェック
            title = article.get("title") or ""
            desc = article.get("description") or ""
            
            title_ja = translate_to_ja(title) if title else ""
            description_ja = translate_to_ja(desc) if desc else ""
            
            result = {
                "title_en": title,
                "title_ja": title_ja or title,
                "description_en": desc,
                "description_ja": description_ja or desc,
                "url": article["url"],
                "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"],
                "source": article["source"],
                "lang": "ja",
            }
        else:
            # 日本語→英語に翻訳
            title = article.get("title") or ""
            desc = article.get("description") or ""

            title_en = translate_to_en(title) if title else ""
            description_en = translate_to_en(desc) if desc else ""
            
            result = {
                "title_en": title_en or title,
                "title_ja": title,
                "description_en": description_en or desc,
                "description_ja": desc,
                "url": article["url"],
                "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"],
                "source": article["source"],
                "lang": "en",
            }
        
        translation_cache[cache_key] = result
        return result
    except Exception as e:
        print(f"[_translate_article] Error processing article: {e}")
        return {
            "title_en": article.get("title", ""),
            "title_ja": article.get("title", ""),
            "description_en": article.get("description", ""),
            "description_ja": article.get("description", ""),
            "url": article.get("url", ""),
            "urlToImage": article.get("urlToImage", ""),
            "publishedAt": article.get("publishedAt", ""),
            "source": article.get("source", ""),
            "lang": target_lang,
        }


def get_translated_articles(query="Apple", page_size=10, lang="ja"):
    """
    ニュース記事を取得し、言語に応じて翻訳する（複数API並列対応、英語・日本語両方の記事を取得）
    """
    print(f"[get_translated_articles] Received query: '{query}', target lang: {lang}")

    keywords = query.split()
    api_query = " AND ".join(f'"{k}"' for k in keywords)

    # 各APIへのリクエストを並列実行
    with ThreadPoolExecutor(max_workers=5) as api_executor:
        futures = []
        
        # 1. NewsAPI (英語記事のみ)
        futures.append(api_executor.submit(fetch_full_articles, query=api_query, page_size=page_size))
        
        # 2. NewsData.io (英語と日本語両方取得)
        futures.append(api_executor.submit(fetch_full_articles_newsdata, query=api_query, page_size=page_size, language="en"))
        futures.append(api_executor.submit(fetch_full_articles_newsdata, query=api_query, page_size=page_size, language="ja"))
        
        # 3. GNews (英語と日本語両方取得)
        futures.append(api_executor.submit(fetch_full_articles_gnews, query=api_query, page_size=page_size, language="en"))
        futures.append(api_executor.submit(fetch_full_articles_gnews, query=api_query, page_size=page_size, language="ja"))

        all_results = [future.result() for future in futures]

    # 言語情報を付加しつつ結果を結合
    # (注: 各APIモジュールが 'language' キーを返すと想定)
    combined_articles = []
    for i, result_list in enumerate(all_results):
        # APIごとに言語を推定（本来はAPI側でセットすべきだが、ここで補完）
        # 0: NewsAPI(en), 1: NewsData(en), 2: NewsData(ja), 3: GNews(en), 4: GNews(ja)
        est_lang = "ja" if i in [2, 4] else "en"
        for art in result_list:
            if "language" not in art:
                art["language"] = est_lang
            combined_articles.append(art)

    # 重複排除
    all_articles = []
    seen_urls = set()
    for article in combined_articles:
        url = article.get("url")
        if url and url not in seen_urls:
            all_articles.append(article)
            seen_urls.add(url)

    # 厳密なタイトル検索
    filtered_articles = []
    lower_keywords = [k.lower() for k in keywords]
    for article in all_articles:
        title_lower = (article.get("title") or "").lower()
        if all(k in title_lower for k in lower_keywords):
            filtered_articles.append(article)

    if not filtered_articles:
        return []

    # 翻訳処理を並列実行
    tasks = [(article, lang) for article in filtered_articles]
    result_articles = list(executor.map(_translate_article, tasks))

    return result_articles
