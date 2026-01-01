# firstpractice.py (New)

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session
from dotenv import load_dotenv
from deepl import translate_to_ja, translate_to_en
from newsapi import fetch_full_articles
from newsdata_io import fetch_full_articles_newsdata
from gnews import fetch_full_articles_gnews # 新しくインポート
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from concurrent.futures import ThreadPoolExecutor

API_KEY = os.getenv("OPENAI_API_KEY")

# Flaskのインスタンス作成
app = Flask(__name__)

# 環境変数の読み込み
load_dotenv()

# セッション管理のための秘密鍵
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# ファイルアップロード設定
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# アップロードフォルダを作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

POSTS_FILE = 'posts.json'
USERS_FILE = 'users.json'
AVATARS_FOLDER = 'static/avatars'

# アバターフォルダを作成
os.makedirs(AVATARS_FOLDER, exist_ok=True)

# 翻訳処理を並列実行するためのスレッドプール
executor = ThreadPoolExecutor(max_workers=5)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_posts():
    """ユーザー投稿を読み込む"""
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_posts(posts):
    """ユーザー投稿を保存"""
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def load_users():
    """ユーザーデータを読み込む"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_users(users):
    """ユーザーデータを保存"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user_by_email(email):
    """メールアドレスでユーザーを検索"""
    users = load_users()
    for user in users:
        if user['email'] == email:
            return user
    return None

def get_user_by_id(user_id):
    """IDでユーザーを検索"""
    users = load_users()
    for user in users:
        if user['id'] == user_id:
            return user
    return None

def _translate_article(article_lang_tuple):
    """個々の記事を翻訳するヘルパー関数"""
    article, lang = article_lang_tuple
    try:
        if lang == "ja":
            # 英語→日本語に翻訳
            title_ja = translate_to_ja(article["title"])
            description_ja = translate_to_ja(article["description"])
            return {
                "title_en": article["title"],
                "title_ja": title_ja,
                "description_en": article["description"],
                "description_ja": description_ja,
                "url": article["url"],
                "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"],
                "source": article["source"],
                "lang": "ja"
            }
        else:
            # 日本語→英語に翻訳
            title_en = translate_to_en(article["title"])
            description_en = translate_to_en(article["description"])
            return {
                "title_en": title_en,
                "title_ja": article["title"],
                "description_en": description_en,
                "description_ja": article["description"],
                "url": article["url"],
                "urlToImage": article["urlToImage"],
                "publishedAt": article["publishedAt"],
                "source": article["source"],
                "lang": "en"
            }
    except Exception as e:
        print(f"[_translate_article] Error processing article: {e}")
        # エラー時も元の形式で返す
        return {
            "title_en": article.get("title", ""),
            "title_ja": article.get("title", ""),
            "description_en": article.get("description", ""),
            "description_ja": article.get("description", ""),
            "url": article.get("url", ""),
            "urlToImage": article.get("urlToImage", ""),
            "publishedAt": article.get("publishedAt", ""),
            "source": article.get("source", ""),
            "lang": lang
        }

