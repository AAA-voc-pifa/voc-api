# 个人词汇管理 API

## 本地测试

``` bash
# 准备源码
git clone git@github.com:AAA-voc-pifa/voc-api.git
cd ./voc-api

# 构建 docker image (image 命名为 my-voc)
docker build -t my-voc .
# 设置环境变量
export MONGODB_URI=''
# 启动容器
docker run --rm \
	-p 127.0.0.1:20001:8000 \
  my-voc
```
