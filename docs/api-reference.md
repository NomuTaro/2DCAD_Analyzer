# API リファレンス

## 概要

TrustCAD AnalyzerのWebアプリケーションAPIの詳細仕様です。このAPIは主にFlaskアプリケーション内で使用される内部APIですが、システムの理解や拡張のための参考資料として提供しています。

## 認証

すべてのAPI（ログイン・登録以外）はFlask-Loginによる認証が必要です。

## エンドポイント一覧

### 認証関連

#### POST /login
ユーザーログイン

**リクエストパラメータ:**
- `username` (string): ユーザー名
- `password` (string): パスワード

**レスポンス:**
- 成功: ホーム画面へリダイレクト
- 失敗: ログイン画面にエラーメッセージ表示

#### POST /register
新規ユーザー登録

**リクエストパラメータ:**
- `username` (string): ユーザー名
- `password` (string): パスワード

**レスポンス:**
- 成功: ホーム画面へリダイレクト
- 失敗: 登録画面にエラーメッセージ表示

#### GET /logout
ログアウト

**レスポンス:**
- ログイン画面へリダイレクト

### プロジェクト管理

#### GET /
ホーム画面表示

**レスポンス:**
- HTML: メインメニュー

#### GET /editor_home
プロジェクト管理画面表示

**レスポンス:**
- HTML: プロジェクト一覧と新規作成フォーム

#### POST /create_project
新規プロジェクト作成

**リクエストパラメータ:**
- `project_name` (string): プロジェクト名
- `dxf_file` (file): DXFファイル

**レスポンス:**
- 成功: プロジェクトエディタへリダイレクト
- 失敗: プロジェクト管理画面にエラーメッセージ表示

#### POST /delete_project/<int:project_id>
プロジェクト削除

**URLパラメータ:**
- `project_id` (int): プロジェクトID

**レスポンス:**
- 成功: プロジェクト管理画面へリダイレクト

#### GET /editor/<int:project_id>
プロジェクトエディタ表示

**URLパラメータ:**
- `project_id` (int): プロジェクトID

**レスポンス:**
- HTML: プロジェクト編集画面

### DXF図形解析

#### GET /shape_analyzer
#### POST /shape_analyzer
DXF図形解析画面

**GETレスポンス:**
- HTML: 図形解析画面

**POSTリクエストパラメータ:**
- `upload_file` (file): DXFファイル（新規アップロード時）
- `project_id` (int): 既存プロジェクトID
- `search_type` (string): 検索タイプ
  - `"specific"`: 特定機器検索
  - `"vehicle"`: 車両用信号機検索
  - `"pedestrian"`: 歩行者用信号機検索
- `item_type` (string): 機器タイプ（specific時）
- `custom_params` (JSON string): カスタム検索パラメータ

**POSTレスポンス:**
- HTML: 検索結果表示

### プロジェクトアイテム操作

#### POST /editor/<int:project_id>/add_item
アイテム追加

**URLパラメータ:**
- `project_id` (int): プロジェクトID

**リクエストパラメータ:**
- `item_type` (string): アイテムタイプ
- `hinmei` (string): 品名
- `hinshitsu` (string): 品質
- `suryo` (int): 数量
- `tani` (string): 単位
- `color` (int): 色番号

**レスポンス:**
- プロジェクトエディタへリダイレクト

#### POST /editor/<int:project_id>/add_subtotal
小計追加

**URLパラメータ:**
- `project_id` (int): プロジェクトID

**レスポンス:**
- プロジェクトエディタへリダイレクト

#### POST /editor/<int:project_id>/update_all
全アイテム更新

**URLパラメータ:**
- `project_id` (int): プロジェクトID

**リクエストパラメータ:**
- `kouji_basho` (string): 工事場所
- `gokei_kingaku` (string): 合計金額
- `page_number` (string): ページ番号
- `hinmei_{i}` (string): i番目のアイテムの品名
- `hinshitsu_{i}` (string): i番目のアイテムの品質
- `tani_{i}` (string): i番目のアイテムの単位
- `color_{i}` (int): i番目のアイテムの色

**レスポンス:**
- プロジェクトエディタへリダイレクト

#### POST /editor/<int:project_id>/move_item/<int:item_id>/<direction>
アイテム移動

**URLパラメータ:**
- `project_id` (int): プロジェクトID
- `item_id` (int): アイテムID
- `direction` (string): 移動方向（`"up"` | `"down"`）