# 記事を取得して翻訳する関数 (並列実行に修正)
def get_translated_articles(query="Apple", page_size=10, lang="ja"):
    """
    ニュース記事を取得し、言語に応じて翻訳する（複数API並列対応、厳密なタイトル検索）
    """
    print(f"[get_translated_articles] Received query: '{query}'")

    # 1. 複数キーワードをAND条件に変換
    keywords = query.split()
    api_query = " AND ".join(f'"{k}"' for k in keywords)
    print(f"[get_translated_articles] Formatted API query: '{api_query}'")

    # 2. 各APIへのリクエストを並列で実行
    newsapi_articles = []
    newsdata_articles = []
    gnews_articles = []

    # executorを使って各APIのフェッチ処理をサブミット
    with ThreadPoolExecutor(max_workers=3) as api_executor:
        futures = []
        # NewsAPIは英語記事に強いため、lang="ja"の時に使用
        if lang == "ja":
            print("[get_translated_articles] Submitting fetch from NewsAPI...")
            futures.append(api_executor.submit(fetch_full_articles, query=api_query, page_size=page_size))

        # NewsData.ioは多言語対応
        newsdata_lang = "ja" if lang == "en" else "en"
        print(f"[get_translated_articles] Submitting fetch from NewsData.io with lang='{newsdata_lang}'...")
        futures.append(api_executor.submit(fetch_full_articles_newsdata, query=api_query, page_size=page_size, language=newsdata_lang))

        # GNewsも多言語対応
        gnews_lang = "ja" if lang == "en" else "en"
        print(f"[get_translated_articles] Submitting fetch from GNews with lang='{gnews_lang}'...")
        futures.append(api_executor.submit(fetch_full_articles_gnews, query=api_query, page_size=page_size, language=gnews_lang))

        # 全てのAPIからの結果を待つ
        all_results = [future.result() for future in futures]

    # 結果を結合
    combined_articles = []
    for result_list in all_results:
        combined_articles.extend(result_list)
    
    print(f"[get_translated_articles] Total articles fetched: {len(combined_articles)}")

    # 3. 記事を結合し、URLで重複を排除
    all_articles = []
    seen_urls = set()
    
    for article in combined_articles:
        url = article.get("url")
        if url and url not in seen_urls:
            all_articles.append(article)
            seen_urls.add(url)
    
    print(f"[get_translated_articles] Combined and deduplicated: {len(all_articles)} articles.")

    # 4. 厳密なタイトル検索
    filtered_articles = []
    lower_keywords = [k.lower() for k in keywords]
    for article in all_articles:
        title_lower = (article.get("title") or "").lower()
        if all(k in title_lower for k in lower_keywords):
            filtered_articles.append(article)
            
    print(f"[get_translated_articles] Filtered by title: {len(filtered_articles)} articles remain.")

    if not filtered_articles:
        return []

    # 5. 翻訳処理を並列実行 (既存のexecutorを使用)
    print(f"[get_translated_articles] Translating {len(filtered_articles)} articles in parallel...")
    tasks = [(article, lang) for article in filtered_articles]
    result_articles = list(executor.map(_translate_article, tasks))
    
    print(f"[get_translated_articles] Returning {len(result_articles)} translated articles.")
    return result_articles


@app.route('/')
def index():
    """
    メインページ: 初期表示時は空のリストを表示（APIは呼ばない）
    """
    return render_template(
        'testapp/index.html',
        articles=[]
    )


