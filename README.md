# 俺の家来ないか

## ローカル環境構築
- 前提条件
  - `pipenv`コマンドが有効

```
# 1. 依存パッケージをインストールする
pipenv install

# 2. 仮想環境をアクティブ化
pipenv shell

# 3. サーバー起動
uvicorn server.Web.app:app --reload
```

## API仕様書/APIテスト画面
APIの仕様に沿ってClientから呼び出す。

`http://localhost:8000/docs`


## Pipenvを使った仮想環境の作成と依存ファイルのインストール
```sh
# 同じ依存パッケージを確実に利用するため，本ディレクトリのPipfileとPipfile.lockが同じディレクトリに存在することを前提とする.

$ pipenv install # 依存パッケージインストール
$ pipenv shell # 仮想環境をアクティブ化
$ exit # 仮想環境から抜ける
$ pipenv --rm # 仮想環境を削除
```


## pipenv環境をvscodeで使用する方法
VSCodeがpipenvの仮想環境を認識し，パッケージを正しくインポートできるように設定する
1. コマンドパレットを開く`Cmd + Shift + P`
2. `Python: Select Interpreter`を選択
3. pipenvの仮想環境を選ぶ


## パッケージ追加時の対応
1. 依存関係の再インストール（仮想環境外で）
```sh
pipenv install
```
2. (必要に応じて)依存関係の確認
```sh
pipenv graph
```


### 補足
- 実行対象のディレクトリの下で上記のコマンドを実行する
- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`