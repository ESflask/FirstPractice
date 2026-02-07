# Firebase Migration Plan (Revised)

ユーザー情報と投稿データを SQLite から Firebase (Firestore) へ移行し、セキュアに運用するための手順書。

## 1. Firebase Console 設定

1. **プロジェクト作成**: [Firebase Console](https://console.firebase.google.com/) で新規プロジェクトを作成。
2. **Firestore 作成**: `Build` > `Firestore Database` > `Create database` (Start in **Test mode**)。
3. **Admin SDK キー取得**:
   - `Project settings` > `Service accounts` > `Python` を選択。
   - `Generate new private key` をクリック。
   - JSONファイルをダウンロードし、`serviceAccountKey.json` にリネームしてプロジェクトルートに配置。
   - **重要**: `.gitignore` に `serviceAccountKey.json` を追記してコミットしないこと。

## 2. ライブラリ導入

```bash
pip install firebase-admin python-dotenv
```

## 3. 環境変数の設定 (.env)

セキュリティと保守性のため、Firebaseのクライアント設定も `.env` で管理し、Flask経由でテンプレートに渡す。

**.env (例)**
```ini
# Firebase Client Config (Public but managed via env)
FIREBASE_API_KEY="AIzaSyD..."
FIREBASE_AUTH_DOMAIN="news-mobile-91125.firebaseapp.com"
FIREBASE_PROJECT_ID="news-mobile-91125"
FIREBASE_STORAGE_BUCKET="news-mobile-91125.firebasestorage.app"
FIREBASE_MESSAGING_SENDER_ID="982012188520"
FIREBASE_APP_ID="1:982012188520:web:..."
FIREBASE_MEASUREMENT_ID="G-7WR5KVPC00"

# Firebase Admin SDK (Server-side Secret)
GOOGLE_APPLICATION_CREDENTIALS="serviceAccountKey.json"
```

## 4. コード修正方針

### A. 設定の読み込み (`app/routes/main.py` 等)

Flask側で環境変数を読み込み、テンプレートへ渡す。

```python
import os
from flask import render_template

@main_bp.route("/")
def index():
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
    }
    return render_template("testapp/index.html", firebase_config=firebase_config)
```

### B. テンプレート修正 (`app/templates/testapp/index.html`)

ハードコードされた設定を削除し、Flaskから渡された変数を使用する。

```html
<script>
    // Flaskから渡された設定を使用 (tojsonフィルターで安全にJSON化)
    const firebaseConfig = {{ firebase_config | tojson }};
    
    // Initialize Firebase
    firebase.initializeApp(firebaseConfig);
    // ...
</script>
```

### C. サーバーサイド初期化 (`app/__init__.py`)

Admin SDK の初期化。

```python
import firebase_admin
from firebase_admin import credentials, firestore

def create_app():
    # ...
    # serviceAccountKey.json を使用して初期化
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    
    app.db = firestore.client()
    # ...
```

## 5. データ構造 (Firestore)

**Collection: `users`**
- Document ID: `email`
- Fields: `password_hash`, `icon`, `created_at`

**Collection: `posts`**
- Document ID: `Auto-ID`
- Fields: `title`, `description`, `image`, `user_email`, `timestamp`