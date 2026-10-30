# 个人词汇管理 API

## 本地测试

``` bash
# 准备源码
git clone git@github.com:AAA-voc-pifa/voc-api.git
cd ./voc-api

# 启动测试数据库
docker compose -f misc/db/compose.yaml up -d

# 初始化运行环境
uv sync
source .venv/bin/activate

# 设置环境变量
export password='123456'
export MONGODB_URI='mongodb://ppz:123456@127.0.0.1:30001/?authSource=admin'
export MONGODB_DB='my-voc'

# go
fastapi dev
# fastapi run
```
