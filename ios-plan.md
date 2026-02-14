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
- [ ] News API の iOS 用キー設定。
- [ ] `NewsService` の作成（URLSession による直接取得）。
- [ ] ニュース一覧表示（Web版に近いレイアウト）。

### フェーズ 2: 認証とプロフィール
- [ ] Firebase Auth によるログイン・新規登録。
- [ ] プロフィール表示（Firestore から取得）。
- [ ] ※アバター画像はWeb版がローカル保存のため、iOSからはURL表示のみ、またはBase64での更新を検討。

### フェーズ 3: Firestore 連携（投稿表示・作成）
- [ ] Firestore `posts` コレクションの購読。
- [ ] 投稿作成：画像を **Base64 文字列** に変換し、Firestore の `image_data` フィールド等に保存。
- [ ] Web側での表示対応（Base64デコード表示）。

### フェーズ 4: 相互連携の最適化
- [ ] iOSで投稿した内容がWebのFirestore経由で即時反映されることを確認。
- [ ] Webで投稿された画像（ローカルパス）をiOSで表示するための Flask URL 変換処理。

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
1. **Week 1**: News API 直接取得と基本的なデザイン実装。
2. **Week 2**: Firebase Auth と Firestore 連携（閲覧のみ）。
3. **Week 3**: iOSからの投稿機能（Base64画像保存）の実装。
4. **Week 4**: Web/iOS 間の画像表示互換性の調整。
