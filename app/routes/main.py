from flask import Blueprint, render_template, request, jsonify
from app.services.aggregator import get_translated_articles
from app.models import Post, db

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    """
    メインページ: 初期表示時は空のリストを表示（APIは呼ばない）
    """
    return render_template("testapp/index.html", articles=[])


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

        # ユーザー投稿を検索 (複数キーワードのAND検索に対応)
        keywords = query.lower().split()

        # Postのtitleとdescriptionに対して検索
        post_query = Post.query
        for keyword in keywords:
            post_query = post_query.filter(
                db.or_(
                    Post.title.ilike(f"%{keyword}%"),
                    Post.description.ilike(f"%{keyword}%"),
                )
            )
        filtered_posts = post_query.order_by(Post.timestamp.desc()).all()

        # NewsAPI/NewsData.io/GNewsで記事を検索
        print(f"[search] Searching external APIs for: {query}, lang={lang}")
        articles = get_translated_articles(query=query, page_size=10, lang=lang)

        return jsonify(
            {"posts": [post.to_dict() for post in filtered_posts], "articles": articles}
        ), 200

    except Exception as e:
        print(f"[search] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500
