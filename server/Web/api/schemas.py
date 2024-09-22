from typing import Optional
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
    memo: Optional[str] = "" # memoフィールドを追加し、空文字をデフォルト値に
    address: Optional[str] = ""

    class Config:
        # モデルが任意のフィールドを持つことを禁止する
        extra = "forbid"

# ユーザーのリストを返すスキーマ
class UserList(BaseModel):
    users: List[UserStatus]

# リクエストボディの定義
class DestinationRequest(BaseModel):
    destination_user_id: str  # フレンドのID

class CancelRequest(BaseModel):
    friend_id: str  # キャンセルする友人のID