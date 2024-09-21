# ベースイメージとして公式のPython 3.10イメージを使用
FROM python:3.10-slim

# 作業ディレクトリを作成
WORKDIR /app

# PipenvやPython依存関係をインストール
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy

# アプリケーションコードをコンテナにコピー
COPY . /app

# 環境変数を設定（Firestoreの認証ファイルなど）
ENV GOOGLE_APPLICATION_CREDENTIALS=firebase-adminsdk.json

# FastAPIを起動するためのUvicornをインストール
RUN pip install "uvicorn[standard]"

# アプリケーションを起動するためのコマンド
CMD ["uvicorn", "server.Web.app:app", "--host", "0.0.0.0", "--port", "8080"]
