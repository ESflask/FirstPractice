# 機能実装ガイド

## 実装ステータス

| Phase | 内容 | 状態 |
|---|---|---|
| Phase 1 | Flaskモジュール分割・リファクタリング | 完了 |
| Phase 2 | Firebase (Auth, Firestore) 基盤導入 | 完了 |
| Phase 3 | iOS SwiftUI 開発・Firebase連携 | 完了 (継続開発中) |
| Phase 4 | Web Firebase化 (Auth移行・DB移行) | 完了 |
| Phase 5 | ソーシャル機能: いいね・コメント | 完了 |
| Phase 6 | ユーザープロフィール | 未実装 |
| Phase 7 | フォロー / フォロワー | 未実装 |
| Phase 8 | パーソナライズドフィード | 未実装 |
| Phase 9 | アプリ内通知センター | 未実装 |

---

## アーキテクチャ概要

### 認証
- **ユーザー** -> Firebase Auth (Client SDK) -> IDトークン
- **トークン** -> Flaskバックエンド (Admin SDKで検証) -> セッション確立

### データベース (Firestore)
- **Web**: Firebase JS SDK <-> Firestore `posts` コレクション
- **iOS**: Firebase iOS SDK <-> Firestore `posts` コレクション
- **同期**: 両プラットフォームでリアルタイム更新

### ニュース取得 (サーバーサイド)
1. クライアント (Web/iOS) が `/api/update` にリクエスト送信
2. `aggregator.py` が複数ニュースAPI (NewsAPI, GNews, NewsData.io) から並列で記事を取得
3. 重複排除ロジックを実行
4. `deepl.py` でタイトル・説明を翻訳 (JA <-> EN)
5. JSONでレスポンス返却。ニュース記事はDBに保存しない -- オンデマンド取得。

### DeepL フォールバック
DeepL APIが利用不可の場合、翻訳をスキップし対象言語の記事のみを取得するフォールバック機構を実装済み。

---

## Firestore データモデル

### posts コレクション (既存)

```
posts/{postId}
  +-- title: string
  +-- description: string
  +-- image: string           # Webローカルパス (/static/uploads/...)
  +-- image_base64: string    # iOS Base64エンコード画像
  +-- user_email: string
  +-- user_id: string
  +-- timestamp: Timestamp
  +-- type: string            # 'user_post' | 'cached_article'
  +-- url: string?            # cached_articleの場合、元記事URL
  +-- keywords: string[]
  +-- like_count: number      # 非正規化カウンター
  +-- comment_count: number   # 非正規化カウンター
```

### posts/{postId}/likes サブコレクション

```
posts/{postId}/likes/{userId}   # ドキュメントID = user_id (1人1いいね保証)
  +-- user_id: string
  +-- user_email: string
  +-- liked_at: Timestamp
```

### posts/{postId}/comments サブコレクション

```
posts/{postId}/comments/{commentId}
  +-- text: string
  +-- user_id: string
  +-- user_email: string
  +-- user_display_name: string   # 現在は email.split('@')[0]、将来はusersコレクションと統一
  +-- timestamp: Timestamp
```

### users コレクション (Phase 6)

```
users/{userId}
  +-- email: string
  +-- display_name: string
  +-- bio: string
  +-- avatar_base64: string?     # iOS投稿用
  +-- avatar_url: string?        # Web投稿用 (/static/uploads/...)
  +-- follower_count: number
  +-- following_count: number
  +-- post_count: number
```

### follows コレクション (Phase 7)

```
follows/{followId}               # followId = "{followerId}_{followingId}"
  +-- follower_id: string
  +-- follower_email: string
  +-- following_id: string
  +-- following_email: string
  +-- created_at: Timestamp
```

### notifications コレクション (Phase 9)

```
notifications/{notificationId}
  +-- to_user_id: string
  +-- from_user_id: string
  +-- from_user_email: string
  +-- type: string                # "like" | "comment" | "follow"
  +-- post_id: string?
  +-- post_title: string?
  +-- comment_text: string?
  +-- read: boolean
  +-- created_at: Timestamp
```

