from google.cloud import firestore

# Firestoreクライアントを初期化
def get_firestore_client():
    return firestore.Client()
