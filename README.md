# 英語ニュース記事の日本語翻訳表示システム

このアプリケーションは、NewsAPIから英語のニュース記事を取得し、DeepL APIを使用して日本語に翻訳して表示するFlaskアプリケーションです。

## 機能

- NewsAPIから最新のニュース記事を取得
- DeepL APIを使用して記事のタイトルと説明を日本語に翻訳
- 翻訳された記事を美しいUIで表示
- 元の英語記事も併せて表示（参考用）

## 必須のセットアップ手順

### 1. 必要なパッケージのインストール

```bash
pip install flask requests python-dotenv
```

### 2. 環境変数の設定

`.env`ファイルをプロジェクトルートに作成し、以下の環境変数を設定します（必要に応じて）：

```env
NEWSAPI_KEY=your_newsapi_key_here
```

**注意**: 現在のコードでは、APIキーは直接コード内に記述されています。本番環境では環境変数を使用することを推奨します。

### 3. APIキーの確認

以下のファイルでAPIキーが正しく設定されているか確認してください：

- `newsapi.py`: NewsAPIのAPIキー（5行目）
- `deepl.py`: DeepLの認証キー（3行目）

### 4. アプリケーションの起動

```bash
python firstpractice.py
```

アプリケーションは `http://0.0.0.0:8000` で起動します。

ブラウザで `http://localhost:8000` にアクセスして、翻訳された記事を確認できます。

## ファイル構成

```
Flask1st/
├── firstpractice.py      # メインのFlaskアプリケーション
├── newsapi.py            # NewsAPIから記事を取得するモジュール
├── deepl.py              # DeepL APIを使用して翻訳するモジュール
├── templates/
│   └── testapp/
│       └── index.html    # 記事を表示するHTMLテンプレート
└── README.md             # このファイル
```

## コードの動作フロー

### 1. 記事の取得 (`newsapi.py`)

- `fetch_full_articles()` 関数がNewsAPIから記事を取得
- 各記事のタイトル、説明、URL、画像URL、公開日、出典を取得

### 2. 翻訳処理 (`firstpractice.py`)

- `get_translated_articles()` 関数が記事を取得
- 各記事のタイトルと説明を `translate_to_ja()` 関数で日本語に翻訳
- 翻訳済みの記事データをリストとして返す

### 3. 表示処理 (`templates/testapp/index.html`)

- Flaskのテンプレートエンジン（Jinja2）を使用
- 各記事をカード形式で表示
- 画像、出典、公開日、元記事へのリンクも表示

## カスタマイズ方法

### 検索クエリの変更

`firstpractice.py`の`index()`関数内で、検索クエリを変更できます：

```python
articles = get_translated_articles(query="Apple", page_size=5)
```

例：
- `query="Technology"` - テクノロジー関連の記事
- `query="Japan"` - 日本関連の記事
- `query="AI OR artificial intelligence"` - AI関連の記事

### 表示記事数の変更

`page_size`パラメータで取得する記事数を変更できます：

```python
articles = get_translated_articles(query="Apple", page_size=10)
```

### スタイルのカスタマイズ

`templates/testapp/index.html`の`<style>`セクションを編集して、デザインをカスタマイズできます。

## トラブルシューティング

### 記事が表示されない場合

1. APIキーが正しく設定されているか確認
2. インターネット接続を確認
3. NewsAPIとDeepL APIの利用制限に達していないか確認
4. ターミナルにエラーメッセージが表示されていないか確認

### 翻訳が正しく表示されない場合

1. DeepL APIの認証キーが正しいか確認
2. 翻訳対象のテキストが空でないか確認
3. DeepL APIの利用制限に達していないか確認

### 画像が表示されない場合

- 記事に画像URLが含まれていない場合、プレースホルダーが表示されます
- 画像URLが無効な場合、自動的にプレースホルダーに切り替わります

## 注意事項

- NewsAPIの無料プランには1日あたりのリクエスト数に制限があります
- DeepL APIの無料プランにも月間の翻訳文字数に制限があります
- 本番環境では、APIキーを環境変数や設定ファイルから読み込むようにしてください
- エラーハンドリングを追加して、APIエラー時の適切な処理を実装することを推奨します

## 今後の改善案

- エラーハンドリングの強化
- キャッシュ機能の追加（同じ記事を再翻訳しない）
- ページネーション機能の追加
- 検索機能の追加
- 翻訳言語の選択機能
- レスポンシブデザインの改善

## デザイン

- ガラス調のデザインを採用、タイトルは見えにくくならないように縁を白くしました。
- GitHub内でapple liquid glassデザインを再現している方のcssコードを適応させています。
- ![0CE4467F-9268-4062-9587-682A527C5650_1_201_a](https://github.com/user-attachments/assets/fa9e7886-e2b5-4aa8-b2eb-7e79224b9515)

## 工夫

- 無料版のnewsAPI,deeplAPIを使用したため、newsAPIのリクエスト回数に制限があるので、APIを更新というボタンを作り、トークンを節約してます
