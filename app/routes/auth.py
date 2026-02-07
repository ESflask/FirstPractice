import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session, current_app
from firebase_admin import auth, firestore
from werkzeug.utils import secure_filename
from app.utils.files import allowed_file

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Firebase ID Tokenを使用してログインし、セッションを作成する
    """
    try:
        id_token = request.json.get("idToken")
        if not id_token:
            return jsonify({"error": "ID Token required"}), 400

        # IDトークンの検証
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email')

        # Firestoreからユーザー情報を取得、なければ作成
        db = current_app.db
        if db:
            user_ref = db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                # 新規ユーザーとして保存
                user_data = {
                    'email': email,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'icon': decoded_token.get('picture', "")
                }
                user_ref.set(user_data)
                print(f"[login] Created new user in Firestore: {email} ({uid})")
            else:
                print(f"[login] User logged in: {email} ({uid})")

        # セッションにログイン情報を保存
        session["user_id"] = uid
        session["user_email"] = email

        return jsonify({
            "uid": uid,
            "email": email,
            "message": "Login successful"
        }), 200

    except Exception as e:
        print(f"[login] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    ユーザーログアウト
    """
    session.clear()
    print("[logout] User logged out")
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/current", methods=["GET"])
def get_current_user():
    """
    現在のログインユーザー情報を取得
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"logged_in": False}), 200
    
    # Firestoreから最新情報を取得
    db = current_app.db
    user_data = {}
    if db:
        try:
            doc = db.collection('users').document(user_id).get()
            if doc.exists:
                user_data = doc.to_dict()
        except Exception as e:
            print(f"Error fetching user data: {e}")

    return jsonify(
        {
            "logged_in": True,
            "id": user_id,
            "email": session.get("user_email"),
            "icon": user_data.get("icon", ""),
            # "is_superuser": user_data.get("is_superuser", False) 
        }
    ), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    互換性のために残すが、クライアントサイドで登録を行うため
    基本的にはログインと同様の処理を行う
    """
    return login()


@auth_bp.route("/profile", methods=["PUT"])
def update_profile():
    """
    ユーザープロフィール更新 (Firestore)
    注意: パスワードやメールアドレスの変更は本来Firebase Client SDKで行うべき。
    ここではFirestore上のユーザーメタデータ(アイコンなど)の更新を行う。
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    db = current_app.db
    if not db:
        return jsonify({"error": "Database error"}), 500

    try:
        user_ref = db.collection('users').document(user_id)
        
        # アイコン更新
        icon_url = None
        if "icon" in request.files:
            file = request.files["icon"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"avatar_{timestamp}_{filename}"
                filepath = os.path.join(current_app.config["AVATARS_FOLDER"], filename)
                file.save(filepath)
                icon_url = f"/static/avatars/{filename}"

        updates = {}
        if icon_url:
            updates['icon'] = icon_url
        
        # EmailがフォームにあればFirestore側も更新しておく (Auth側と不整合になる可能性はあるが)
        new_email = request.form.get("email", "").strip()
        if new_email:
            updates['email'] = new_email

        if updates:
            user_ref.set(updates, merge=True)
            # セッション情報も更新
            if 'email' in updates:
                session['user_email'] = updates['email']

        print(f"[update_profile] Profile updated for user: {user_id}")
        return jsonify({"id": user_id, "icon": icon_url, "message": "Profile updated"}), 200

    except Exception as e:
        print(f"[update_profile] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500