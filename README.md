# Multi-API News Application (Web & iOS)
![3C4E4793-8B76-44FE-863F-7A2CD265FC12_1_105_c](https://github.com/user-attachments/assets/05000198-978a-4ef7-a798-daeb0222122a)

A cross-platform news aggregation and social platform that pulls articles from multiple global sources (NewsAPI, GNews, NewsData.io), translates them seamlessly using DeepL, and lets users share and discuss content.

The **Web version (Flask)** and **iOS version (SwiftUI)** run in parallel, sharing data in real time via Firebase as a unified backend.

The UI adopts a Liquid Glass design inspired by publicly available implementations, with a performance-optimized lightweight mode also included. Most of the coding was directed through AI agents.

---

## Features

### Smart News Aggregation
- **Multi-source:** Fetches articles from **NewsAPI**, **GNews**, and **NewsData.io** for broad coverage.
- **Parallel fetching:** Uses `ThreadPoolExecutor` to query multiple APIs concurrently, reducing response time.
- **Intelligent deduplication:** Automatically removes duplicate articles across different sources.

### Seamless Translation
- **DeepL integration:** High-quality translation between English and Japanese.
- **Bidirectional:** Supports both EN→JA and JA→EN for titles and descriptions.
- **Fallback mechanism:** If DeepL is unavailable, only articles in the target language are served (no broken translations).

### Cross-Platform User System
- **Firebase integration:** Secure login via **Firebase Authentication** and real-time data sync via **Firestore**.
- **Shared data:** Posts created on Web are visible on iOS and vice versa. Accounts are unified across platforms.
- **User posts:** Users can create posts with a title, description, and image.
- **Likes & Comments:** Like and comment on both news articles and user posts, with optimistic UI updates.
- **User profiles:** Display name, bio, and avatar customization. Accessible even without email verification.

### Web UI/UX
- **Liquid Glass design:** Distinctive glassmorphism with transparency and blur effects.
- **Lightweight mode (Clean Glass):** Animation-free, performance-first design mode to prevent slowdowns in Chrome and similar browsers. Switchable from settings.
- **Responsive:** Card-based layout that adapts to various screen sizes.

### iOS (Native)
- **Native Liquid Glass:** Glassmorphism using iOS standard `UltraThinMaterial` for a fully native feel.
- **Unified feed:** News articles and user posts displayed seamlessly in a single timeline.
- **Image optimization:** Automatic resize and aspect-ratio-preserving display for post images.
- **Auth security flows:** Email verification, password reset, re-authentication, account deletion, and email address change.
- **Theme & language switching:** Light / Dark / System theme and JA / EN language toggle.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Flask, Firebase Admin SDK |
| Database | Google Cloud Firestore (NoSQL) |
| Authentication | Firebase Authentication (Email/Password) |
| HTTP | `requests`, `httpx` |
| Web Frontend | HTML5, CSS3, Vanilla JS, Firebase JS SDK |
| iOS | SwiftUI, Firebase iOS SDK |
| News APIs | NewsAPI, GNews, NewsData.io |
| Translation | DeepL API |
| Deploy | `gunicorn` |

---

## Setup & Installation (Web)

### 1. Prerequisites
- Python 3.11+
- API keys for NewsAPI, GNews, NewsData.io, and DeepL
- A Firebase project with Authentication (Email/Password) and Firestore enabled
- Firebase Admin SDK credentials JSON file

### 2. Install dependencies

```bash
git clone <repository-url>
cd flaskdev
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
# Flask
SECRET_KEY=your_secret_key_here

# News APIs
NEWSAPI_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_api_key_here
NEWSDATA_IO_API_KEY=your_newsdata_io_api_key_here

# Translation
DEEPL_AUTH_KEY=your_deepl_auth_key_here

# Firebase (Admin SDK)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-adminsdk.json
```

### 4. Run the application

```bash
python run.py
# or
flask run --host=0.0.0.0 --port=8000
```

Open `http://localhost:8000` in your browser.

---

## Project Structure

```
flaskdev/
├── app/
│   ├── __init__.py        # App factory & Firebase Admin SDK init
│   ├── routes/
│   │   ├── main.py        # News fetch & search endpoints
│   │   ├── auth.py        # Authentication (session management)
│   │   ├── posts.py       # Posts API (Firestore CRUD, likes, comments)
│   │   └── users.py       # User profiles API (display name, bio, avatar)
│   ├── services/
│   │   ├── aggregator.py  # Parallel news fetching & deduplication
│   │   ├── deepl.py       # DeepL translation wrapper
│   │   ├── gnews.py       # GNews API wrapper
│   │   ├── newsapi.py     # NewsAPI wrapper
│   │   └── newsdata.py    # NewsData.io wrapper
│   ├── static/            # CSS (glassUI.css, lightweightUI.css), images
│   └── templates/         # Jinja2 HTML (includes Firebase JS SDK init)
├── News-Mobile/           # iOS SwiftUI project (Firebase-integrated)
│   └── News-Mobile/
│       ├── ContentView.swift     # Main view (unified feed)
│       ├── PostViewModel.swift   # Firestore logic
│       ├── NewsService.swift     # Flask API client
│       └── CommentView.swift     # Comment sheet
├── docs/                  # Project documentation & implementation plans
├── requirements.txt
└── run.py                 # Entry point
```

---

## Architecture Overview

### News Flow (Server-Side)
```
Client (Web/iOS)
  → GET /api/update
  → Flask aggregator.py (parallel fetch from NewsAPI, GNews, NewsData.io)
  → DeepL translation
  → JSON response (not stored in DB — fetched on demand)
```

### User Data Flow (Firestore)
```
Web  ←→ Firebase JS SDK  ←→ Firestore `posts` / `users` collections
iOS  ←→ Firebase iOS SDK ←→ Firestore `posts` / `users` collections
         (real-time sync across platforms)
```

### Authentication
```
Client → Firebase Auth (Client SDK) → ID Token
Token  → Flask Backend (Admin SDK verification) → Session established
```

---

## Design Highlights

- **Dual Web themes:** Heavy "Liquid Glass" and lightweight "Clean Glass" — users choose based on their hardware.
- **iOS native feel:** `UltraThinMaterial` throughout, matching Apple's design language.
- **On-demand news fetching:** No scheduled jobs needed; news is fetched when the user requests it, saving API quota.
- **Base64 image storage:** Since Firebase Storage (Blaze plan) is not used, iOS post images are resized to ≤800px, JPEG-compressed, and stored as Base64 strings directly in Firestore.

---

## Roadmap

- [x] Multi-source news aggregation with parallel fetch
- [x] DeepL translation with fallback
- [x] Firebase Auth + Firestore cross-platform sync
- [x] iOS Native Liquid Glass UI
- [x] Likes & comments (Web)
- [ ] Likes & comments (iOS)
- [x] User profiles (display name, bio, avatar)
- [ ] Push notifications via FCM
- [ ] Full-text search (Algolia or similar)
- [ ] Firestore pagination
- [ ] iOS home screen widget

---

# Multi-API ニュースアプリケーション（Web & iOS）

複数のグローバルニュースソース（NewsAPI、GNews、NewsData.io）から記事を取得し、DeepLでシームレスに翻訳し、ユーザーがコンテンツを共有・議論できるクロスプラットフォームのニュース集約・ソーシャルプラットフォームです。

**Web版（Flask）** と **iOS版（SwiftUI）** は並行して動作し、Firebaseを統合バックエンドとして利用することで、リアルタイムにデータを共有します。

UIは公開されている実装から着想を得たLiquid Glassデザインを採用しており、パフォーマンスを最適化した軽量モードも搭載しています。コーディングの大部分はAIエージェントへの指示を通じて行われました。

---

## 機能

### スマートなニュース集約
- **複数ソース対応:** **NewsAPI**、**GNews**、**NewsData.io** から記事を取得し、幅広いニュースをカバーします。
- **並列取得:** `ThreadPoolExecutor` を使って複数APIへ同時に問い合わせ、レスポンス時間を短縮します。
- **高度な重複排除:** 異なるソース間で重複する記事を自動的に除去します。

### シームレスな翻訳
- **DeepL連携:** 英語と日本語の間で高品質な翻訳を行います。
- **双方向対応:** タイトルと説明文について、EN→JA と JA→EN の両方向をサポートします。
- **フォールバック機構:** DeepLが利用できない場合は、翻訳が壊れた状態で表示せず、対象言語の記事のみを提供します。

### クロスプラットフォームのユーザーシステム
- **Firebase連携:** **Firebase Authentication** による安全なログインと、**Firestore** によるリアルタイムデータ同期に対応します。
- **共有データ:** Webで作成した投稿はiOSでも表示され、その逆も同様です。アカウントはプラットフォーム間で統一されています。
- **ユーザー投稿:** ユーザーはタイトル、説明文、画像付きの投稿を作成できます。
- **いいね・コメント:** ニュース記事とユーザー投稿の両方に、楽観的UI更新付きでいいね・コメントできます。
- **ユーザープロフィール:** 表示名、自己紹介、アバターをカスタマイズできます。メール未認証でもアクセス可能です。

### Web UI/UX
- **Liquid Glassデザイン:** 透明感とブラー効果を使った特徴的なグラスモーフィズムUIです。
- **軽量モード（Clean Glass）:** Chromeなどのブラウザでの動作低下を防ぐため、アニメーションを排除したパフォーマンス優先のデザインモードです。設定から切り替えできます。
- **レスポンシブ対応:** さまざまな画面サイズに適応するカードベースのレイアウトです。

### iOS（ネイティブ）
- **ネイティブLiquid Glass:** iOS標準の `UltraThinMaterial` を使ったグラスモーフィズムにより、完全にネイティブな見た目を実現します。
- **統合フィード:** ニュース記事とユーザー投稿を、単一のタイムライン内にシームレスに表示します。
- **画像最適化:** 投稿画像を自動リサイズし、アスペクト比を保ったまま表示します。
- **認証セキュリティフロー:** メール認証、パスワードリセット、再認証、アカウント削除、メールアドレス変更に対応します。
- **テーマ・言語切り替え:** ライト / ダーク / システムテーマと、日本語 / 英語の言語切り替えに対応します。

---

## 技術スタック

| レイヤー | 技術 |
|---|---|
| バックエンド | Python 3.11+, Flask, Firebase Admin SDK |
| データベース | Google Cloud Firestore (NoSQL) |
| 認証 | Firebase Authentication (Email/Password) |
| HTTP | `requests`, `httpx` |
| Webフロントエンド | HTML5, CSS3, Vanilla JS, Firebase JS SDK |
| iOS | SwiftUI, Firebase iOS SDK |
| ニュースAPI | NewsAPI, GNews, NewsData.io |
| 翻訳 | DeepL API |
| デプロイ | `gunicorn` |

---

## セットアップとインストール（Web）

### 1. 前提条件
- Python 3.11+
- NewsAPI、GNews、NewsData.io、DeepL のAPIキー
- Authentication（Email/Password）とFirestoreを有効化したFirebaseプロジェクト
- Firebase Admin SDKの認証情報JSONファイル

### 2. 依存関係のインストール

```bash
git clone <repository-url>
cd flaskdev
pip install -r requirements.txt
```

### 3. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成します。

```env
# Flask
SECRET_KEY=your_secret_key_here

# ニュースAPI
NEWSAPI_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_api_key_here
NEWSDATA_IO_API_KEY=your_newsdata_io_api_key_here

# 翻訳
DEEPL_AUTH_KEY=your_deepl_auth_key_here

# Firebase（Admin SDK）
FIREBASE_CREDENTIALS_PATH=path/to/firebase-adminsdk.json
```

### 4. アプリケーションの実行

```bash
python run.py
# または
flask run --host=0.0.0.0 --port=8000
```

ブラウザで `http://localhost:8000` を開きます。

---

## プロジェクト構成

```
flaskdev/
├── app/
│   ├── __init__.py        # アプリファクトリ & Firebase Admin SDK初期化
│   ├── routes/
│   │   ├── main.py        # ニュース取得 & 検索エンドポイント
│   │   ├── auth.py        # 認証（セッション管理）
│   │   ├── posts.py       # 投稿API（Firestore CRUD、いいね、コメント）
│   │   └── users.py       # ユーザープロフィールAPI（表示名、自己紹介、アバター）
│   ├── services/
│   │   ├── aggregator.py  # ニュースの並列取得 & 重複排除
│   │   ├── deepl.py       # DeepL翻訳ラッパー
│   │   ├── gnews.py       # GNews APIラッパー
│   │   ├── newsapi.py     # NewsAPIラッパー
│   │   └── newsdata.py    # NewsData.ioラッパー
│   ├── static/            # CSS（glassUI.css、lightweightUI.css）、画像
│   └── templates/         # Jinja2 HTML（Firebase JS SDK初期化を含む）
├── News-Mobile/           # iOS SwiftUIプロジェクト（Firebase連携）
│   └── News-Mobile/
│       ├── ContentView.swift     # メインビュー（統合フィード）
│       ├── PostViewModel.swift   # Firestoreロジック
│       ├── NewsService.swift     # Flask APIクライアント
│       └── CommentView.swift     # コメントシート
├── docs/                  # プロジェクトドキュメント & 実装計画
├── requirements.txt
└── run.py                 # エントリーポイント
```

---

## アーキテクチャ概要

### ニュースフロー（サーバー側）
```
クライアント（Web/iOS）
  → GET /api/update
  → Flask aggregator.py（NewsAPI、GNews、NewsData.io から並列取得）
  → DeepL翻訳
  → JSONレスポンス（DBには保存せず、オンデマンドで取得）
```

### ユーザーデータフロー（Firestore）
```
Web  ←→ Firebase JS SDK  ←→ Firestore `posts` / `users` コレクション
iOS  ←→ Firebase iOS SDK ←→ Firestore `posts` / `users` コレクション
         （プラットフォーム間でリアルタイム同期）
```

### 認証
```
クライアント → Firebase Auth（Client SDK）→ IDトークン
トークン    → Flaskバックエンド（Admin SDKで検証）→ セッション確立
```

---

## デザインの特徴

- **Webの2テーマ:** 高負荷な「Liquid Glass」と軽量な「Clean Glass」を用意し、ユーザーが自分のハードウェアに合わせて選択できます。
- **iOSネイティブの操作感:** 全体に `UltraThinMaterial` を採用し、Appleのデザイン言語に合う見た目にしています。
- **オンデマンドなニュース取得:** 定期実行ジョブは不要です。ユーザーがリクエストしたタイミングでニュースを取得するため、APIクォータを節約できます。
- **Base64画像保存:** Firebase Storage（Blazeプラン）を使用しないため、iOSの投稿画像は800px以下にリサイズし、JPEG圧縮したうえでBase64文字列としてFirestoreに直接保存します。

---

## ロードマップ

- [x] 複数ソースからのニュース集約と並列取得
- [x] フォールバック付きDeepL翻訳
- [x] Firebase Auth + Firestore によるクロスプラットフォーム同期
- [x] iOSネイティブLiquid Glass UI
- [x] いいね・コメント（Web）
- [ ] いいね・コメント（iOS）
- [x] ユーザープロフィール（表示名、自己紹介、アバター）
- [ ] FCMによるプッシュ通知
- [ ] 全文検索（Algoliaなど）
- [ ] Firestoreページネーション
- [ ] iOSホーム画面ウィジェット
