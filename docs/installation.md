# インストールガイド

## システム要件

### 推奨環境
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8以上（推奨: 3.9以上）
- **RAM**: 4GB以上（推奨: 8GB以上）
- **ストレージ**: 1GB以上の空き容量

### ブラウザ要件
- Chrome 80+
- Firefox 75+
- Edge 80+
- Safari 13+

## インストール手順

### 1. Python環境の確認

```bash
python --version
```

Python 3.8以上が必要です。インストールされていない場合は、[Python公式サイト](https://www.python.org/)からダウンロードしてインストールしてください。

### 2. プロジェクトのダウンロード

#### Git経由
```bash
git clone https://github.com/yourusername/TrustCAD-Analyzer.git
cd TrustCAD-Analyzer
```

#### ZIPファイル経由
1. GitHubリポジトリのページで「Code」→「Download ZIP」をクリック
2. ダウンロードしたファイルを展開
3. コマンドプロンプト/ターミナルで展開したフォルダに移動

### 3. 仮想環境の作成

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

仮想環境が有効化されると、プロンプトの先頭に`(venv)`が表示されます。

### 4. 依存パッケージのインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. データベースの初期化

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. アプリケーションの起動

```bash
python app.py
```

成功すると以下のようなメッセージが表示されます：
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
```

### 7. ブラウザでアクセス

ブラウザで `http://localhost:5000` にアクセスしてください。

## トラブルシューティング

### よくある問題

#### 1. `ModuleNotFoundError: No module named 'ezdxf'`

**原因**: 依存パッケージが正しくインストールされていない

**解決策**:
```bash
pip install -r requirements.txt
```

#### 2. `sqlite3.OperationalError: no such table`

**原因**: データベースが初期化されていない

**解決策**:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### 3. `Address already in use`

**原因**: ポート5000が他のプロセスで使用中

**解決策**:
```bash
# 別のポートを指定
python app.py --port=5001
```

#### 4. DXFファイルのアップロードでエラー

**原因**: 
- ファイルサイズが大きすぎる
- ファイル形式が対応していない

**解決策**:
- ファイルサイズを確認（推奨: 10MB未満）
- DXFファイルの形式を確認（R2010以降を推奨）

### ログの確認

問題が発生した場合は、コンソールに表示されるエラーメッセージを確認してください。

```bash
python app.py
```

### パフォーマンスの最適化

#### メモリ使用量の削減
- 大きなDXFファイルを処理する場合は、できるだけファイルサイズを小さくしてください
- 複数のプロジェクトを同時に開くのを避けてください

#### 処理速度の向上
- SSD環境での実行を推奨します
- CPUコア数が多い環境で実行してください

## アンインストール

### 1. 仮想環境の無効化
```bash
deactivate
```

### 2. プロジェクトフォルダの削除
```bash
rm -rf TrustCAD-Analyzer  # macOS/Linux
rmdir /s TrustCAD-Analyzer  # Windows
```

### 3. Python仮想環境の削除
プロジェクトフォルダ内の`venv`フォルダも一緒に削除されます。

## 本番環境での運用

### セキュリティ設定
1. `app.py`内の`SECRET_KEY`を変更
2. データベースのパスワード設定
3. HTTPSの設定

### パフォーマンス設定
1. Gunicorn/uWSGIの使用
2. Nginxでのリバースプロキシ設定
3. データベースの最適化

詳細は[デプロイガイド](deployment.md)を参照してください。