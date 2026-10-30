import re
from datetime import datetime, timezone
from typing import Annotated, Any

from pydantic import AfterValidator, Field

_WORD = re.compile(r"^[a-z]+(?:['-][a-z]+)*$")
_MAX_WORD_LENGTH = 64
_MAX_COUNT = 10_000
_INT64_MIN = -9_223_372_036_854_775_808
_INT64_MAX = 9_223_372_036_854_775_807


def normalize_word(raw: str) -> str:
    word = raw.strip().lower()
    if not word or len(word) > _MAX_WORD_LENGTH or _WORD.fullmatch(word) is None:
        raise ValueError("不合法的单词")
    return word


Word = Annotated[str, AfterValidator(normalize_word)]
Points = Annotated[int, Field(ge=_INT64_MIN, le=_INT64_MAX)]
Count = Annotated[int, Field(ge=1, le=_MAX_COUNT)]


def as_utc_iso(value: datetime) -> str:
    # 驱动有时会把 UTC 时间当成无时区 datetime 返回。
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def public_word(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "word": doc["word"],
        "points": int(doc["points"]),
        "add_at": as_utc_iso(doc["add_at"]),
        "update_at": as_utc_iso(doc["update_at"]),
    }