### ニュース記事とユーザー投稿の区別

`timestamp` フィールドの有無で判定: ユーザー投稿は `timestamp` を持ち、ニュース記事は持たない。

### 投稿の type フィールド

- `type: 'user_post'` -- ユーザー投稿 (Firestore起点)
- `type: 'cached_article'` -- ニュース記事がいいね/コメントされた際にキャッシュされたもの

---

## Firestore セキュリティルール

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isAuthenticated() {
      return request.auth != null;
    }

    function isOwner(userId) {
      return request.auth.uid == userId;
    }

    match /posts/{postId} {
      allow read: if true;
      allow create: if isAuthenticated();
      allow update: if isAuthenticated() &&
        (isOwner(resource.data.user_id) ||
         request.resource.data.diff(resource.data).affectedKeys()
           .hasOnly(['like_count', 'comment_count']));
      allow delete: if isOwner(resource.data.user_id);

      match /likes/{userId} {
        allow read: if true;
        allow write: if isAuthenticated() && isOwner(userId);
      }

      match /comments/{commentId} {
        allow read: if true;
        allow create: if isAuthenticated();
        allow delete: if isAuthenticated() && isOwner(resource.data.user_id);
      }
    }

    match /users/{userId} {
      allow read: if true;
      allow create, update: if isAuthenticated() && isOwner(userId);
    }

    match /follows/{followId} {
      allow read: if true;
      allow create: if isAuthenticated() &&
        isOwner(request.resource.data.follower_id);
      allow delete: if isAuthenticated() &&
        isOwner(resource.data.follower_id);
    }

    match /notifications/{notificationId} {
      allow read: if isAuthenticated() &&
        isOwner(resource.data.to_user_id);
      allow update: if isAuthenticated() &&
        isOwner(resource.data.to_user_id) &&
        request.resource.data.diff(resource.data).affectedKeys().hasOnly(['read']);
    }
  }
}
```

---

## Firebase 移行 (完了)

### セットアップ手順 (参考)

1. Firebaseコンソールでプロジェクトを作成
2. Firestoreデータベースを有効化 (テストモードで開始)
3. Admin SDKの秘密鍵を生成し、プロジェクトルートに `serviceAccountKey.json` として保存
4. `.gitignore` に `serviceAccountKey.json` を追加
5. 依存関係をインストール: `pip install firebase-admin python-dotenv`
6. `.env` にFirebaseクライアント設定と `GOOGLE_APPLICATION_CREDENTIALS` を設定
7. `app/__init__.py` でAdmin SDKを初期化
8. Flaskから `render_template` 経由でFirebaseクライアント設定をテンプレートに渡す

---

## Phase 5: いいね・コメント (完了)

### バックエンド (Flask) - `app/routes/posts.py`

| メソッド | パス | 説明 |
|---|---|---|
| `POST` | `/api/posts/cache-article` | ニュース記事をFirestoreにキャッシュ |
| `GET/POST/DELETE` | `/api/posts/<id>/like` | いいね状態の取得・追加・削除 |
| `GET/POST` | `/api/posts/<id>/comments` | コメント一覧取得・投稿 |
| `DELETE` | `/api/posts/<id>/comments/<cid>` | コメント削除 |

- トランザクション関数 `_add_like_tx` / `_remove_like_tx` / `_add_comment_tx` / `_delete_comment_tx` をモジュールレベルで定義
- 記事キャッシュ: 同じ `url` のドキュメントが既存なら既存IDを返す。`get_posts()` が `type` フィールドを上書きしないよう修正済み。

### Webフロントエンド
- 詳細モーダルを `flex-direction:column` に変更: スクロール領域 (`flex:1`) + 固定アクションバー (`flex-shrink:0`) の2段構成
- いいね: 楽観的UI更新 -> API呼び出し -> 失敗時ロールバック。ニュース記事は先に `cache-article` を呼び出す。
- コメント: ボタンでセクションをトグル。自分のコメントのみ削除ボタンを表示。

### 技術的注意点

**Firestore トランザクション (Python)**
```python
@firestore.transactional
def _add_like_tx(transaction, post_ref, like_ref, like_data):
    post = post_ref.get(transaction=transaction)
    current_count = post.get('like_count') or 0
    transaction.set(like_ref, like_data)
    transaction.update(post_ref, {'like_count': current_count + 1})
