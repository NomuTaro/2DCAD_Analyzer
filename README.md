# TrustCAD Analyzer

TrustCAD Analyzerは、交通制御システムの設計・積算業務を効率化するためのWebアプリケーションです。CAD図面（DXFファイル）から交通信号機器を自動検出・カウントし、積算レポートを生成します。

## 🚀 主要機能

### 1. DXF図形解析・カウンター
- **交通信号機器の自動検出**: CAD図面から交通信号、歩行者用灯器、制御機器などを自動認識
- **高精度パターンマッチング**: 図形の組み合わせパターンから16種類以上の機器を判別
- **カスタム検索条件**: ユーザー定義の検索パラメータで柔軟な機器検出

### 2. プロジェクト管理システム
- **マルチユーザー対応**: ユーザー認証によるプロジェクトの個別管理
- **プロジェクトエディタ**: 検出結果の編集・調整機能
- **データベース連携**: SQLiteを使用した堅牢なデータ管理

### 3. レポート生成
- **積算レポート**: 工事積算に必要な形式でのレポート出力
- **Excelファイル生成**: 色分けされたDXFデータをExcel形式で出力
- **DXF再変換**: 編集内容を反映したDXFファイルの再生成

## 🛠️ 技術仕様

### バックエンド
- **Flask**: Webアプリケーションフレームワーク
- **SQLAlchemy**: ORM・データベース管理
- **Flask-Login**: ユーザー認証システム
- **ezdxf**: DXFファイル処理ライブラリ

### データ処理
- **pandas**: データ解析・変換
- **numpy**: 数値計算・幾何学演算
- **openpyxl**: Excelファイル操作

### フロントエンド
- **Bootstrap**: レスポンシブUIフレームワーク
- **Jinja2**: テンプレートエンジン

## 📦 インストール

### 必要環境
- Python 3.8以上
- pip (Pythonパッケージマネージャー)

### セットアップ手順

1. **リポジトリのクローン**
```bash
git clone https://github.com/yourusername/TrustCAD-Analyzer.git
cd TrustCAD-Analyzer
```

2. **仮想環境の作成・有効化**
```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# macOS/Linux
source venv/bin/activate
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

4. **データベースの初期化**
```bash
python -c "from app import db; db.create_all()"
```

5. **アプリケーションの起動**
```bash
python app.py
```

6. **ブラウザでアクセス**
```
http://localhost:5000
```

## 🔧 使用方法

### 基本的なワークフロー

1. **ユーザー登録・ログイン**
   - 新規ユーザーはアカウントを作成
   - 既存ユーザーはログイン

2. **プロジェクト作成**
   - 「新しいプロジェクト」から開始
   - DXFファイルをアップロード
   - プロジェクト名を設定

3. **図形解析**
   - 「DXF図形カウンター」機能を使用
   - 検出したい機器タイプを選択
   - 自動検出結果を確認

4. **レポート編集**
   - プロジェクトエディタで結果を調整
   - 数量・単価・仕様を編集
   - 項目の並び替え・追加・削除

5. **出力・保存**
   - 印刷用レポートの生成
   - 色変更Excelファイルのダウンロード
   - DXF再変換ファイルの出力

### 検出可能な機器一覧

#### 01群: 柱類
- 専用柱 (01-01)
- 関電柱 (01-02)
- 照明柱 (01-04, 01-05, 01-06)

#### 02群: 車両用灯器
- 横型3位式 (02-01)
- 両面横型3位式 (02-02)
- 縦型3位式 (02-13)
- 予告灯用 (02-14)
- 矢印灯器 (02-18)

#### 03群: 歩行者用灯器
- 2位式(抱込型) (03-01)

#### 04群: 設備
- 制御機 (04-01)
- 付加装置 (04-02)

#### 05群: 感知器
- 感知器アーム (05-02)

#### 06群: 形態
- ハンドホール (06-01)

## 📁 プロジェクト構造

```
TrustCAD-Analyzer/
├── app.py                 # メインアプリケーション
├── shape_definitions.py   # 図形定義・検出ロジック
├── requirements.txt       # Python依存関係
├── app_final.db          # SQLiteデータベース
├── templates/            # HTMLテンプレート
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── editor_home.html
│   ├── editor.html
│   ├── shape_analyzer.html
│   └── report.html
├── uploads/              # アップロードファイル保存先
├── instance/             # Flask設定ファイル
├── docs/                 # ドキュメント
│   ├── installation.md
│   ├── user-guide.md
│   └── api-reference.md
└── samples/              # サンプルファイル
    ├── sample.dxf
    └── README.md
```

## 🧪 開発・テスト

### 開発環境の設定
```bash
# デバッグモードでの起動
export FLASK_ENV=development  # macOS/Linux
set FLASK_ENV=development     # Windows
python app.py
```

### サンプルデータの使用
`samples/`フォルダにサンプルDXFファイルが含まれています。機能テストにご活用ください。

## 🤝 貢献

プロジェクトへの貢献を歓迎します！

1. フォークを作成
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## 🆘 サポート

問題や質問がありましたら、以下の方法でお気軽にお問い合わせください：

- GitHub Issues: バグレポートや機能要求
- Email: [your-email@example.com]
- Wiki: [プロジェクトWiki](https://github.com/yourusername/TrustCAD-Analyzer/wiki)

## 🏆 謝辞

このプロジェクトは以下の技術・ライブラリを使用して開発されました：

- [Flask](https://flask.palletsprojects.com/)
- [ezdxf](https://ezdxf.readthedocs.io/)
- [pandas](https://pandas.pydata.org/)
- [Bootstrap](https://getbootstrap.com/)

---

**TrustCAD Analyzer** - 交通制御システム設計の効率化を支援します。