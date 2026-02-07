import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from firebase_admin import firestore
from app.utils.files import allowed_file

posts_bp = Blueprint('posts', __name__)

@posts_bp.route("", methods=["GET"])
def get_posts():
    """
    ユーザー投稿を取得 (Firestore)
    """
    try:
        db = current_app.db
        if not db:
            return jsonify([]), 200

        posts_ref = db.collection('posts')
        query = posts_ref.order_by('timestamp', direction=firestore.Query.DESCENDING)
        docs = query.stream()

        posts = []
        for doc in docs:
            post_data = doc.to_dict()
            # タイムスタンプの変換 (Firestore Timestamp to ISO string)
            if 'timestamp' in post_data and post_data['timestamp']:
                # firestore.SERVER_TIMESTAMPの場合は取得時にdatetimeになることがある
                ts = post_data['timestamp']
                if hasattr(ts, 'isoformat'):
                    post_data['timestamp'] = ts.isoformat()
            
            # クライアント互換性のためのフィールド追加
            post_data['id'] = doc.id
            post_data['type'] = 'user_post'
            
            # author情報を取得 (本来はjoinするか、投稿時に非正規化して埋め込むべき)
            # ここでは簡易的に post_data に含まれていると仮定するか、
            # user_email から引く実装にするが、パフォーマンスのため一旦埋め込み期待
            if 'user_email' in post_data and 'author_email' not in post_data:
                post_data['author_email'] = post_data['user_email']

            posts.append(post_data)

        return jsonify(posts)
    except Exception as e:
        print(f"[get_posts] Error: {e}")
        return jsonify({"error": str(e)}), 500


@posts_bp.route("", methods=["POST"])
def create_post():
    """
    新しい投稿を作成 (Firestore)
    """
    user_id = session.get("user_id")
    user_email = session.get("user_email")
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
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                
                # Local Upload (Phase 4 Step 1: Keep local upload, save URL to Firestore)
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                image_url = f"/static/uploads/{filename}"
                
                # TODO: Phase 4 Step 2: Upload to Firebase Storage
                # bucket = storage.bucket()
                # blob = bucket.blob(filename)
                # blob.upload_from_filename(filepath)
                # blob.make_public()
                # image_url = blob.public_url

        # Firestoreに保存
        db = current_app.db
        if not db:
            return jsonify({"error": "Database not connected"}), 500

        new_post_data = {
            'title': title,
            'description': description,
            'image': image_url,
            'user_id': user_id,
            'user_email': user_email,
            'timestamp': firestore.SERVER_TIMESTAMP
        }

        # postsコレクションに追加
        update_time, post_ref = db.collection('posts').add(new_post_data)
        
        # レスポンス用にIDを追加
        new_post_data['id'] = post_ref.id
        # datetimeオブジェクトはJSONシリアライズできないので変換
        new_post_data['timestamp'] = datetime.now().isoformat()

        print(f"[create_post] Created new post in Firestore: {title}")
        return jsonify(new_post_data), 201

    except Exception as e:
        print(f"[create_post] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500