import os
import json
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account
from server.Web.api.schemas import UserStatus, UserList, StatusEnum
from server.Web.firestore import get_firestore_client

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


# Firestoreのユーザーが存在するかを確認する関数
def check_user_exists(user_id: str, db: firestore.Client):
    # Firestoreのコレクションからユーザードキュメントを取得
    user_doc_ref = db.collection('users').document(str(user_id))
    user_doc = user_doc_ref.get()

    # ユーザーが存在しない場合、404エラーを返す
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    return user_doc

# 全ユーザーのステータスを取得するAPI
@api.get("/users", response_model=UserList)
async def get_all_user_status(db: firestore.Client = Depends(get_firestore_client)):
    users_ref = db.collection("users")  # Firestoreのコレクション参照
    docs = users_ref.stream()  # 全ユーザーのドキュメントをストリームで取得

    # Firestoreから取得したユーザーのリストを構築
    users = []
    for doc in docs:
        data = doc.to_dict()  # Firestoreドキュメントを辞書形式に変換
        user = UserStatus(id=data["id"], status=data["status"])
        users.append(user)

    return UserList(users=users)

# 特定のユーザーのステータスを取得するAPI
@api.get("/users/{user_id}", response_model=UserStatus)
async def get_user_status(user_id: str, db: firestore.Client = Depends(get_firestore_client)):
    user_ref = db.collection("users").document(str(user_id))  # ユーザーIDに基づくドキュメント参照
    user_doc = user_ref.get()

    if user_doc.exists:
        data = user_doc.to_dict()
        return UserStatus(id=data["id"], status=data["status"])
    else:
        raise HTTPException(status_code=404, detail="User not found")

# フレンド登録API（Firestoreバージョン）
@api.post("/users/{user_id}/friends")
async def add_friend(user_id: str, friend_id: str, db: firestore.Client = Depends(get_firestore_client)):
    # Firestoreでユーザーが存在するか確認
    user_doc = check_user_exists(user_id, db)

    # フレンドが存在するかも確認する
    friend_doc = check_user_exists(friend_id, db)

    # Firestoreにフレンドリストを更新（追加）
    user_doc_ref = db.collection('users').document(str(user_id))
    user_doc_ref.update({
        'friends': firestore.ArrayUnion([str(friend_id)])
    })

    return {"message": "Friend added successfully"}

# フレンド取得API
@api.get("/users/{user_id}/friends")
async def get_friends(user_id: str, db: firestore.Client = Depends(get_firestore_client)):
    # ユーザーが存在するか確認
    user_doc = check_user_exists(user_id, db)

    # フレンドリストを取得
    friends = user_doc.to_dict().get('friends', [])

    return {"friends": friends}

# フレンド削除API（Firestore版）
@api.delete("/users/{user_id}/friends/{friend_id}")
async def delete_friend(user_id: str, friend_id: str, db: firestore.Client = Depends(get_firestore_client)):
    # ユーザーとフレンドの存在確認
    user_doc = check_user_exists(user_id, db)
    friend_doc = check_user_exists(friend_id, db)

    # ユーザードキュメントからフレンドリストを取得
    user_data = user_doc.to_dict()
    friends = user_data.get('friends', [])

    # フレンドが存在しない場合
    if str(friend_id) not in friends:
        raise HTTPException(status_code=404, detail="Friend not found")

    # Firestoreでフレンドを削除（ArrayRemoveを使用）
    user_doc_ref = db.collection('users').document(str(user_id))
    user_doc_ref.update({
        'friends': firestore.ArrayRemove([str(friend_id)])
    })

    return {"message": "Friend deleted successfully"}