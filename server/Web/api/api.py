from fastapi import APIRouter, Depends, HTTPException
from google.cloud import firestore
from server.Web.api.schemas import UserStatus, UserList, DestinationRequest, CancelRequest
from server.Web.firestore import get_firestore_client
from datetime import datetime

# FastAPIのルーターを作成
api = APIRouter()

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

        # 存在しないカラムにはデフォルト値を指定
        user_id = doc.id  # ドキュメントのIDを取得
        name = data.get("name", "Unknown")  # nameが存在しない場合は"Unknown"を使用
        status = data.get("status", "closed")  # statusが存在しない場合は"closed"を使用
        # "close"という不正な値がある場合は"closed"に置き換える
        if status == "close":
            status = "closed"

        created_at = data.get("created_at", datetime.utcnow())  # created_atがない場合のデフォルト

        # memoフィールドを取得、存在しない場合や空の場合には空文字を使用
        memo = data.get("memo", "")  # デフォルトで空文字を設定
        # "address"が存在しない場合のデフォルト
        address = data.get("address", "")  # addressフィールドを取得、存在しない場合には空文字を設定

        # Pydanticモデルに渡す
        user = UserStatus(user_id=user_id, name=name, status=status, created_at=created_at, memo=memo, address=address)
        users.append(user)

    return UserList(users=users)

# 特定のユーザーのステータスを取得するAPI
@api.get("/users/{user_id}", response_model=UserStatus)
async def get_user_status(user_id: str, db: firestore.Client = Depends(get_firestore_client)):
    user_ref = db.collection("users").document(str(user_id))  # ユーザーIDに基づくドキュメント参照
    user_doc = user_ref.get()

    if user_doc.exists:
        data = user_doc.to_dict()

        # ドキュメントIDを取得
        user_id = user_doc.id

        # "name"が存在しない場合のデフォルト
        name = data.get("name", "Unknown")

        # "status"が不正な値を持つ場合のクリーニング
        status = data.get("status", "closed")
        if status == "close":  # "close" を "closed" に変換
            status = "closed"

        # "created_at"が存在しない場合のデフォルト
        created_at = data.get("created_at", datetime.utcnow())

        # "memo"が存在しない場合のデフォルト
        memo = data.get("memo", "")  # memoフィールドを取得、存在しない場合には空文字を設定

        # "address"が存在しない場合のデフォルト
        address = data.get("address", "")  # addressフィールドを取得、存在しない場合には空文字を設定

        # UserStatusモデルにデータを渡す
        return UserStatus(user_id=user_id, name=name, status=status, created_at=created_at, memo=memo, address=address)
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

# ユーザーがフレンドに「いく！」を押すエンドポイント
@api.post("/users/{user_id}/destination")
async def go_to_friend(user_id: str, request: DestinationRequest, db: firestore.Client = Depends(get_firestore_client)):
    user_ref = db.collection('users').document(user_id)

    # Firestoreでユーザーのドキュメントを更新
    try:
        user_ref.update({
            "destination_user_id": request.destination_user_id  # 行き先のフレンドIDを設定
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # フレンドのcomming_friendsに追加
    friend_ref = db.collection('users').document(request.destination_user_id)
    try:
        friend_ref.update({
            "comming_friends": firestore.ArrayUnion([user_id])  # フレンドのリストに自分を追加
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Destination and comming friends updated successfully"}

# ユーザーが「[いく！]ボタンキャンセル」を押すエンドポイント
@api.patch("/users/{user_id}/cancel")
async def cancel_trip(user_id: str, request: CancelRequest, db: firestore.Client = Depends(get_firestore_client)):
    user_ref = db.collection('users').document(user_id)

    # 自分のdestinationをクリア
    try:
        user_ref.update({
            "destination_user_id": firestore.DELETE_FIELD  # 行き先を削除
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # フレンドのcomming_friendsリストから自分を削除
    friend_ref = db.collection('users').document(request.friend_id)
    try:
        friend_ref.update({
            "comming_friends": firestore.ArrayRemove([user_id])  # フレンドのリストから自分を削除
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Trip cancelled successfully"}