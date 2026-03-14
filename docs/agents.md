# Project Documentation (agents.md)

このドキュメントは、本プロジェクトの技術的な概要、構造、そして開発指針をまとめたものです。開発者やAIエージェントがシステムを迅速に理解し、一貫性を保ちながら新しい機能を実装することを目的としています。

## 1. プロジェクト概要

このアプリケーションは、Web (Flask) と iOS (SwiftUI) の両方で動作するクロスプラットフォームニュースリーダーです。Firebaseをバックエンドとして採用し、デバイス間でシームレスな体験を提供します。

## 2. 技術スタック

- **バックエンド**: Python 3, Flask, Firebase Admin SDK
- **データベース**: Google Cloud Firestore (NoSQL)
- **認証**: Firebase Authentication (Email/Password)
- **フロントエンド (Web)**: HTML5, Vanilla JavaScript, CSS (Liquid Glass / Lightweight), Firebase JS SDK
- **フロントエンド (iOS)**: SwiftUI, Firebase iOS SDK
- **外部API**:
  - [NewsAPI](https://newsapi.org/), [GNews](https://gnews.io/), [NewsData.io](https://newsdata.io/): ニュース記事の取得
  - [DeepL API](https://www.deepl.com/docs-api/): 多言語翻訳

## 3. プロジェクト構造

```
/
├── app/
│   ├── __init__.py      # Flaskアプリ初期化 & Firebase Admin SDK設定
│   ├── routes/          # APIエンドポイント
│   │   ├── main.py      # ニュース取得・検索・メインページ
│   │   ├── auth.py      # 認証API (セッション管理連携)
│   │   └── posts.py     # 投稿API (Firestore操作)
│   ├── services/        # 外部APIラッパー (NewsAPI, DeepL, Aggregator)
│   ├── static/          # CSS (glassUI.css, lightweightUI.css), JS, 画像
│   └── templates/       # HTMLテンプレート (Firebase JS SDK初期化含む)
├── News-Mobile/         # iOS SwiftUI プロジェクト
│   ├── News-Mobile/     # ソースコード (Views, ViewModels)
│   └── News-Mobile.xcodeproj/
├── docs/                # ドキュメント
├── .env                 # APIキー、Firebase認証情報パス
└── requirements.txt     # Python依存ライブラリ
```

## 4. 主要なロジックとデータフロー

### ニュース取得・翻訳フロー (Server-Side)

1.  **クライアント (Web/iOS)**: ニュース更新リクエスト (`/api/update`) を送信。
2.  **バックエンド (Flask)**:
    a. `aggregator.py` が複数のニュースAPI (NewsAPI, GNews等) から並列で記事を取得。
    b. 重複排除ロジックを実行。
    c. `deepl.py` を使用して記事のタイトル・詳細を翻訳 (JA <-> EN)。
    d. 翻訳された記事リストをJSONとして返却。
3.  **クライアント**: 受け取ったJSONを描画。Firestoreには保存せず、オンメモリまたは一時キャッシュとして扱います。

### ユーザーデータ管理 (Firestore & Auth)

1.  **認証**:
    -   **Web**: Firebase JS SDK (`signInWithEmailAndPassword`) で認証し、IDトークンを取得。トークンをバックエンドに送信し、セッション検証を行う。
    -   **iOS**: Firebase iOS SDK で直接認証。
2.  **投稿データ (Posts)**:
    -   データは **Firestore** の `posts` コレクションに保存されます。
    -   **Web**: フロントエンドからAPI経由、または直接Firestore SDKを用いて読み書き。
    -   **iOS**: Firestore SDK (`addDocument`, `getDocuments`) を用いて直接読み書き。
    -   画像データはBase64エンコードしてFirestoreに保存（小規模な場合）またはStorage参照として保存。

## 5. UI/UX デザイン方針

-   **Web版**:
    -   **Default**: 「Liquid Glass」デザイン。高負荷なブラー効果とアニメーションを使用。
    -   **Lightweight**: 「Clean Glass」モード。パフォーマンスを重視し、アニメーションを排除したシンプルなデザイン。ユーザー設定で切り替え可能。
-   **iOS版**:
    -   **Native Liquid Glass**: iOS標準の `UltraThinMaterial` を活用し、OSに馴染むグラスモーフィズムを実現。

## 6. 今後の開発指針

-   **新機能の追加**: 常にWebとiOSの両方での利用を想定して設計すること。
-   **データ整合性**: Firestoreのセキュリティルールを適切に設定し、クライアントからの不正な書き込みを防ぐ。
-   **パフォーマンス**: ニュース取得APIのレスポンス時間を短縮するため、キャッシュ戦略（Redis等）の導入を検討する。

### 日記 (History)

- **Day 1**: iOSプロジェクト作成。Firebaseセットアップ完了。Web/iOS間の認証共通化に成功。
- **Day 2**: iOSアプリのUI改善（Native Liquid Glass）。Web版の軽量UIモード実装。DeepL翻訳修正。
- **Day 3**: Firebase Auth セキュリティフロー（メール認証・パスワード再設定・再認証・アカウント削除・メールアドレス変更）実装。iOS テーマ切替（ライト/ダーク/システム）・言語切替（JA/EN）・Liquid Glass FAB・キーボード自動dismiss完成。DeepL障害時のフォールバック機構実装。

### 既知の技術的課題 (Known Issues)

~~すべて解消済み。~~

### Next Steps

-   上記 Known Issues の解消
-   プッシュ通知の実装（FCM）
-   ユーザー間のコメント・インタラクション機能
-   Firestoreページネーション対応
