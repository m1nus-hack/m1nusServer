# GCPへのデプロイ方法
```sh
# マルチアーキテクチャイメージのビルド
docker buildx build --platform linux/amd64,linux/arm64 -t gcr.io/m1nus-server/m1nus-server --push .

# Cloud Runにdocker imageを再デプロイ
gcloud run deploy m1nus-server \
    --image gcr.io/m1nus-server/m1nus-server \
    --platform managed \
    --region asia-northeast1 \
    --allow-unauthenticated
```