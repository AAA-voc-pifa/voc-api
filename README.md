# 个人词汇管理 API

接口需请求头 `Authentication`，值与环境变量 `AUTHENTICATION` 一致。
就绪检查：`GET /ready`（无需鉴权）。

## DEV

```sh
uv sync
source .venv/bin/activate
export AUTHENTICATION=123456
export MONGODB_URI='mongodb://127.0.0.1:27017/my-voc'
fastapi dev
```

API 文档: 浏览器打开 http://127.0.0.1:20001/docs

## Deploy with docker
```sh
docker build -t my-voc .
docker run --rm \
	-p 127.0.0.1:20001:80 \
	-e MONGODB_URI='' \
	-e AUTHENTICATION=123456 \
	my-voc
```