**レスポンス:**
- プロジェクトエディタへリダイレクト

#### POST /editor/<int:project_id>/delete_item/<int:item_id>
アイテム削除

**URLパラメータ:**
- `project_id` (int): プロジェクトID
- `item_id` (int): アイテムID

**レスポンス:**
- プロジェクトエディタへリダイレクト

### レポート生成

#### POST /editor/<int:project_id>/generate
レポート・Excelファイル生成

**URLパラメータ:**
- `project_id` (int): プロジェクトID

**リクエストパラメータ:**
- `report` (string): 印刷用レポート生成フラグ
- `excel` (string): Excelファイル生成フラグ

**レスポンス:**
- `report`指定時: HTML レポート表示
- `excel`指定時: Excelファイルダウンロード

#### POST /editor/<int:project_id>/generate_dxf
DXF再変換

**URLパラメータ:**
- `project_id` (int): プロジェクトID

**レスポンス:**
- DXFファイルダウンロード

## データモデル

### User
ユーザー情報

```python
{
    "id": int,              # ユーザーID
    "username": str,        # ユーザー名
    "password_hash": str,   # パスワードハッシュ
    "projects": [Project]   # 関連プロジェクト
}
```

### Project
プロジェクト情報

```python
{
    "id": int,                    # プロジェクトID
    "name": str,                  # プロジェクト名
    "user_id": int,               # オーナーユーザーID
    "kouji_basho": str,           # 工事場所
    "gokei_kingaku": str,         # 合計金額
    "page_number": str,           # ページ番号
    "original_dxf_path": str,     # 元DXFファイルパス
    "converted_excel_path": str,  # 変換Excelファイルパス
    "items": [ReportItem]         # 関連アイテム
}
```

### ReportItem
レポートアイテム情報

```python
{
    "id": int,               # アイテムID
    "project_id": int,       # プロジェクトID
    "order": int,            # 表示順序
    "item_type": str,        # アイテムタイプ
    "hinmei": str,           # 品名
    "hinshitsu": str,        # 品質
    "suryo": int,            # 数量
    "tani": str,             # 単位
    "search_params": str,    # 検索パラメータ（JSON）
    "color": int             # 色番号
}
```

## 図形検出システム

### 検出可能な図形タイプ

図形検出は `shape_definitions.py` で定義されています。

#### 基本図形要素
- `LINE`: 直線
- `CIRCLE`: 円
- `ARC`: 円弧
- `TEXT`: テキスト

#### 複合図形パターン
各機器は複数の基本図形要素の組み合わせパターンで定義されます。

```python
SHAPE_DEFINITIONS = {
    "dedicated_pole": {
        "name": "専用柱 (01-01)",
        "entity_counts": {"CIRCLE": 2},
        "anchor_type": "CIRCLE",
        "search_radius_ratio": 1.5,
        "check_function": "check_dedicated_pole"
    },
    # ... 他の定義
}
```

### 検出アルゴリズム

1. **基本図形抽出**: DXFファイルから基本図形要素を抽出
2. **アンカー図形特定**: 各図形定義のアンカータイプに基づき基準図形を特定
3. **近接図形検索**: アンカー図形周辺の指定範囲内で関連図形を検索
4. **パターンマッチング**: 図形の組み合わせと配置パターンを照合
5. **検証**: 幾何学的な制約条件をチェック

### カスタム検索パラメータ

```json
{
    "search_radius": 10.0,     // 検索半径
    "tolerance": 0.1,          // 許容誤差
    "color_filter": null,      // 色フィルター（null=全色）
    "scale_factor": 1.0        // スケール係数
}
```

## エラーハンドリング

### HTTPステータスコード
- `200`: 成功
- `400`: 不正なリクエスト
- `403`: アクセス権限なし
- `404`: リソースが見つからない
- `500`: 内部サーバーエラー

### エラーレスポンス形式

```json
{
    "error": "エラーメッセージ",
    "code": "ERROR_CODE",
    "details": "詳細情報（デバッグ時のみ）"
}
```

## 拡張ポイント

### 新しい機器タイプの追加

1. `shape_definitions.py`に図形定義を追加
2. 対応するチェック関数を実装
3. テンプレートファイルに選択肢を追加

### カスタム出力形式の追加

1. `generate()`関数を拡張
2. 新しいテンプレートファイルを作成
3. 必要に応じてMIMEタイプを設定

---

詳細な実装については、ソースコードのコメントも併せて参照してください。