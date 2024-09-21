from fastapi import FastAPI

# FastAPIインスタンスを作成
app = FastAPI()

# server.api.apiモジュールをインポートし、ルーターを登録
from server.api.api import api

# ルーターを登録
app.include_router(api)
