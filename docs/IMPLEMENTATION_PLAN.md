# Integrated News Platform - 実装計画とアーキテクチャ

## 1. プロジェクト概要
**News-Mobile / Flask-Web Integrated System**

本プロジェクトは、Web (Flask) と iOS (Native SwiftUI) の両プラットフォームで動作するニュースアグリゲーションおよびユーザー投稿プラットフォームです。
現在、Web版は稼働中（Renderデプロイ対応済み）で、iOS版はプロジェクトの初期段階です。最終的にはFirebaseをバックエンドとして採用し、両プラットフォーム間で認証とデータを共有します。

## 2. ディレクトリ構成 (Current Status)

リファクタリング後の現在のプロジェクト構造です。

```text
/ (Project Root)
├── app/                          # Flask Webアプリケーション (Backend & Frontend)
│   ├── __init__.py               # Application Factory
│   ├── models.py                 # SQLite用 DBモデル (User, Post) - ※将来的にFirestoreへ移行
│   ├── routes/                   # エンドポイント定義
│   │   ├── main.py               # ニュース取得・表示
│   │   ├── auth.py               # 認証 (Session/SQLite)
│   │   ├── posts.py              # 投稿API
│   │   └── admin.py              # 管理画面
│   ├── services/                 # 外部API連携
│   │   ├── aggregator.py         # 記事取得・翻訳統合ロジック
│   │   ├── deepl.py              # DeepL API
│   │   ├── gnews.py              # GNews API
│   │   ├── newsapi.py            # NewsAPI
│   │   └── newsdata.py           # NewsData.io API
│   ├── static/                   # 静的アセット
│   │   ├── avatars/              # ユーザーアイコン (Local Storage)
│   │   ├── uploads/              # 投稿画像 (Local Storage)
│   │   └── glassUI.css
│   ├── templates/                # Jinja2 テンプレート
│   └── utils/
│       └── decorators.py
├── News-Mobile/                  # iOS Nativeアプリケーション
│   ├── News-Mobile/
│   │   ├── News_MobileApp.swift  # Entry Point
│   │   ├── ContentView.swift
│   │   └── Assets.xcassets/
│   └── News-Mobile.xcodeproj/
├── data/                         # 初期データ・マイグレーション用JSON
├── docs/                         # ドキュメント類
├── instance/                     # SQLiteデータベース (project.db)
├── run.py                        # ローカル開発用起動スクリプト
├── app.py                        # Renderデプロイ用互換スクリプト
└── requirements.txt              # Python依存パッケージ
```

## 3. アーキテクチャ移行計画

現在はFlask + SQLiteで完結していますが、iOSアプリとのデータ共有を実現するため、以下の段階を経てFirebase中心のアーキテクチャへ移行します。

### Phase 1: 現状整理とリファクタリング (完了)
- Flaskアプリのモジュール分割 (`app/` 以下への整理)。
- 外部API連携ロジック (`services/`) の分離。
- iOSプロジェクトフォルダの配置。

### Phase 2: Firebase基盤の導入 (Next Step)
iOSとWebで共通のバックエンドを持たせる準備を行います。

1. **Firebase Project作成**: Consoleにてプロジェクト作成。
2. **Authentication**: Email/Password認証を有効化。
3. **Firestore**: データベース作成。`posts` コレクションを設計。
4. **Storage**: 画像保存用のバケット作成。

### Phase 3: iOSアプリ開発 & 接続
iOSアプリを先行してFirebaseに接続し、ネイティブアプリとしての機能を実装します。

- **SDK導入**: `FirebaseAuth`, `FirebaseFirestore`, `FirebaseStorage` をSPMで導入。
- **認証実装**: iOS側でのログイン・新規登録。
- **データ表示**: Firestore上のデータをSwiftUIでリスト表示。
- **ニュース表示**: Flask側で作ったニュース取得ロジック（API）をiOSから叩くか、あるいはiOS側で直接APIを叩くか検討が必要。
    - *推奨方針*: APIキー隠蔽のため、ニュース取得はFlaskサーバー経由 (`/api/update`) で行い、iOSはそれをJSONとして受け取る。

### Phase 4: WebアプリのFirebase化 (Hybrid)
Flaskアプリのデータ層をSQLiteからFirebaseへ移行します。

- **認証移行**: Flaskのセッション管理(`auth.py`)を、Firebase Authentication (JS SDK) または Firebase Admin SDK に置き換え。
- **DB移行**: `app/models.py` (SQLAlchemy) を廃止し、Firestoreへの読み書きに変更。
    - 既存の `users.json`, `posts.json` データをFirestoreへマイグレーション。
- **画像移行**: ローカルの `app/static/uploads` ではなく、Firebase Storageへの直接アップロード、またはServer経由アップロードに変更。

## 4. データフローの変更点

### Before (現在)
- **Web**: User -> Flask (Session) -> SQLite (User/Post)
- **News**: Flask -> External APIs -> Translation -> Frontend (Jinja2)
- **iOS**: (未実装)

### After (目標)
- **Auth**: User -> Firebase Auth (Token発行)
- **Database**:
    - Web -> Firebase JS SDK -> Firestore
    - iOS -> Firebase iOS SDK -> Firestore
- **News Logic**:
    - Web -> Flask (`services/aggregator.py`) -> Display
    - iOS -> Request to Flask API (`/api/update`) -> JSON Response -> SwiftUI Display
    - *これにより、高価なAPIキーや翻訳ロジックはサーバー(Flask)側に隠蔽され、クライアント(iOS)は安全にデータを取得できる。*

## 5. Renderデプロイ設定
ディレクトリ構成変更後も以下の設定で動作します。

- **Root Directory**: `.` (ルート)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
    - ※ルートにある `app.py` が `app/__init__.py` の `create_app` を呼び出すため正常に動作します。
## 新しいUIの実装案
Safariでは比較的快適に動作するが、Chromeではアニメーションが非常に重くなります。改善案として既存のliquid glassを再現したUIとは別で、軽量でシンプルなデザインを適応したいと思います

- デザインの詳細画面 : 上部に透明度低めのすりガラス状バーを置き（画面上に浮かせないで）、