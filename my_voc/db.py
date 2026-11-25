from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import ASCENDING, ReturnDocument, MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConfigurationError, DuplicateKeyError

mongo: MongoClient | None = None
words: Collection | None = None


def connect(uri: str) -> None:
    global mongo, words
    client = MongoClient(
        uri,
        tz_aware=True,
        tzinfo=timezone.utc,
        serverSelectionTimeoutMS=3000,
    )
    try:
        client.admin.command("ping")
        database = client.get_default_database()
    except ConfigurationError as exc:
        client.close()
        raise RuntimeError("MONGODB_URI 里需要包含数据库名") from exc
    except Exception as exc:
        client.close()
        raise RuntimeError("无法连接 MongoDB") from exc
    mongo = client
    words = database["words"]
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


def update_points(word: str, points: int) -> dict[str, Any] | None:
    """Apply delta and return the updated word doc, or None if missing."""
    if points == 0:
        return get_word(word)
    return _collection().find_one_and_update(
        {"word": word},
        {"$inc": {"points": points}, "$set": {"update_at": datetime.now(timezone.utc)}},
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER,
    )


def list_words(
    limit: int | None = None,
    exclude: list[str] | None = None,
    idle_seconds: int | None = None,
) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if exclude:
        query["word"] = {"$nin": exclude}
    if idle_seconds is not None:
        query["update_at"] = {
            "$lt": datetime.now(timezone.utc) - timedelta(seconds=idle_seconds)
        }
    cursor = _collection().find(query, {"_id": 0}).sort(
        [("points", ASCENDING), ("update_at", ASCENDING)]
    )
    if limit is not None:
        cursor = cursor.limit(limit)
    return list(cursor)


def list_words_and_add_points(
    limit: int,
    delta: int,
    exclude: list[str] | None = None,
    idle_seconds: int | None = None,
) -> list[dict[str, Any]]:
    docs = list_words(limit, exclude=exclude, idle_seconds=idle_seconds)
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
