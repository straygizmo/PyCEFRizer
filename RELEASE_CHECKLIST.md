# リリースチェックリスト

PyPIに公開する前に、以下の項目を確認してください：

## 必須項目

- [ ] **バージョン番号の一致**
  - [ ] `pyproject.toml` のversion
  - [ ] `setup.py` のversion
  - [ ] `pycefrizer/__init__.py` の`__version__`
  - [ ] `pycefrizer/cli.py` の`--version`出力

- [ ] **ライセンス**
  - [ ] `LICENSE`ファイルが存在する
  - [ ] `pyproject.toml`でライセンスが指定されている
  - [ ] ライセンスがプロジェクトに適切である

- [ ] **必須ファイルの確認**
  - [ ] `README.md`
  - [ ] `CHANGELOG.md`
  - [ ] `MANIFEST.in`
  - [ ] `pyproject.toml`
  - [ ] `setup.py`

- [ ] **データファイルの確認**
  - [ ] `pycefrizer/data/word_lookup.json`が存在
  - [ ] `pycefrizer/data/coca_frequencies.json`が存在
  - [ ] データファイルがMANIFEST.inに含まれている

- [ ] **依存関係**
  - [ ] すべての依存関係が`pyproject.toml`に記載されている
  - [ ] バージョン指定が適切である
  - [ ] spaCyモデルのダウンロード手順が文書化されている

## テスト項目

- [ ] **ローカルインストールテスト**
  ```bash
  pip install -e .
  pycefrizer --version
  ```

- [ ] **パッケージビルド**
  ```bash
  python -m build
  twine check dist/*
  ```

- [ ] **基本動作確認**
  ```bash
  # CLI
  pycefrizer "This is a test text."
  
  # Python API
  python -c "import pycefrizer; print(pycefrizer.analyze('Test text'))"
  ```

- [ ] **データファイルの読み込み確認**
  ```python
  from pycefrizer import PyCEFRizer
  analyzer = PyCEFRizer()  # エラーが出ないことを確認
  ```

## ドキュメント確認

- [ ] **README.md**
  - [ ] インストール手順が正確
  - [ ] 使用例が動作する
  - [ ] APIドキュメントが最新
  - [ ] 連絡先/リポジトリURLが正しい

- [ ] **コード内のドキュメント**
  - [ ] すべてのクラス/関数にdocstringがある
  - [ ] 著作権表示が適切

## セキュリティ確認

- [ ] **機密情報のチェック**
  - [ ] APIキー、パスワードが含まれていない
  - [ ] 個人情報が含まれていない
  - [ ] `.gitignore`が適切に設定されている

- [ ] **依存関係のセキュリティ**
  - [ ] 既知の脆弱性がある依存関係を使用していない

## 最終確認

- [ ] **クリーンな環境でのテスト**
  ```bash
  # 新しい仮想環境でテスト
  python -m venv test-release
  source test-release/bin/activate
  pip install dist/pycefrizer-*.whl
  pip install spacy
  python -m spacy download en_core_web_sm
  pycefrizer "Test text"
  ```

- [ ] **パッケージサイズの確認**
  - [ ] 不要なファイルが含まれていない
  - [ ] データファイルのサイズが適切

## 公開後の確認

- [ ] PyPIページが正しく表示される（PyPIに公開した場合）
- [ ] `pip install pycefrizer`が動作する（PyPIに公開した場合）
- [ ] ドキュメントのリンクが有効
- [ ] GitHubにタグを作成
  ```bash
  git tag v3.0.0
  git push origin v3.0.0
  ```