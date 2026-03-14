# Integrated News Platform - 実装計画とアーキテクチャ

## 1. プロジェクト概要
**News-Mobile / Flask-Web Integrated System**

本プロジェクトは、Web (Flask) と iOS (Native SwiftUI) の両プラットフォームで動作するニュースアグリゲーションおよびユーザー投稿プラットフォームです。
Web版・iOS版共にFirebase (Authentication, Firestore) をバックエンドとして利用し、ユーザーデータと投稿をリアルタイムで同期します。

## 2. ディレクトリ構成 (Current Status)

Firebase統合完了後の現在のプロジェクト構造です。

```text
/ (Project Root)
├── app/                          # Flask Webアプリケーション
│   ├── __init__.py               # Firebase Admin SDK初期化
│   ├── models.py                 # (Deprecated) 旧SQLAlchemyモデル
│   ├── routes/                   # エンドポイント定義
│   │   ├── main.py               # ニュース取得・表示
│   │   ├── auth.py               # 認証 (Firebase Token検証)
│   │   └── posts.py              # 投稿API (Firestore連携)
│   ├── services/                 # 外部API連携
│   │   ├── aggregator.py         # 記事取得・翻訳統合ロジック
│   │   ├── deepl.py              # DeepL API
│   │   ├── gnews.py              # GNews API
│   │   ├── newsapi.py            # NewsAPI
│   │   └── newsdata.py           # NewsData.io API
│   ├── static/                   # 静的アセット (glassUI.css, lightweightUI.css)
│   └── templates/                # Jinja2 テンプレート (Firebase JS SDK)
├── News-Mobile/                  # iOS Nativeアプリケーション
│   ├── News-Mobile/
│   │   ├── News_MobileApp.swift  # Entry Point
│   │   ├── ContentView.swift     # Main View (Unified Feed)
│   │   ├── PostViewModel.swift   # Firestore Logic
│   │   └── Assets.xcassets/
│   └── News-Mobile.xcodeproj/
├── docs/                         # ドキュメント類
├── requirements.txt              # Python依存パッケージ
└── run.py                        # アプリケーション起動スクリプト
```

## 3. アーキテクチャ移行計画 (Status Report)

Web版のSQLite依存を脱却し、Firebase中心のアーキテクチャへの移行が完了しました。

### Phase 1: 現状整理とリファクタリング (完了)
- Flaskアプリのモジュール分割。
- 外部API連携ロジックの分離。

### Phase 2: Firebase基盤の導入 (完了)
- Firebase Project作成、Auth (Email/Password) 有効化。
- Firestoreデータベース作成、ルール設定。

### Phase 3: iOSアプリ開発 & 接続 (完了 / 継続開発中)
- Firebase SDK (Auth, Firestore) の導入済み。
- **Native Liquid Glass** デザインの実装（ultraThinMaterial FAB、透過CreatePostView）。
- ニュースとユーザー投稿の統合タイムライン実装済み。
- 画像のアスペクト比維持表示、自動リサイズロジック実装済み。
- Firebase Auth セキュリティフロー（メール認証・パスワード再設定・再認証・アカウント削除・メールアドレス変更）実装済み。
- テーマ切替（ライト/ダーク/システム）・言語切替（JA/EN）・キーボード自動dismiss実装済み。
- DeepL障害時のフォールバック機構（対象言語の記事のみ取得）実装済み。

### Phase 4: WebアプリのFirebase化 (完了)
- **認証**: Firebase JS SDK + Admin SDKによるセッション管理へ移行済み。
- **DB**: Firestoreへの完全移行済み。`users.json`, `posts.json` は廃止。
- **UI**: パフォーマンスを重視した「Clean Glass (軽量モード)」を実装済み。

## 4. データフロー (Current)

### Authentication
- **User** -> Firebase Auth (Client SDK) -> ID Token
- **Token** -> Flask Backend (Verify via Admin SDK) -> Session Established

### Database (Firestore)
- **Web**: Firebase JS SDK <-> Firestore `posts` collection
- **iOS**: Firebase iOS SDK <-> Firestore `posts` collection
- **Sync**: Realtime updates on both platforms

### News Logic (Server-Side Aggregation)
- **Web/iOS Request** -> Flask (`/api/update`)
- **Flask** -> External APIs (NewsAPI, etc.) -> Translation (DeepL) -> **JSON Response**
- *ニュース記事自体はDBに保存せず、オンデマンドで取得・翻訳してクライアントに返却。*

## 5. UIデザイン仕様

### Web: Hybrid Glass
- **Liquid Glass (Default)**: リッチなブラー効果とアニメーション。
- **Clean Glass (Lightweight)**: アニメーションを排除し、描画負荷を最小限に抑えたモード。設定から即時切り替え可能。

### iOS: Native Liquid Glass
- **Material**: iOS標準の `UltraThinMaterial` を全面的に採用。
- **Unified Feed**: ニュース記事とユーザー投稿を単一のリストで表示。
- **Native Interactions**: スワイプバック、長押しメニューなど、OS標準の操作感を提供。

## 6. Next Steps (Maintenance & Features)

- **Technical Debt (優先)**: 既知の技術的課題の解消（`agents.md` の Known Issues 参照）。
- **Push Notifications**: FCM (Firebase Cloud Messaging) を利用した新着通知の実装。
- **Search Optimization**: Algolia等の全文検索エンジンの導入検討（Firestoreの検索機能強化のため）。
- **Performance Tuning**: Firestoreページネーション対応・画像のCDN配信やキャッシュ戦略の最適化。
