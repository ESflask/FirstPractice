# AIエージェント リファレンス

このドキュメントはAIエージェントがシステムを迅速に理解し、一貫性を保ちながら作業するためのリファレンスです。

## 技術スタック

- **バックエンド**: Python 3, Flask, Firebase Admin SDK
- **データベース**: Google Cloud Firestore (NoSQL)
- **認証**: Firebase Authentication (Email/Password)
- **フロントエンド (Web)**: HTML5, Vanilla JavaScript, CSS (Liquid Glass / Lightweight), Firebase JS SDK
- **フロントエンド (iOS)**: SwiftUI, Firebase iOS SDK
- **外部API**: NewsAPI / GNews / NewsData.io (ニュース取得), DeepL API (翻訳)

## ディレクトリ構成

```
/
+-- app/
|   +-- __init__.py      # Flaskアプリ初期化 & Firebase Admin SDK設定
|   +-- routes/
|   |   +-- main.py      # ニュース取得・検索・メインページ
|   |   +-- auth.py      # 認証API (セッション管理)
|   |   +-- posts.py     # 投稿API (Firestore操作、いいね/コメント含む)
|   |   +-- users.py     # ユーザープロフィールAPI (Phase 6、実装中)
|   +-- services/        # 外部APIラッパー (aggregator, deepl, gnews, newsapi, newsdata)
|   +-- static/          # CSS (glassUI.css, lightweightUI.css), JS, 画像アップロード
|   +-- templates/       # HTMLテンプレート (Firebase JS SDK初期化含む)
+-- News-Mobile/         # iOS SwiftUIプロジェクト
|   +-- News-Mobile/     # ContentView.swift, PostViewModel.swift, CommentView.swift 等
+-- docs/                # ドキュメント
+-- .env                 # APIキー、Firebase認証情報パス (gitignore済み)
+-- requirements.txt
```

## アーキテクチャ

### ニュース取得フロー
1. クライアント (Web/iOS) -> `/api/update` リクエスト
2. `aggregator.py` が複数ニュースAPIから並列取得・重複排除
3. `deepl.py` でタイトル・説明を翻訳 (JA <-> EN)。障害時は対象言語の記事のみ取得するフォールバック実装済み
4. JSONでレスポンス返却。ニュース記事はDBに保存しない (オンデマンド取得)。

### ユーザーデータ (Firestore)
- **認証**: WebはFirebase JS SDKでIDトークン取得 -> Flask Admin SDKで検証。iOSはFirebase iOS SDKで直接認証。
- **投稿**: `posts` コレクション。Web/iOS共通。iOS画像はBase64で `image_base64` フィールドに保存 (800pxリサイズ + JPEG圧縮)。
- **いいね/コメント**: `posts/{postId}/likes` と `posts/{postId}/comments` サブコレクション。カウンターは `like_count` / `comment_count` で非正規化。

### 投稿の type フィールド
- `type: 'user_post'` -- ユーザー投稿 (Firestore起点)
- `type: 'cached_article'` -- ニュース記事がいいね/コメントされた際にキャッシュされたもの

### ニュース記事とユーザー投稿の区別
`timestamp` フィールドの有無で判定: ユーザー投稿は `timestamp` を持ち、ニュース記事は持たない。

## APIエンドポイント

### ニュース (`app/routes/main.py`)
| メソッド | パス | 説明 |
|---|---|---|
| GET | `/` | メインページ |
| GET | `/api/update` | ニュース記事の取得・翻訳 |
| GET | `/api/search` | ニュース記事の検索 |

### 認証 (`app/routes/auth.py`)
| メソッド | パス | 説明 |
|---|---|---|
| POST | `/api/auth/session` | Firebase IDトークンからセッション作成 |
| POST | `/api/auth/logout` | セッション終了 |

### 投稿 (`app/routes/posts.py`)
| メソッド | パス | 説明 |
|---|---|---|
| GET | `/api/posts` | 全投稿一覧 |
| POST | `/api/posts` | 投稿作成 |
| DELETE | `/api/posts/<id>` | 投稿削除 |
| POST | `/api/posts/cache-article` | ニュース記事をFirestoreにキャッシュ |
| GET/POST/DELETE | `/api/posts/<id>/like` | いいね状態: 取得/追加/削除 |
| GET/POST | `/api/posts/<id>/comments` | コメント: 一覧/作成 |
| DELETE | `/api/posts/<id>/comments/<cid>` | コメント削除 |

### ユーザー (`app/routes/users.py`) - Phase 6
| メソッド | パス | 説明 |
|---|---|---|
| GET | `/api/users/<user_id>` | ユーザープロフィール取得 |
| PUT | `/api/users/<user_id>` | ユーザープロフィール更新 |
| GET | `/api/users/<user_id>/posts` | ユーザーの投稿一覧 |

## 開発ガイドライン

- 新機能はWeb・iOS両方での利用を想定して設計すること。
- Firestoreのカウンター更新 (`like_count`, `comment_count` 等) は必ずトランザクションを使うこと。
- iOS画像投稿時は Firestore 1MB上限に注意し、リサイズ・圧縮を必須とする。
- `.env` と `serviceAccountKey.json` は絶対にコミットしないこと。
- `users/{userId}` ドキュメントは初回ログインまたは初回投稿時に作成。既存ユーザーは初回アクセス時にドキュメントがなければ作成。

## 既知の課題

| # | 課題 | 重大度 | ステータス |
|---|---|---|---|
| 1 | IPアドレスのハードコード | 高 | 解決済 |
| 2 | 翻訳キャッシュの Race Condition | 高 | 解決済 |
| 3 | 検索の投稿部分が未実装 | 中 | 解決済 |
| 4 | MainActorでのBase64デコード | 中 | 解決済 |
| 5 | ログアウトボタンが動かない | 中 | 未解決 |
| 6 | 不要・重複インポート | 低 | 未解決 |
| 7 | 全件Firestoreクエリ | 中 | 解決済 |

## Web UI 変更ログ

### 2026-03-14: ユーザー投稿UI改善
- ミニマル表示: `title + description` 合計60文字未満の投稿に `user-post-minimal` クラスを付与 (`width: 33%; align-self: flex-start`)
- 画像付き投稿もミニマル判定の対象
- ミニマル・通常カードでHTML構造を統一
- `openUserPostDetail(post)` を新規追加し、既存の `articleDetailModal` を流用
- `openArticleDetailByIndex` で `item.timestamp` の有無によりニュース記事かユーザー投稿かを判定

### 2026-03-14: iOS ユーザー投稿カード改善
- `UserPostCard` の画像アスペクト比を修正: `.fill` から `.fit` に変更、固定高さ削除
- `HomeView` 最上部に未認証バナーを追加 (Xタップで非表示、スライドアウトアニメーション)
- `SettingsView` に「認証する」ボタン追加 -> 確認ダイアログでメール認証送信を選択

### 2026-03-15: いいね・コメント (Phase 1, 2)
- 詳細モーダルを `flex-direction:column` に変更: スクロール領域 + 固定アクションバー
- いいね: 楽観的UI -> API -> 失敗時ロールバック。ニュース記事は先に `cache-article` を呼び出し
- コメント: トグルセクション、自分のコメントのみ削除ボタン表示
- バックエンドのトランザクション関数をモジュールレベルで定義 (スレッドセーフ)
