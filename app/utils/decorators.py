from functools import wraps
from flask import session, jsonify, current_app

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        db = current_app.db
        if not db:
             return jsonify({"error": "Database error"}), 500

        try:
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return jsonify({"error": "User not found"}), 403
            
            user_data = user_doc.to_dict()
            if not user_data.get('is_superuser', False):
                return jsonify({"error": "Admin access required"}), 403

        except Exception as e:
            print(f"Admin check error: {e}")
            return jsonify({"error": "Authorization check failed"}), 500

        return f(*args, **kwargs)

    return decorated_function