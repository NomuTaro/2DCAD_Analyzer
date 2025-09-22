# Contributing to TrustCAD Analyzer

TrustCAD Analyzerプロジェクトへの貢献をありがとうございます！このドキュメントでは、プロジェクトに貢献するためのガイドラインを説明します。

## 貢献の方法

### バグレポート

バグを発見した場合は、以下の手順で報告してください：

1. [GitHub Issues](https://github.com/yourusername/TrustCAD-Analyzer/issues)を確認し、既に同じ問題が報告されていないかチェック
2. 新しいissueを作成し、以下の情報を含めてください：
   - 問題の簡潔な説明
   - 再現手順
   - 期待する動作
   - 実際の動作
   - 環境情報（OS、Python版数、ブラウザなど）
   - エラーメッセージやスクリーンショット（該当する場合）

### 機能要求

新機能の提案は以下の手順で行ってください：

1. [GitHub Issues](https://github.com/yourusername/TrustCAD-Analyzer/issues)で`enhancement`ラベルを使用
2. 以下の情報を含めてください：
   - 機能の概要と目的
   - 具体的な使用例
   - 期待する効果・メリット
   - 可能であれば実装のアイデア

### コード貢献

#### 開発環境のセットアップ

1. **フォークとクローン**
   ```bash
   git clone https://github.com/yourusername/TrustCAD-Analyzer.git
   cd TrustCAD-Analyzer
   ```

2. **開発用仮想環境の作成**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

3. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **開発用ブランチの作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### コーディング規約

- **Python**: PEP 8に準拠
- **HTML/CSS**: 一貫したインデント（2スペース）
- **JavaScript**: ES6+の使用を推奨

#### テスト

新しい機能やバグ修正を行う場合は、以下を実行してください：

1. **手動テスト**: 
   - 基本的なワークフローが正常に動作することを確認
   - 複数のブラウザでの動作確認

2. **サンプルファイルでのテスト**:
   - `samples/`ディレクトリのファイルを使用
   - 機器検出機能の精度確認

#### コミット・プルリクエスト

1. **コミットメッセージ**
   ```
   feat: 新機能の追加
   fix: バグ修正
   docs: ドキュメント更新
   style: コードスタイルの修正
   refactor: リファクタリング
   test: テスト追加・修正
   chore: その他の変更
   ```

2. **プルリクエスト**
   - 変更内容の明確な説明
   - 関連するissue番号の記載
   - テスト結果の共有
   - スクリーンショット（UI変更の場合）

## 開発ガイドライン

### 新しい機器タイプの追加

1. **図形定義の追加**
   ```python
   # shape_definitions.py
   SHAPE_DEFINITIONS["new_device"] = {
       "name": "新機器 (XX-XX)",
       "entity_counts": {"CIRCLE": 1, "LINE": 2},
       "anchor_type": "CIRCLE",
       "search_radius_ratio": 2.0,
       "check_function": "check_new_device"
   }
   ```

2. **チェック関数の実装**
   ```python
   def check_new_device(anchor, neighbors):
       # 機器固有の検証ロジック
       return True  # or False
   ```

3. **テンプレートの更新**
   ```html
   <!-- templates/shape_analyzer.html -->
   <option value="new_device">新機器 (XX-XX)</option>
   ```

### データベース変更

スキーマ変更が必要な場合は：

1. モデル定義を更新（`app.py`）
2. マイグレーション手順をドキュメント化
3. 後方互換性を考慮

### UI/UX改善

- Bootstrap 5.xの使用を継続
- レスポンシブデザインを維持
- アクセシビリティを考慮

## リリース プロセス

### バージョニング

セマンティック バージョニング（SemVer）に従います：
- `MAJOR.MINOR.PATCH`
- `1.0.0` → `1.0.1`（パッチ）
- `1.0.0` → `1.1.0`（マイナー）
- `1.0.0` → `2.0.0`（メジャー）

### ブランチ戦略

- `main`: 安定版
- `develop`: 開発版
- `feature/*`: 機能開発
- `hotfix/*`: 緊急修正

## コミュニティ

### コミュニケーション

- GitHub Issues: バグ報告、機能要求
- GitHub Discussions: 一般的な質問、アイデア交換
- Pull Request: コードレビューと議論

### 行動規範

以下の原則を守ってください：

1. **尊重**: 他の貢献者を尊重し、建設的なフィードバックを提供
2. **包括性**: 多様な背景を持つ人々を歓迎
3. **協力**: チームワークと知識共有を重視
4. **品質**: 高品質なコードとドキュメントを目指す

## ライセンス

貢献したコードはMITライセンスの下で公開されることに同意したものとみなします。

## 質問・サポート

不明な点がある場合は、以下の方法でお気軽にお問い合わせください：

- GitHub Issues: 技術的な質問
- GitHub Discussions: 一般的な質問
- Email: [your-email@example.com]

---

貢献してくださる皆様に心から感謝いたします！