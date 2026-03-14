import os
from flask import Blueprint, render_template, request, jsonify, current_app
from firebase_admin import firestore
from app.services.aggregator import get_translated_articles

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
    クエリパラメータ: q (検索ワード), lang=en または lang=ja (デフォルト: ja)
    """
    query = request.args.get("q", "Apple")
    lang = request.args.get("lang", "ja")
    # クエリパラメータ 'q' があればそれを使用、なければデフォルトの 'Apple'
    articles = get_translated_articles(query=query, page_size=10, lang=lang)
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

        # Firestoreから投稿を取得してPython側でフィルタリング
        # (Firestoreは全文検索非対応のため)
        filtered_posts = []
        db = current_app.config.get("FIREBASE_DB")
        if db:
            try:
                docs = db.collection('posts').order_by(
                    'timestamp', direction=firestore.Query.DESCENDING
                ).limit(200).stream()
                query_lower = query.lower()
                for doc in docs:
                    data = doc.to_dict()
                    title = (data.get('title') or '').lower()
                    desc = (data.get('description') or '').lower()
                    if query_lower in title or query_lower in desc:
                        data['id'] = doc.id
                        data['type'] = 'user_post'
                        ts = data.get('timestamp')
                        if ts and hasattr(ts, 'isoformat'):
                            data['timestamp'] = ts.isoformat()
                        filtered_posts.append(data)
            except Exception as e:
                print(f"[search] Firestore error: {e}")

        # NewsAPI/NewsData.io/GNewsで記事を検索
        print(f"[search] Searching external APIs for: {query}, lang={lang}")
        articles = get_translated_articles(query=query, page_size=10, lang=lang)

        return jsonify({"posts": filtered_posts, "articles": articles}), 200

    except Exception as e:
        print(f"[search] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500
