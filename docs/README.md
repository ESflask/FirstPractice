# マルチソース・ニュースアグリゲーター & ソーシャルプラットフォーム

これは、複数のグローバルソース（NewsAPI、GNews、NewsData.io）からニュースを集約し、DeepLを使用してシームレスに翻訳するとともに、ユーザーがコンテンツを共有・議論できるソーシャルプラットフォームを提供するFlaskベースのWebアプリケーションです。特徴的な「Liquid Glass（リキッドグラス）」UIデザインを採用しています。

## 機能

### スマートニュース集約
- **マルチソース対応:** **NewsAPI**、**GNews**、**NewsData.io** から記事を取得し、幅広い情報をカバーします。
- **並列処理:** `ThreadPoolExecutor` を使用して複数のAPIから同時にデータを取得し、応答時間を短縮しています。
- **インテリジェントな重複排除:** 異なるソース間での記事の重複を自動的に排除します。

### シームレス翻訳
- **DeepL統合:** 英語と日本語の間で高品質な翻訳を提供します。
- **双方向対応:** タイトルと説明文の「英語→日本語」および「日本語→英語」の翻訳をサポートしています。

### ユーザーシステム
- **認証機能:** 安全なアカウント登録とログインシステム。
- **プロフィール:** アバターアップロード機能を備えたユーザープロフィール。
- **投稿機能:** ユーザーはタイトル、説明、画像付きで独自の投稿を作成できます。
- **内部検索:** 外部ニュースAPIと内部ユーザー投稿の両方を一度に検索できる統合検索機能。

### UI/UX
- **Liquid Glass デザイン:** 透明感とぼかし効果を活用した、特徴的なグラスモーフィズムデザイン。
- **レスポンシブ:** 様々な画面サイズに適応するカードベースのレイアウト。
- **動的更新:** APIの利用枠を節約するため、自動更新ではなく「APIを更新」ボタンによるオンデマンド更新を採用しています。

### モバイル統合
- **iOSアプリ:** ネイティブモバイル体験を提供するSwiftUIプロジェクト（`News-Mobile/`）が含まれています（現在開発中）。

## 技術スタック

- **バックエンド:** Flask, Flask-SQLAlchemy
- **データベース:** SQLite (デフォルト) / PostgreSQL (設定により対応可能)
- **HTTPクライアント:** `requests`, `httpx` (非同期処理用)
- **非同期処理:** `concurrent.futures.ThreadPoolExecutor`
- **フロントエンド:** Jinja2 Templates, CSS (Glassmorphism), JavaScript
- **デプロイ:** `gunicorn` でのデプロイに対応可能な構成

## セットアップとインストール

### 1. 前提条件
- Python 3.11以上
- NewsAPI, GNews, NewsData.io, DeepL のAPIキー

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
DATABASE_URL=sqlite:///project.db

# APIキー
NEWSAPI_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_api_key_here
NEWSDATA_IO_API_KEY=your_newsdata_io_api_key_here
DEEPL_AUTH_KEY=your_deepl_auth_key_here
```

### 4. データベースの初期化

初回実行時、アプリケーションは自動的にデータベースを初期化し、`data/users.json` および `data/posts.json` が存在する場合はそこからデータを移行します。

### 5. アプリケーションの起動

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
│   ├── __init__.py        # アプリケーションファクトリ & DB設定
│   ├── models.py          # SQLAlchemyモデル (User, Post)
│   ├── routes/            # Blueprints (ルーティング)
│   │   ├── main.py        # メインページ & 検索API
│   │   ├── auth.py        # 認証機能
│   │   ├── posts.py       # ユーザー投稿機能
│   │   └── admin.py       # 管理画面
│   ├── services/          # 外部API連携サービス
│   │   ├── aggregator.py  # ニュース取得と翻訳のオーケストレーション
│   │   ├── deepl.py       # DeepL API ラッパー
│   │   ├── newsapi.py     # NewsAPI ラッパー
│   │   ├── gnews.py       # GNews ラッパー
│   │   └── newsdata.py    # NewsData.io ラッパー
│   ├── static/            # CSS, 画像, アップロードファイル
│   └── templates/         # HTMLテンプレート
├── data/                  # 初期シードデータ (JSON)
├── docs/                  # ドキュメント類
├── instance/              # SQLiteデータベース
├── News-Mobile/           # iOS SwiftUI プロジェクト
├── tests/                 # ユニットテスト
├── requirements.txt       # Python依存関係
└── run.py                 # エントリーポイント
```

## デザイン哲学と工夫

- **ビジュアル:** (Web版において)「Liquid Glass」デザインは、透明度とぼかし効果を使用して奥行きを作り出しています。タイトル画像が見えにくくならないよう、文字の縁取りなどの工夫を施しています。
- **効率性:** 無料版APIの制限を考慮し、自動更新は行わず、ユーザーが「APIを更新」ボタンを押した時のみリクエストを送信する設計にしています。これによりトークン消費を抑えています。
- **安全性:** AIを活用した開発プロセスを `docs/agents.md` に記録し、意図しないコード変更を防ぐためのガイドラインを設けています。

## 今後の改善案

- **エラーハンドリング:** API制限やネットワークエラー時のUIフィードバックの強化。
- **ページネーション:** ニュースAPIからの大量の結果に対するページ送り機能の実装。
- **AI要約:** OpenAI API等を活用した記事の要約機能の追加。
- **モバイルアプリ:** バックエンドと連携するSwiftUIアプリの完全実装。
