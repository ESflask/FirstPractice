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

import re

def _is_japanese(text):
    """テキストが日本語（ひらがな、カタカナ、漢字）を含んでいるか判定"""
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))

from app.services.deepl import translate_to_en, translate_to_ja, DeepLFatalError

def _translate_article(article_tuple):
    """個々の記事を翻訳するヘルパー関数"""
    article, target_lang = article_tuple
    title = article.get("title") or ""
    desc = article.get("description") or ""
    url = article.get("url")

    # キャッシュチェック
    cache_key = f"{url}_{target_lang}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]

    try:
        if target_lang == "ja":
            if _is_japanese(title):
                title_ja, description_ja = title, desc
            else:
                title_ja = translate_to_ja(title) if title else ""
                description_ja = translate_to_ja(desc) if desc else ""
            
            result = {
                "title_en": title, "title_ja": title_ja or title,
                "description_en": desc, "description_ja": description_ja or desc,
                "url": article["url"], "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"], "source": article["source"], "lang": "ja",
            }
        else:
            if _is_japanese(title):
                title_en = translate_to_en(title) if title else ""
                description_en = translate_to_en(desc) if desc else ""
            else:
                title_en, description_en = title, desc
            
            result = {
                "title_en": title_en or title, "title_ja": title,
                "description_en": description_en or desc, "description_ja": desc,
                "url": article["url"], "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"], "source": article["source"], "lang": "en",
            }
        translation_cache[cache_key] = result
        return result
    except DeepLFatalError:
        # DeepLが致命的なエラーを起こした場合、上位関数に伝える
        raise
    except Exception as e:
        # 一般的なエラーはスキップ
        print(f"[_translate_article] Error processing article: {e}")
        return {
            "title_en": title, "title_ja": title,
            "description_en": desc, "description_ja": desc,
            "url": article.get("url", ""), "urlToImage": article.get("urlToImage", ""),
            "publishedAt": article.get("publishedAt", ""), "source": article.get("source", ""),
            "lang": target_lang,
        }

def _fetch_fallback_articles(api_query, page_size, target_lang):
    """DeepL利用不可時の代替手段：ターゲット言語の記事のみを取得"""
    print(f"[_fetch_fallback_articles] DeepL is down. Fetching {target_lang} articles only...")
    with ThreadPoolExecutor(max_workers=3) as api_executor:
        futures = []
        lang_code = "jp" if target_lang == "ja" else "en"
        futures.append(api_executor.submit(fetch_full_articles, query=api_query, page_size=page_size, language=lang_code))
        
        lang_code_nd = "ja" if target_lang == "ja" else "en"
        futures.append(api_executor.submit(fetch_full_articles_newsdata, query=api_query, page_size=page_size, language=lang_code_nd))
        futures.append(api_executor.submit(fetch_full_articles_gnews, query=api_query, page_size=page_size, language=lang_code_nd))
        
        all_results = [f.result() for f in futures]
    
    combined = []
    seen_urls = set()
    for result_list in all_results:
        for art in result_list:
            if art.get("url") and art["url"] not in seen_urls:
                # ターゲット言語ですでに書かれているので翻訳なしで構造を合わせる
                combined.append({
                    "title_en": art.get("title") if target_lang == "en" else "",
                    "title_ja": art.get("title") if target_lang == "ja" else "",
                    "description_en": art.get("description") if target_lang == "en" else "",
                    "description_ja": art.get("description") if target_lang == "ja" else "",
                    "url": art.get("url"),
                    "urlToImage": art.get("urlToImage"),
                    "publishedAt": art.get("publishedAt"),
                    "source": art.get("source"),
                    "lang": target_lang
                })
                seen_urls.add(art["url"])
    return combined

def get_translated_articles(query="Apple", page_size=10, lang="ja"):
    """
    ニュース記事を取得し、言語に応じて翻訳する
    DeepLエラー時はターゲット言語の記事のみを再取得して返す
    """
    print(f"[get_translated_articles] Received query: '{query}', target lang: {lang}")
    keywords = query.split()
    api_query = " AND ".join(f'"{k}"' for k in keywords)

    try:
        # 通常の取得（多言語）
        with ThreadPoolExecutor(max_workers=5) as api_executor:
            futures = []
            futures.append(api_executor.submit(fetch_full_articles, query=api_query, page_size=page_size, language=None))
            futures.append(api_executor.submit(fetch_full_articles_newsdata, query=api_query, page_size=page_size, language="en"))
            futures.append(api_executor.submit(fetch_full_articles_newsdata, query=api_query, page_size=page_size, language="ja"))
            futures.append(api_executor.submit(fetch_full_articles_gnews, query=api_query, page_size=page_size, language="en"))
            futures.append(api_executor.submit(fetch_full_articles_gnews, query=api_query, page_size=page_size, language="ja"))
            all_results = [future.result() for future in futures]

        combined_articles = []
        for result_list in all_results:
            combined_articles.extend(result_list)

        all_articles = []
        seen_urls = set()
        for article in combined_articles:
            url = article.get("url")
            if url and url not in seen_urls:
                all_articles.append(article)
                seen_urls.add(url)

        # キーワードフィルタリング
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

    except DeepLFatalError:
        # DeepLが死んだ場合のフォールバック
        return _fetch_fallback_articles(api_query, page_size, lang)
    except Exception as e:
        print(f"[get_translated_articles] Error: {e}")
        return []
