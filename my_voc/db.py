from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

mongo: MongoClient | None = None
words: Collection | None = None


def connect(uri: str, db_name: str) -> None:
    global mongo, words
    client = MongoClient(
        uri,
        tz_aware=True,
        tzinfo=timezone.utc,
        serverSelectionTimeoutMS=3000,
    )
    try:
        client.admin.command("ping")
    except Exception as exc:
        client.close()
        raise RuntimeError("无法连接 MongoDB") from exc
    mongo = client
    words = client[db_name]["words"]
    words.create_index("word", unique=True, name="word_unique")


def close() -> None:
    if mongo is not None:
        mongo.close()


def _collection() -> Collection:
    if words is None:
        raise RuntimeError("数据库还没连接")
    return words


def insert_word(word: str) -> bool:
    collection = _collection()
    if collection.find_one({"word": word}, {"_id": 1}) is not None:
        return False
    now = datetime.now(timezone.utc)
    try:
        collection.insert_one(
            {"word": word, "points": 0, "add_at": now, "update_at": now}
        )
    except DuplicateKeyError:
        return False
    return True


def word_exists(word: str) -> bool:
    return _collection().find_one({"word": word}, {"_id": 1}) is not None


def delete_word(word: str) -> bool:
    result = _collection().delete_one({"word": word})
    return result.deleted_count != 0


def get_word(word: str) -> dict[str, Any] | None:
    return _collection().find_one({"word": word}, {"_id": 0})


def update_points(word: str, points: int) -> bool:
    if points == 0:
        return get_word(word) is not None
    result = _collection().update_one(
        {"word": word},
        {"$inc": {"points": points}, "$set": {"update_at": datetime.now(timezone.utc)}},
    )
    return result.matched_count != 0


def list_words(
    limit: int | None = None,
    exclude: list[str] | None = None,
) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if exclude:
        query["word"] = {"$nin": exclude}
    cursor = _collection().find(query, {"_id": 0}).sort(
        [("points", ASCENDING), ("add_at", ASCENDING)]
    )
    if limit is not None:
        cursor = cursor.limit(limit)
    return list(cursor)


def list_words_and_add_points(
    limit: int,
    delta: int,
    exclude: list[str] | None = None,
) -> list[dict[str, Any]]:
    docs = list_words(limit, exclude=exclude)
    if not docs or delta == 0:
        return docs
    now = datetime.now(timezone.utc)
    _collection().update_many(
        {"word": {"$in": [doc["word"] for doc in docs]}},
        {"$inc": {"points": delta}, "$set": {"update_at": now}},
    )
    for doc in docs:
        doc["points"] = int(doc["points"]) + delta
        doc["update_at"] = now
    return docs
