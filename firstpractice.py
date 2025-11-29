import os
from flask import Flask, render_template
from dotenv import load_dotenv
from deepl import translate_to_ja
from newsapi import fetch_full_articles

# Flaskのインスタンス作成
app = Flask(__name__)

# 環境変数の読み込み
load_dotenv()

# 記事を取得して翻訳する関数
def get_translated_articles(query="Apple", page_size=5):
    """
    ニュース記事を取得し、タイトルと説明を日本語に翻訳する
    
    Args:
        query: 検索クエリ
        page_size: 取得する記事数
    
    Returns:
        翻訳済み記事のリスト
    """
    # 記事を取得
    articles = fetch_full_articles(query=query, page_size=page_size)
    
    translated_articles = []
    for article in articles:
        # タイトルと説明を翻訳
        title_ja = translate_to_ja(article["title"]) if article["title"] else ""
        description_ja = translate_to_ja(article["description"]) if article["description"] else ""
        
        translated_article = {
            "title_en": article["title"],
            "title_ja": title_ja,
            "description_en": article["description"],
            "description_ja": description_ja,
            "url": article["url"],
            "urlToImage": article["urlToImage"],  # 画像URLをHTMLテンプレートに渡す
            "publishedAt": article["publishedAt"],
            "source": article["source"],
        }
        translated_articles.append(translated_article)
    
    return translated_articles


@app.route('/')
def index():
    """
    メインページ: 翻訳済みのニュース記事を表示
    """
    # 記事を取得して翻訳
    articles = get_translated_articles(query="Apple", page_size=5)
    
    return render_template(
        'testapp/index.html',
        articles=articles
    )


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8000)