@app.route('/api/update')
def api_update():
    """
    API更新エンドポイント: ニュース記事を取得してJSONで返す
    クエリパラメータ: lang=en または lang=ja (デフォルト: ja)
    """
    lang = request.args.get('lang', 'ja')
    # デフォルトのクエリを"Apple"に設定
    articles = get_translated_articles(query="Apple", page_size=10, lang=lang)
    return jsonify(articles)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    ユーザー投稿を取得
    """
    posts = load_posts()
    return jsonify(posts)


@app.route('/api/posts', methods=['POST'])
def create_post():
    """
    新しい投稿を作成
    """
    try:
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # 画像のアップロード処理
        image_url = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # タイムスタンプを追加してユニークにする
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f'/static/uploads/{filename}'
        
        # 新しい投稿を作成
        new_post = {
            'id': datetime.now().isoformat(),
            'title': title,
            'description': description,
            'image': image_url,
            'timestamp': datetime.now().isoformat(),
            'type': 'user_post'
        }
        
        # 投稿を保存
        posts = load_posts()
        posts.insert(0, new_post)  # 新しい投稿を先頭に
        save_posts(posts)
        
        print(f"[create_post] Created new post: {title}")
        return jsonify(new_post), 201
        
    except Exception as e:
        print(f"[create_post] Error: {type(e).__name__}: {e}")
        return jsonify({'error': str(e)}), 500


# ===== AUTHENTICATION ENDPOINTS =====

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    新規ユーザー登録
    """
    try:
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # メールアドレスの重複チェック
        if get_user_by_email(email):
            return jsonify({'error': 'Email already exists'}), 400
        
        # 新規ユーザー作成
        users = load_users()
        new_user = {
            'id': datetime.now().isoformat(),
            'email': email,
            'password_hash': generate_password_hash(password),
            'icon': '',  # デフォルトはアイコンなし
            'created_at': datetime.now().isoformat()
        }
        users.append(new_user)
        save_users(users)
        
        # セッションにログイン情報を保存
        session['user_id'] = new_user['id']
        session['user_email'] = new_user['email']
        
        print(f"[register] New user registered: {email}")
        return jsonify({
            'id': new_user['id'],
            'email': new_user['email'],
            'icon': new_user['icon']
        }), 201
        
    except Exception as e:
        print(f"[register] Error: {type(e).__name__}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    ユーザーログイン
    """
    try:
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # ユーザーを検索
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # パスワード検証
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # セッションにログイン情報を保存
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        
        print(f"[login] User logged in: {email}")
        return jsonify({
            'id': user['id'],
            'email': user['email'],
            'icon': user.get('icon', '')
        }), 200
        
    except Exception as e:
        print(f"[login] Error: {type(e).__name__}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    ユーザーログアウト
    """
    session.clear()
    print("[logout] User logged out")
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/current', methods=['GET'])
def get_current_user():
    """
    現在のログインユーザー情報を取得
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'logged_in': False}), 200
    
    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'logged_in': False}), 200
    
    return jsonify({
        'logged_in': True,
        'id': user['id'],
        'email': user['email'],
        'icon': user.get('icon', '')
    }), 200


@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """
    ユーザープロフィール更新
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        users = load_users()
        user_index = None
        for i, user in enumerate(users):
            if user['id'] == user_id:
                user_index = i
                break
        
        if user_index is None:
            return jsonify({'error': 'User not found'}), 404
        
        # メールアドレス更新
        new_email = request.form.get('email', '').strip()
        if new_email and new_email != users[user_index]['email']:
            # 重複チェック
            if get_user_by_email(new_email):
                return jsonify({'error': 'Email already exists'}), 400
            users[user_index]['email'] = new_email
            session['user_email'] = new_email
        
        # パスワード更新
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        if new_password:
            if not current_password:
                return jsonify({'error': 'Current password required'}), 400
            if not check_password_hash(users[user_index]['password_hash'], current_password):
                return jsonify({'error': 'Invalid current password'}), 401
            users[user_index]['password_hash'] = generate_password_hash(new_password)
        
        # アイコン更新
        if 'icon' in request.files:
            file = request.files['icon']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"avatar_{timestamp}_{filename}"
                filepath = os.path.join(AVATARS_FOLDER, filename)
                file.save(filepath)
                users[user_index]['icon'] = f'/static/avatars/{filename}'
        
        save_users(users)
        
        print(f"[update_profile] Profile updated for user: {users[user_index]['email']}")
        return jsonify({
            'id': users[user_index]['id'],
            'email': users[user_index]['email'],
            'icon': users[user_index].get('icon', '')
        }), 200
        
    except Exception as e:
        print(f"[update_profile] Error: {type(e).__name__}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search():
    """
    記事と投稿を検索
    """
    try:
        query = request.args.get('q', '').strip()
        lang = request.args.get('lang', 'ja')
        
        if not query:
            return jsonify({'posts': [], 'articles': []}), 200
        
        # ユーザー投稿を検索 (複数キーワードのAND検索に対応)
        posts = load_posts()
        keywords = query.lower().split()
        filtered_posts = []
        for post in posts:
            # タイトルと説明を結合して検索対象とする
            searchable_content = (post.get('title', '') + ' ' + post.get('description', '')).lower()
            if all(k in searchable_content for k in keywords):
                filtered_posts.append(post)
        
        # NewsAPI/NewsData.io/GNewsで記事を検索
        print(f"[search] Searching external APIs for: {query}, lang={lang}")
        articles = get_translated_articles(query=query, page_size=10, lang=lang)
        
        return jsonify({
            'posts': filtered_posts,
            'articles': articles
        }), 200
        
    except Exception as e:
        print(f"[search] Error: {type(e).__name__}: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
