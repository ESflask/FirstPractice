# APIを多用した多機能ニュースアプリケーション (Web & iOS)

これは、複数のグローバルソース（NewsAPI、GNews、NewsData.io）からニュースを集約し、DeepLを使用してシームレスに翻訳するとともに、ユーザーがコンテンツを共有・議論できるソーシャルプラットフォームです。
**Web版 (Flask)** と **iOS版 (SwiftUI)** のクロスプラットフォームで動作し、Firebaseをバックエンドとしてデータをリアルタイムに共有します。

GitHub内で公開されていたLiquid Glass（リキッドグラス）UIデザインを採用しつつ、パフォーマンスを考慮した軽量モードも実装しました。
コーディング作業は主にAIエージェントに指示を行い、意向に沿った機能を実装しています。

## 機能

### スマートニュース集約
- **マルチソース対応:** **NewsAPI**、**GNews**、**NewsData.io** から記事を取得し、幅広い情報をカバーします。
- **並列処理:** `ThreadPoolExecutor` を使用して複数のAPIから同時にデータを取得し、応答時間を短縮しています。
- **インテリジェントな重複排除:** 異なるソース間での記事の重複を自動的に排除します。

### シームレス翻訳
- **DeepL統合:** 英語と日本語の間で高品質な翻訳を提供します。
- **双方向対応:** タイトルと説明文の「英語→日本語」および「日本語→英語」の翻訳をサポートしています。

### クロスプラットフォーム・ユーザーシステム
- **Firebase統合:** **Authentication** による安全なログインと、**Firestore** によるリアルタイムデータ同期。
- **データ共有:** Web版で作成した投稿をiOS版で閲覧したり、その逆も可能です。アカウント情報も共通化されています。
- **プロフィール:** アバター画像のアップロードとプロフィール管理。
- **投稿機能:** ユーザーはタイトル、説明、画像付きで独自の投稿を作成できます。

### UI/UX (Web版)
- **Liquid Glass デザイン:** 透明感とぼかし効果を活用した、特徴的なグラスモーフィズムデザイン。
- **軽量モード (Clean Glass):** Chrome等でのパフォーマンス低下を防ぐため、アニメーションを排除した軽量でシンプルなデザインモードを搭載（設定から切り替え可能）。
- **レスポンシブ:** 様々な画面サイズに適応するカードベースのレイアウト。

### モバイル統合 (iOS)
- **Native Liquid Glass:** iOS標準のMaterial素材を生かした、ネイティブなグラスモーフィズムデザイン。
- **統合フィード:** ニュース記事とユーザー投稿がシームレスに混在するタイムライン。
- **画像最適化:** 投稿画像の自動リサイズとアスペクト比保持表示。

## 技術スタック

- **バックエンド:** Flask (API Gateway / Proxy), Firebase Admin SDK
- **データベース:** Google Cloud Firestore (NoSQL)
- **認証:** Firebase Authentication
- **HTTPクライアント:** `requests`, `httpx` (非同期処理用)
- **フロントエンド (Web):** HTML5, CSS3, Vanilla JS, Firebase JS SDK
- **モバイル (iOS):** SwiftUI, Firebase iOS SDK
- **デプロイ:** `gunicorn` (Web)

## セットアップとインストール (Web版)

### 1. 前提条件
- Python 3.11以上
- NewsAPI, GNews, NewsData.io, DeepL のAPIキー
- Firebaseプロジェクトの設定 (`firebase-adminsdk.json` およびウェブアプリ設定)

### 2. インストール

リポジトリをクローンし、依存パッケージをインストールします：

```bash
git clone <repository-url>
cd flaskdev
pip install -r requirements.txt
```

### 3. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成し、以下の変数を設定してください：

```env
# Flask設定
SECRET_KEY=your_secret_key_here

# APIキー
NEWSAPI_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_api_key_here
NEWSDATA_IO_API_KEY=your_newsdata_io_api_key_here
DEEPL_AUTH_KEY=your_deepl_auth_key_here

# Firebase設定 (Admin SDKのパスなど)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-adminsdk.json
```

### 4. アプリケーションの起動

```bash
python run.py
# または
flask run --host=0.0.0.0 --port=8000
```

ブラウザで `http://localhost:8000` にアクセス

## プロジェクト構成

```
flaskdev/
├── app/
│   ├── __init__.py        # アプリケーションファクトリ & Firebase初期化
│   ├── models.py          # (旧) SQLAlchemyモデル -> Firestore辞書定義へ移行
│   ├── routes/            # APIエンドポイント
│   │   ├── main.py        # ニュース取得・検索
│   │   ├── auth.py        # 認証連携
│   │   └── posts.py       # 投稿API (Firestore連携)
│   ├── services/          # 外部API連携サービス
│   │   ├── aggregator.py  # ニュース統合ロジック
│   │   └── deepl.py       # 翻訳サービス
│   ├── static/            # CSS (glassUI.css, lightweightUI.css), 画像
│   └── templates/         # HTML (Firebase JS SDK含む)
├── data/                  # (旧) 初期データ
├── docs/                  # ドキュメント類
├── News-Mobile/           # iOS SwiftUI プロジェクト (Firebase連携済み)
├── requirements.txt       # Python依存関係
└── run.py                 # エントリーポイント
```

## デザインと工夫

- **Web UI:** 重厚な「Liquid Glass」と軽快な「Clean Glass」の2つのテーマを実装し、ユーザーの環境に合わせて選択可能にしました。
- **iOS UI:** SwiftUIの `UltraThinMaterial` を活用し、Web版の世界観をネイティブアプリとして再現しました。
- **効率性:** API利用枠節約のため、ニュース更新はオンデマンド方式を採用。
- **安全性:** 開発プロセスにAIエージェントガイドライン (`docs/agents.md`) を導入し、品質を維持しています。

## 今後の改善案

- **エラーハンドリング:** API制限時のフォールバック処理強化（完了）。
- **ページネーション:** ニュースAPIからの大量の結果に対するページ送り機能。
- **iOSウィジェット:** ホーム画面でのニュース表示。
- **プッシュ通知:** 新着ニュースやコメントの通知（FCM利用）。
