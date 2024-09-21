from fastapi import APIRouter, HTTPException
from uuid import UUID
from datetime import datetime
from server.api.schemas import UserStatus, UserList, StatusEnum

# FastAPIのルーターを作成
api = APIRouter()

# サンプルデータ：ユーザーのステータス情報
sample_users = {
    UUID("c9b1b9b5-5e8c-456a-a8f7-23dabaafca9a"): UserStatus(
        user_id=UUID("c9b1b9b5-5e8c-456a-a8f7-23dabaafca9a"),
        name="Alice",
        status=StatusEnum.open,
        created_at=datetime(2023, 9, 1)
    ),
    UUID("b5d9c9b9-b91e-45d6-90d1-40e91b9443ca"): UserStatus(
        user_id=UUID("b5d9c9b9-b91e-45d6-90d1-40e91b9443ca"),
        name="Bob",
        status=StatusEnum.closed,
        created_at=datetime(2023, 6, 15)
    )
}

# 全ユーザーのステータスを取得するAPI
@api.get("/users", response_model=UserList)
async def get_all_user_status():
    # sample_usersの値をリスト形式で取得し、レスポンスを返す
    return UserList(users=list(sample_users.values()))

# ユーザーのステータスを取得するエンドポイント
@api.get("/users/{user_id}", response_model=UserStatus)
async def get_user_status(user_id: UUID):
    if user_id in sample_users:
        return sample_users[user_id]
    raise HTTPException(status_code=404, detail="User not found")
