from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import List

# 列挙型スキーマを宣言
class StatusEnum(str, Enum):
    open = 'open'
    closed = 'closed'

# ユーザーのステータススキーマ
class UserStatus(BaseModel):
    user_id: str
    name: str = "unknown"
    status: StatusEnum = StatusEnum.closed
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # モデルが任意のフィールドを持つことを禁止する
        extra = "forbid"
        schema_extra = {
            "example": {
                "user_id": "c9b1b9b5-5e8c-456a-a8f7-23dabaafca9a",
                "name": "John Doe",
                "status": "open",
                "created_at": "2023-09-20T15:03:00Z"
            }
        }

# ユーザーのリストを返すスキーマ
class UserList(BaseModel):
    users: List[UserStatus]

# リクエストボディの定義
class DestinationRequest(BaseModel):
    destination_user_id: str  # フレンドのID

class CancelRequest(BaseModel):
    friend_id: str  # キャンセルする友人のID