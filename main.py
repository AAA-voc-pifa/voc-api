import json
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from my_voc.auth import AuthError, configure
from my_voc.db import close, connect
from my_voc.routes import router

_REQUIRED_ENV = ("password", "MONGODB_URI", "MONGODB_DB")


class UnicodeJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(content, ensure_ascii=False).encode("utf-8")


def _prepare() -> None:
    missing = [name for name in _REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        print("缺少环境变量: " + ", ".join(missing), file=sys.stderr)
        sys.exit(1)
    configure(os.environ["password"])
    try:
        connect(os.environ["MONGODB_URI"], os.environ["MONGODB_DB"])
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


_prepare()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    close()


def auth_error_handler(_request: Request, _exc: AuthError) -> UnicodeJSONResponse:
    return UnicodeJSONResponse(
        status_code=401,
        content={"ok": False, "error": "未授权"},
    )


app = FastAPI(
    title="个人词汇管理 API",
    version="0.1.0",
    lifespan=lifespan,
    default_response_class=UnicodeJSONResponse,
)
app.add_exception_handler(AuthError, auth_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
