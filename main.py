import json
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from my_voc.db import close, connect
from my_voc.routes import router


class UnicodeJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(content, ensure_ascii=False).encode("utf-8")


def _prepare() -> None:
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        print("缺少环境变量: MONGODB_URI", file=sys.stderr)
        sys.exit(1)
    try:
        connect(uri)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


_prepare()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    close()


app = FastAPI(
    title="个人词汇管理 API",
    version="0.1.0",
    description="本机基础服务，无鉴权。业务失败看 body 的 `ok`；参数不合法返回 422。",
    lifespan=lifespan,
    default_response_class=UnicodeJSONResponse,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
