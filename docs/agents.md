# Firebase マルチプラットフォーム掲示板 実装計画書

## 1. プロジェクト概要
**目的:** 画像と一言コメントを投稿できる掲示板アプリの開発

**プラットフォーム:** Web (PC/Mobile ブラウザ) および iOS (Native)

**データ共有:** リアルタイムデータベースおよび画像ストレージを共有し、即時反映させる。

## 2. 技術スタック詳細
### 共通バックエンド (Firebase)
- **Authentication:** ユーザー認証（メール/パスワード）
- **Cloud Firestore:** 投稿データ、ユーザー情報の保存 (NoSQL)
- **Cloud Storage:** 投稿された画像ファイルの保存

### Webフロントエンド / サーバー
- **Python (Flask):** ルーティング、HTML配信、環境変数管理
- **HTML/CSS/JavaScript:** UI構築、Firebase Web SDKの実行

### iOSクライアント
- **Swift / SwiftUI:** UI構築、ロジック
- **Firebase iOS SDK:** バックエンドとの通信

## 3. ディレクトリ構成案
現在のプロジェクト構造に基づいた構成です。
```plaintext
/ (Project Root)
├── app/                      # Flask Webアプリケーション
│   ├── __init__.py           # アプリ初期化 (Factory Pattern)
│   ├── models.py             # DBモデル
│   ├── routes/               # ルーティング
│   ├── services/             # API連携ロジック
│   ├── static/               # CSS, JS, 画像など
│   ├── templates/            # HTMLテンプレート
│   └── utils/                # ユーティリティ
├── News-Mobile/              # iOS Nativeアプリケーション (Xcode Project)
│   ├── News-Mobile/
│   │   ├── News_MobileApp.swift # アプリのエントリーポイント
│   │   ├── ContentView.swift    # メインビュー
│   │   └── Assets.xcassets/     # アセット
│   └── News-Mobile.xcodeproj/   # Xcodeプロジェクトファイル
├── data/                     # データファイル (JSON)
├── docs/                     # ドキュメント
├── instance/                 # SQLiteデータベース
├── run.py                    # Flask起動スクリプト
└── requirements.txt          # Python依存関係
```

## 4. データ設計 (Firestore)
WebとiOSで共通して参照するデータベース設計です。

**コレクション: `posts`**

掲示板の投稿を管理します。

| フィールド名 | 型 | 説明 |
| :--- | :--- | :--- |
| `id` | String | ドキュメントID (自動生成) |
| `userId` | String | 投稿者のUID |
| `userName` | String | 投稿者の表示名（オプション） |
| `text` | String | 一言コメント |
| `imageUrl` | String | Storage上の画像のダウンロードURL |
| `createdAt`| Timestamp| 投稿日時 (ソート用) |

**Cloud Storage 構成**

パス: `/images/{userId}/{uuid}.jpg`

ユーザーごとにフォルダを分け、ユニークなファイル名で保存します。

## 5. 実装ステップ
### Step 1: Firebase プロジェクトのセットアップ
1. Firebase Consoleで新規プロジェクトを作成。
2. Authenticationを有効化（メール/パスワード認証をオン）。
3. Firestore Databaseを作成（まずはテストモードで開始）。
4. Storageを作成（まずはテストモードで開始）。
5. アプリを追加:
    - **Webアプリ:** Config情報（apiKeyなど）を取得。
    - **iOSアプリ:** バンドルIDを指定し、`GoogleService-Info.plist`をダウンロード。

### Step 2: WebアプリへのFirebase統合 (Flask + Firebase JS SDK)
既存のFlaskアプリにFirebase Web SDKを導入し、クライアントサイドでのデータ操作を可能にします。

**実装内容:**
- `app/static/js/firebase_config.js`: Firebase Consoleから取得したConfigキーで初期化。
- `app/templates/testapp/index.html`:
    - Firebase JS SDKを読み込み。
    - 記事の読み込みロジックを既存のAPI呼び出しからFirestoreのリアルタイム監視 (`onSnapshot`) へ必要に応じて統合。
    - 画像投稿機能を、サーバーサイド経由からFirebase Storage + Firestoreへの直接保存に移行。

### Step 3: iOSアプリ実装 (SwiftUI)
既に作成済みの `News-Mobile` プロジェクトにFirebaseを統合します。

1. **SDK導入:** Swift Package Manager (SPM) を使用して、`News-Mobile` ターゲットに `firebase-ios-sdk` を追加。
    - **選択ライブラリ:** `FirebaseAuth`, `FirebaseFirestore`, `FirebaseStorage`.
2. **初期化:** ダウンロードした `GoogleService-Info.plist` を `News-Mobile/News-Mobile/` 直下に配置。
3. **Appクラスの修正:** `News_MobileApp.swift` で `FirebaseApp.configure()` を実行。
4. **UI/ロジック実装:**
    - `ContentView.swift` を拡張し、Firestoreからの投稿取得および投稿画面を構築。
    - `AsyncImage` を使用して、Firebase Storage上の画像URLを表示。

## 6. セキュリティルールの設定 (重要)
開発終盤でテストモードから以下のルールへ移行し、本人以外のデータ操作を防ぎます。

**firestore.rules (例)**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /posts/{postId} {
      // 読み取りは誰でもOK、作成はログイン必須
      allow read: if true;
      allow create: if request.auth != null;
      // 削除・更新は投稿者本人のみ
      allow update, delete: if request.auth != null && request.auth.uid == resource.data.userId;
    }
  }
}
```

## 7. 今後の拡張アイデア
- **プッシュ通知:** Cloud Functions for Firebase を使い、新しい書き込みがあったらiOSへ通知。
- **画像圧縮:** Extension または Cloud Functions でアップロードされた画像をリサイズ（モバイルの通信量削減）。
- **ユーザープロフィール:** アイコン画像の登録など。