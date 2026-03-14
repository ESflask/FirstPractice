# iOS アプリ (News-Mobile) 実装計画書 (改訂版)

## 1. プロジェクト概要
FlaskベースのWebアプリケーションと相互連携するネイティブiOSアプリケーション（SwiftUI）の実装計画です。Firebase Storage (Blazeプラン) を使用せず、**Firestoreのみをデータストアとして利用**し、ニュース取得はiOSから直接 **News API** を叩く構成に変更します。

## 2. アーキテクチャ構成

### バックエンド・通信方針
- **Firebase Auth**: ユーザー認証（Web/iOS共通）。
- **Cloud Firestore**: 全データ（投稿、プロフィール）の管理。
- **News API**: iOSアプリから直接リクエストを行い、最新ニュースを取得。
- **Image Handling**: Firebase Storage を使用できないため、iOSからの新規投稿画像は **Base64形式でFirestoreに直接保存** するか、Flaskサーバーへのアップロードエンドポイントを利用します。

### 技術スタック
- **Language**: Swift 5.10+
- **Framework**: SwiftUI
- **Architecture**: MVVM
- **Dependency**: Firebase (Auth, Firestore), NewsAPI-Swift (または URLSession)

## 3. UI/UX デザイン（Liquid Glass 再現）

- **Visual**: `.ultraThinMaterial` を活用し、Web版の透明感あるデザインを再現。
- **Components**:
    - `GlassCard`: 投稿やニュースを表示する半透明カード。
    - `LiquidSidebar`: SwiftUIの `Tabview` またはカスタムサイドバー。

## 4. 機能実装フェーズ

### フェーズ 1: ニュース取得の実装
- [x] News API の iOS 用キー設定（Flask経由で取得）。
- [x] `NewsService` の作成（URLSession による Flask `/api/update` への取得）。
- [x] ニュース一覧表示（Unified Feed レイアウト）。

### フェーズ 2: 認証とプロフィール
- [x] Firebase Auth によるログイン・新規登録。
- [x] プロフィール表示・セキュリティ設定（`SettingsView`）。
- [x] メール認証・パスワード再設定・再認証・アカウント削除・メールアドレス変更の実装。
- [ ] アバター画像の更新（iOS からの Base64 アップロードは未実装）。

### フェーズ 3: Firestore 連携（投稿表示・作成）
- [x] Firestore `posts` コレクションのリアルタイム取得（`PostViewModel`）。
- [x] 投稿作成：画像を **Base64 文字列** に変換し、Firestore の `image_base64` フィールドに保存（800px リサイズ + JPEG 圧縮）。
- [ ] Web側での Base64 デコード表示（未確認）。

### フェーズ 4: 相互連携の最適化
- [x] iOSで投稿した内容がWebのFirestore経由で即時反映されることを確認。
- [x] Webで投稿された画像（ローカルパス）をiOSで表示するための Flask URL 変換処理（ただしIPハードコードの課題あり → Known Issues 参照）。

## 5. データモデルの変更点

### Firestore: `posts`
```swift
struct Post: Codable, Identifiable {
    @DocumentID var id: String?
    var title: String
    var description: String
    var image: String?      // Web版のローカルパス用 (/static/...)
    var image_base64: String? // iOS/Storage無し環境での画像データ
    var user_email: String
    var timestamp: Timestamp
}
```

## 6. 特記事項（Storage 無しの制約対応）
- **画像表示**: 
    - Webで投稿された画像は `https://[Flask-URL]/static/uploads/...` として参照。
    - iOSで投稿した画像は Firestore の Base64 文字列を UIImage に変換して表示。
- **データ制限**: Firestore のドキュメントサイズ上限（1MB）に注意し、iOSからの画像アップロード時はリサイズと圧縮を必須とします。

## 7. マイルストーン
1. **Week 1** ✅: News API 直接取得と基本的なデザイン実装。
2. **Week 2** ✅: Firebase Auth と Firestore 連携（閲覧のみ）。
3. **Week 3** ✅: iOSからの投稿機能（Base64画像保存）の実装。
4. **Week 4** ✅: Web/iOS 間の画像表示互換性の調整。Auth セキュリティフロー・テーマ/言語切替の完成。

## 8. 既知の技術的課題 (Known Issues)

- **IPハードコード**: `NewsService.swift`・`ContentView.swift`（2箇所）に `http://172.20.10.2:5001` が直書き。`AppConfig.swift` への一元管理が必要。
- **MainActor上でのBase64デコード**: `PostViewModel.fetchPosts()` がメインスレッドで全件デコードを実行しており、投稿数増加時にUIがブロックされる恐れがある。`Task.detached` への移行推奨。
- **`FeedItem.id` の不安定性**: `post.id` が nil の場合に `UUID().uuidString` を毎回生成するため、SwiftUIの差分更新が正しく動作しない可能性。
- **`HomeView` ツールバーのログアウトボタン**: アクションが空のプレースホルダーのまま（`authViewModel.signOut()` の呼び出しが必要）。
