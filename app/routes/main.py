from flask import Blueprint, render_template, request, jsonify
from app.services.aggregator import get_translated_articles
from app.models import Post
import os

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    """
    メインページ: 初期表示時は空のリストを表示（APIは呼ばない）
    """
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
    }
    return render_template("testapp/index.html", articles=[], firebase_config=firebase_config)


@main_bp.route("/about")
def about():
    """
    NewsAppについて ページ: 動的な統計情報を表示
    """
    # Placeholder for database counts until Firebase is fully integrated
    post_count = 0
    user_count = 0
    
    # ニュースソースのリスト（固定だが動的に見せる）
    sources = ["NewsAPI", "GNews", "NewsData.io", "DeepL"]
    
    return render_template("about.html", 
                           post_count=post_count, 
                           user_count=user_count,
                           sources=sources)


@main_bp.route("/api/update")
def api_update():
    """
    API更新エンドポイント: ニュース記事を取得してJSONで返す
    クエリパラメータ: lang=en または lang=ja (デフォルト: ja)
    """
    lang = request.args.get("lang", "ja")
    # デフォルトのクエリを"Apple"に設定
    articles = get_translated_articles(query="Apple", page_size=10, lang=lang)
    return jsonify(articles)


@main_bp.route("/api/search", methods=["GET"])
def search():
    """
    記事と投稿を検索
    """
    try:
        query = request.args.get("q", "").strip()
        lang = request.args.get("lang", "ja")

        if not query:
            return jsonify({"posts": [], "articles": []}), 200

        # Placeholder for post search until Firebase is fully integrated
        # Previously used SQLAlchemy: Post.query.filter(...)
        filtered_posts = []

        # NewsAPI/NewsData.io/GNewsで記事を検索
        print(f"[search] Searching external APIs for: {query}, lang={lang}")
        articles = get_translated_articles(query=query, page_size=10, lang=lang)

        # Note: filtered_posts is currently a list of dicts or objects. 
        # Since it is empty, we don't need to call .to_dict() on items.
        return jsonify(
            {"posts": filtered_posts, "articles": articles}
        ), 200

    except Exception as e:
        print(f"[search] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500
