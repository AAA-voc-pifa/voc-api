import hashlib
import hmac
import os
from typing import Annotated

from fastapi import Header


class AuthError(Exception):
    pass


def require_auth(
    authentication: Annotated[
        str | None,
        Header(
            alias="Authentication",
            description="与环境变量 AUTHENTICATION 一致，不加 Bearer",
        ),
    ] = None,
) -> None:
    expected = os.environ.get("AUTHENTICATION")
    if not expected or authentication is None:
        raise AuthError()
    actual = hashlib.sha256(authentication.encode("utf-8")).digest()
    expected_digest = hashlib.sha256(expected.encode("utf-8")).digest()
    if not hmac.compare_digest(actual, expected_digest):
        raise AuthError()
