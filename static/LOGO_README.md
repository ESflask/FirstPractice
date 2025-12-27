# ロゴのアップロード方法

## 手順

1. **ロゴファイルを準備**
   - 推奨形式: PNG（透過背景推奨）
   - 推奨サイズ: 高さ 80-120px（幅は自動調整されます）
   - ファイル名: `logo.png`

2. **ロゴを配置**
   以下のパスにロゴファイルを配置してください：
   ```
   /Users/endoushougo/Python_pjs/django/flaskdev/static/logo.png
   ```

3. **確認**
   - ブラウザをリフレッシュすると、トップバーの左側にロゴが表示されます
   - ロゴが見つからない場合は、何も表示されません（エラーにはなりません）

## 別の形式を使用する場合

JPEGやSVGを使用したい場合は、`templates/testapp/index.html`の以下の行を編集してください：

```html
<img src="{{ url_for('static', filename='logo.png') }}" alt="Logo" style="height: 40px;" onerror="this.style.display='none';">
```

ファイル名を変更（例: `logo.jpg` または `logo.svg`）