```

**楽観的UI更新 (JavaScript)**
```javascript
async function toggleLike(postId, btn) {
    const wasLiked = btn.classList.contains('liked');
    btn.classList.toggle('liked');
    updateLikeCount(postId, wasLiked ? -1 : 1);
    try {
        await fetch(`/api/posts/${postId}/like`, { method: wasLiked ? 'DELETE' : 'POST' });
    } catch {
        btn.classList.toggle('liked');
        updateLikeCount(postId, wasLiked ? 1 : -1);
    }
}
```

**iOS リアルタイムリスナーのメモリリーク防止**
```swift
class CommentViewModel: ObservableObject {
    private var listener: ListenerRegistration?
    func stopListening() { listener?.remove() }
    deinit { stopListening() }
}
```

**既存ドキュメントのカウンターフィールド nil チェック**
```python
like_count = post_data.get('like_count') or 0
comment_count = post_data.get('comment_count') or 0
```

---

## Phase 6: ユーザープロフィール (未実装)

### バックエンド (Flask)

`app/routes/users.py` を作成し、`app/__init__.py` で Blueprint を登録。

```
GET   /api/users/<user_id>          # プロフィール取得
PUT   /api/users/<user_id>          # プロフィール更新 (display_name, bio, avatar)
GET   /api/users/<user_id>/posts    # ユーザーの投稿一覧
```

初期化ロジック: ユーザーが初めてログインした時点 (または投稿作成時) に `users/{uid}` ドキュメントを作成。既存ユーザーは初回アクセス時にドキュメントがなければ作成。

### Web
- 投稿カードの `user_email` クリックでプロフィールモーダルを表示
- `renderUserPost` 内の `user-post-badge` を `users/{userId}.display_name` に差し替え
- `renderComments()` の `comment-author` も `display_name` で統一

### iOS
- `ProfileView.swift` を新規作成 (`LazyVGrid` で投稿サムネイル一覧)
- 自分のプロフィール: 編集ボタン -> `display_name` / `bio` を編集するSheet
- `PostViewModel` で `user_display_name` を `users` コレクションから取得するよう更新

---

## Phase 7: フォロー / フォロワー (未実装)

### バックエンド

`app/routes/users.py` に追加:

```
POST   /api/users/<user_id>/follow
DELETE /api/users/<user_id>/follow
GET    /api/users/<user_id>/followers
GET    /api/users/<user_id>/following
GET    /api/users/<user_id>/is_following
```

トランザクションで `users/{followingId}.follower_count` と `users/{followerId}.following_count` を同時更新。

### Web / iOS
- プロフィールページにフォローボタンを追加 (自分のプロフィールでは非表示)

---

## Phase 8: パーソナライズドフィード (未実装)

**Option A (シンプル):** フォロー中ユーザーの `user_id` リストで Firestore の `whereIn` フィルタ (上限30件)

**Option B (スケーラブル):** フォロー時に `feed/{userId}/items` にコピーを作成するファンアウト方式

**推奨**: Option A で開始し、フォロー数が30を超える場合に Option B へ移行。

---

## Phase 9: アプリ内通知センター (未実装)

| イベント | 通知内容 |
|---|---|
| いいね | 「○○さんがあなたの投稿にいいねしました」 |
| コメント | 「○○さんがコメントしました: ...」 |
| フォロー | 「○○さんがあなたをフォローしました」 |

- Flask: いいね/コメント/フォローのエンドポイント内で `notifications` コレクションに追加 (自分自身への通知はスキップ)
- Web: ヘッダーにベルアイコン + 未読バッジ、Firestore `onSnapshot` でリアルタイム更新
- iOS: `NotificationsView.swift` を新規作成、`addSnapshotListener` で監視

---

## UI/UX デザイン

### Web: ハイブリッドグラス
- **Liquid Glass (デフォルト)**: `backdrop-filter: blur()` を使ったリッチなブラー効果とアニメーション。
- **Clean Glass (軽量モード)**: アニメーションなし、描画負荷を最小限に。設定から即時切り替え可能。

### iOS: Native Liquid Glass
- **Material**: iOS標準の `UltraThinMaterial` を全面採用。
- **統合フィード**: ニュース記事とユーザー投稿を単一リストで表示。
- **ネイティブ操作**: スワイプバック、長押しメニューなど、OS標準の操作感を提供。

### Liquid Glass CSS 実装

Liquid Glassの5つの重要な要素:

1. **半透明の背景**: `background: rgba(255, 255, 255, 0.1);`
2. **ぼかし効果**: `backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);`
3. **微細な境界線**: `border: 1px solid rgba(255, 255, 255, 0.18);`
4. **柔らかい影**: `box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);`
5. **美しい背景**: `body` にグラデーションや画像を適用し、ガラス効果を引き立てる。

完成形の例:
```css
.article-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.05) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 20px;
}
```

ダークモード版:
```css
.article-card {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
```

パフォーマンス注意: `backdrop-filter` は計算コストが高い。軽量モードではブラー半径を縮小するか無効化すること。

### 画像表示フロー

1. **取得**: NewsAPIが各記事に `urlToImage` URLを返す
2. **受け渡し**: Pythonが翻訳済み記事辞書にURLを含める
3. **描画**: HTML `<img src="{{ article.urlToImage }}">` + `onerror` でプレースホルダーにフォールバック
4. **スタイル**: `object-fit: cover` で異なるサイズの画像を統一的に表示

---

## iOS 実装ステータス

### 完了済み
- Firebase Auth (ログイン・新規登録・メール認証・パスワード再設定・再認証・アカウント削除・メールアドレス変更)
- Firestore `posts` リアルタイム取得 (`PostViewModel`)
- 投稿作成: 画像をBase64変換して `image_base64` に保存 (800pxリサイズ + JPEG圧縮)
- Web投稿画像の表示: Flask URLから `AsyncImage` で読み込み
- Native Liquid Glass デザイン (`ultraThinMaterial`)
- テーマ切替 (ライト/ダーク/システム) ・言語切替 (JA/EN)
- キーボード自動dismiss
- 画像アスペクト比維持表示 (`ImageProcessingActor.swift`)
- `CommentView.swift` 作成済み

### 未実装
- アバター画像の更新 (iOSからBase64アップロード)
- プロフィール画面 (`ProfileView.swift`)
- ログアウトボタンのバグ修正 (既知の課題 #5)

---

## 既知リスクと対策

| リスク | 対策 |
|---|---|
| Firestore `whereIn` の30件上限 (フォロー) | Option Aから開始し、必要に応じてOption Bへ移行 |
| Base64画像による Firestore 1MB上限超過 | iOSでの800pxリサイズ + JPEG圧縮を必須化 |
| `like_count` の競合更新 | Firestoreトランザクション必須 |
| 人気投稿での通知大量生成 | 「最後のX件のみ保持」またはCloud Functionsでバッチ処理 |
| iOS リアルタイムリスナーのメモリリーク | `deinit` で必ず `listener?.remove()` を呼び出す |

---

## 将来の改善候補

- FCMによるプッシュ通知
- 全文検索エンジン (Algolia) の導入によるFirestore検索強化
- Firestoreページネーション対応
- 画像のCDN配信・キャッシュ戦略の最適化
- Redisキャッシュ導入によるニュースAPI応答の高速化
