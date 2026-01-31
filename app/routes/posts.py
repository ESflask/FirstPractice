import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from app.models import db, Post
from app.utils.files import allowed_file

posts_bp = Blueprint('posts', __name__)

@posts_bp.route("", methods=["GET"])
def get_posts():
    """
    ユーザー投稿を取得
    """
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify([post.to_dict() for post in posts])


@posts_bp.route("", methods=["POST"])
def create_post():
    """
    新しい投稿を作成
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    try:
        title = request.form.get("title", "")
        description = request.form.get("description", "")

        if not title:
            return jsonify({"error": "Title is required"}), 400

        # 画像のアップロード処理
        image_url = ""
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # タイムスタンプを追加してユニークにする
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                image_url = f"/static/uploads/{filename}"

        # 新しい投稿を作成
        new_post = Post(
            title=title, description=description, image=image_url, user_id=user_id
        )

        db.session.add(new_post)
        db.session.commit()

        print(f"[create_post] Created new post: {title}")
        return jsonify(new_post.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"[create_post] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500
