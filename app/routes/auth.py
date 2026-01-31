import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app.models import db, User
from app.utils.files import allowed_file

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    新規ユーザー登録
    """
    try:
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # メールアドレスの重複チェック
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400

        # 新規ユーザー作成
        new_user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # セッションにログイン情報を保存
        session["user_id"] = new_user.id
        session["user_email"] = new_user.email

        print(f"[register] New user registered: {email}")
        return jsonify(
            {"id": new_user.id, "email": new_user.email, "icon": new_user.icon}
        ), 201

    except Exception as e:
        db.session.rollback()
        print(f"[register] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    ユーザーログイン
    """
    try:
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # ユーザーを検索
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # パスワード検証
        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        # セッションにログイン情報を保存
        session["user_id"] = user.id
        session["user_email"] = user.email

        print(f"[login] User logged in: {email}")
        return jsonify(
            {
                "id": user.id,
                "email": user.email,
                "icon": user.icon,
                "is_superuser": user.is_superuser,
            }
        ), 200

    except Exception as e:
        print(f"[login] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


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

    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({"logged_in": False}), 200

    return jsonify(
        {
            "logged_in": True,
            "id": user.id,
            "email": user.email,
            "icon": user.icon,
            "is_superuser": user.is_superuser,
        }
    ), 200


@auth_bp.route("/profile", methods=["PUT"])
def update_profile():
    """
    ユーザープロフィール更新
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # メールアドレス更新
        new_email = request.form.get("email", "").strip()
        if new_email and new_email != user.email:
            # 重複チェック
            if User.query.filter_by(email=new_email).first():
                return jsonify({"error": "Email already exists"}), 400
            user.email = new_email
            session["user_email"] = new_email

        # パスワード更新
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        if new_password:
            if not current_password:
                return jsonify({"error": "Current password required"}), 400
            if not check_password_hash(user.password_hash, current_password):
                return jsonify({"error": "Invalid current password"}), 401
            user.password_hash = generate_password_hash(new_password)

        # アイコン更新
        if "icon" in request.files:
            file = request.files["icon"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"avatar_{timestamp}_{filename}"
                filepath = os.path.join(current_app.config["AVATARS_FOLDER"], filename)
                file.save(filepath)
                user.icon = f"/static/avatars/{filename}"

        db.session.commit()

        print(f"[update_profile] Profile updated for user: {user.email}")
        return jsonify({"id": user.id, "email": user.email, "icon": user.icon}), 200

    except Exception as e:
        db.session.rollback()
        print(f"[update_profile] Error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500
