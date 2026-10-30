# 个人词汇管理 API

## 本地测试

``` bash
docker compose -f misc/db/compose.yaml up -d

uv sync

source .venv/bin/activate
export password='123456'
export MONGODB_URI='mongodb://ppz:123456@127.0.0.1:30001/?authSource=admin'
export MONGODB_DB='my-voc'
fastapi dev
```
