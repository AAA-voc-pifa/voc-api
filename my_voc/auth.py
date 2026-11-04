import hashlib
import hmac
from typing import Annotated

from fastapi import Header

password = ""


def configure(value: str) -> None:
    global password
    password = value


class AuthError(Exception):
    pass


def require_auth(
    authentication: Annotated[
        str | None,
        Header(alias="Authentication", description="与环境变量 password 一致，不加 Bearer"),
    ] = None,
) -> None:
    if not password or authentication is None:
        raise AuthError()
    actual = hashlib.sha256(authentication.encode("utf-8")).digest()
    expected = hashlib.sha256(password.encode("utf-8")).digest()
    if not hmac.compare_digest(actual, expected):
        raise AuthError()
