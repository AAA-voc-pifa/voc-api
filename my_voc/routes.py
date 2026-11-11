from typing import Annotated

from fastapi import APIRouter, Depends, Query

from my_voc import db
from my_voc.auth import require_auth
from my_voc.schemas import (
    CallResult_DeleteVoc,
    CallResult_NewVoc,
    CallResult_Unauthorized,
    CallResult_UpdatePoints,
    CallResult_VocDetail,
    CallResult_VocExist,
    CallResult_VocList,
    ErrNewVoc,
    ErrNotFound,
    OkExist,
    OkNull,
    OkVoc,
    OkVocList,
)
from my_voc.words import Count, Points, Word, public_word

router = APIRouter(
    dependencies=[Depends(require_auth)],
    responses={401: {"model": CallResult_Unauthorized, "description": "口令错误或缺失"}},
)


@router.get("/auth", response_model=OkNull, summary="验证口令")
def auth() -> OkNull:
    return OkNull()


@router.post("/voc/{word}", response_model=CallResult_NewVoc, summary="添加单词")
def add_word(word: Word) -> CallResult_NewVoc:
    if not db.insert_word(word):
        return ErrNewVoc()
    return OkNull()


@router.get("/voc/exist/{word}", response_model=CallResult_VocExist, summary="单词是否在词表中")
def word_exists(word: Word) -> CallResult_VocExist:
    return OkExist(data=db.word_exists(word))


@router.get("/voc/detail/{word}", response_model=CallResult_VocDetail, summary="单词详情")
def word_detail(word: Word) -> CallResult_VocDetail:
    doc = db.get_word(word)
    if doc is None:
        return ErrNotFound()
    return OkVoc(data=public_word(doc))


@router.delete("/voc/{word}", response_model=CallResult_DeleteVoc, summary="删除单词")
def delete_word(word: Word) -> CallResult_DeleteVoc:
    if not db.delete_word(word):
        return ErrNotFound()
    return OkNull()


@router.get(
    "/voc",
    response_model=CallResult_VocList,
    summary="取出分数最低的单词并加上 points；同分时早加入的优先",
)
def list_lowest(
    count: Annotated[Count, Query(description="取出多少个")],
    points: Annotated[Points, Query(description="给取出的单词加上的分数，可为负数")],
) -> CallResult_VocList:
    return OkVocList(
        data=[public_word(doc) for doc in db.list_words_and_add_points(count, points)]
    )


@router.get("/voc/all", response_model=OkVocList, summary="全部单词")
def list_all() -> OkVocList:
    return OkVocList(data=[public_word(doc) for doc in db.list_words()])


@router.post(
    "/voc/points/{word}",
    response_model=CallResult_UpdatePoints,
    summary="给单词加上指定分数",
)
def update_points(
    word: Word,
    points: Annotated[Points, Query(description="加上的分数，可为负数")],
) -> CallResult_UpdatePoints:
    if not db.update_points(word, points):
        return ErrNotFound()
    return OkNull()
