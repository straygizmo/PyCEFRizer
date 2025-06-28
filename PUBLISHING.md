# PyPIへの公開手順

## 事前準備

### 1. PyPIアカウントの作成

1. [PyPI](https://pypi.org/)にアクセスして、アカウントを作成
2. [TestPyPI](https://test.pypi.org/)にも同様にアカウントを作成（テスト用）

### 2. API トークンの設定

セキュリティのため、API トークンを使用することを推奨します。

1. PyPIにログイン後、アカウント設定から「API tokens」を選択
2. 「Add API token」をクリック
3. トークン名を入力し、スコープを選択（最初は「Entire account」でOK）
4. トークンをコピーして安全に保管

### 3. `.pypirc`ファイルの設定（オプション）

ホームディレクトリに`.pypirc`ファイルを作成すると、認証情報を保存できます：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJDU1NTU1NTU1LTU1NTUtNTU1NS01NTU1LTU1NTU1NTU1NTU1NQ...

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZwIkNTU1NTU1NTUtNTU1NS01NTU1LTU1NTUtNTU1NTU1NTU1NTU1...
```

**注意**: `.pypirc`ファイルには機密情報が含まれるため、パーミッションを600に設定してください：
```bash
chmod 600 ~/.pypirc
```

## 公開手順

### 1. 必要なツールのインストール

```bash
# ビルドツール
pip install build

# アップロードツール
pip install twine
```

### 2. パッケージのビルド

```bash
# プロジェクトのルートディレクトリで実行
python -m build
```

これにより`dist/`ディレクトリに以下のファイルが作成されます：
- `pycefrizer-3.0.0.tar.gz` (ソース配布物)
- `pycefrizer-3.0.0-py3-none-any.whl` (Wheel配布物)

### 3. ビルドしたパッケージの確認

```bash
# パッケージの内容を確認
tar -tzf dist/pycefrizer-3.0.0.tar.gz

# Wheelの内容を確認
unzip -l dist/pycefrizer-3.0.0-py3-none-any.whl

# パッケージの検証
twine check dist/*
```

### 4. TestPyPIへのアップロード（推奨）

本番環境にアップロードする前に、TestPyPIでテストすることを強く推奨します。

```bash
# TestPyPIにアップロード
twine upload --repository testpypi dist/*
```

プロンプトが表示されたら：
- Username: `__token__`
- Password: TestPyPI用のAPIトークン

### 5. TestPyPIからインストールしてテスト

```bash
# 新しい仮想環境を作成
python -m venv test-env
source test-env/bin/activate  # Windowsの場合: test-env\Scripts\activate

# TestPyPIからインストール
# 注: パッケージ名は実際にTestPyPIに公開した後に利用可能になります
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pycefrizer

# 動作確認
python -c "import pycefrizer; print(pycefrizer.__version__)"
pycefrizer --version
```

### 6. 本番のPyPIへのアップロード

テストが成功したら、本番環境にアップロードします：

```bash
twine upload dist/*
```

プロンプトが表示されたら：
- Username: `__token__`
- Password: PyPI用のAPIトークン

### 7. 公開の確認

```bash
# PyPIからインストール
# 注: パッケージ名は実際にPyPIに公開した後に利用可能になります
pip install pycefrizer

# パッケージページを確認
# https://pypi.org/project/pycefrizer/
```

## バージョンアップ時の手順

### 1. バージョン番号の更新

以下のファイルでバージョン番号を更新：
- `pyproject.toml`
- `setup.py`
- `pycefrizer/__init__.py`

### 2. 変更履歴の更新

`CHANGELOG.md`を作成/更新して変更内容を記録

### 3. 古いビルドファイルの削除

```bash
rm -rf dist/ build/ *.egg-info/
```

### 4. 新しいバージョンをビルド・アップロード

```bash
python -m build
twine upload dist/*
```

## トラブルシューティング

### よくある問題

1. **パッケージ名が既に使用されている**
   - パッケージ名を変更する必要があります
   - `pyproject.toml`と`setup.py`の`name`フィールドを更新

2. **認証エラー**
   - APIトークンが正しくコピーされているか確認
   - `__token__`をユーザー名として使用しているか確認

3. **ファイルが含まれない**
   - `MANIFEST.in`を確認
   - `pyproject.toml`の`package-data`設定を確認

### セキュリティのベストプラクティス

1. APIトークンは環境変数で管理
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJDU1NTU1NTU1LTU1NTUtNTU1NS01NTU1LTU1NTU1NTU1NTU1NQ...
   twine upload dist/*
   ```

2. プロジェクトごとにスコープを限定したAPIトークンを使用

3. 2要素認証を有効化

## 参考リンク

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)