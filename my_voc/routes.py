from typing import Annotated

from fastapi import APIRouter, Depends, Query

from my_voc import db
from my_voc.auth import require_auth
from my_voc.schemas import (
    CallResult_DeleteVoc,
    CallResult_NewVoc,
    CallResult_Unauthorized,
    CallResult_UpdatePoints,
    CallResult_VocExist,
    CallResult_VocList,
    ErrNewVoc,
    ErrNotFound,
    OkExist,
    OkNull,
    OkVocList,
)
from my_voc.words import Count, Points, Word, public_word

router = APIRouter(
    dependencies=[Depends(require_auth)],
    responses={401: {"model": CallResult_Unauthorized}},
)


@router.post("/voc/{word}", response_model=CallResult_NewVoc)
def add_word(word: Word) -> CallResult_NewVoc:
    if not db.insert_word(word):
        return ErrNewVoc()
    return OkNull()


@router.get("/voc/exist/{word}", response_model=CallResult_VocExist)
def word_exists(word: Word) -> CallResult_VocExist:
    return OkExist(data=db.word_exists(word))


@router.delete("/voc/{word}", response_model=CallResult_DeleteVoc)
def delete_word(word: Word) -> CallResult_DeleteVoc:
    if not db.delete_word(word):
        return ErrNotFound()
    return OkNull()


@router.get("/voc", response_model=CallResult_VocList)
def list_lowest(count: Annotated[Count, Query()]) -> CallResult_VocList:
    return OkVocList(data=[public_word(doc) for doc in db.list_words(count)])


@router.get("/voc/all", response_model=OkVocList)
def list_all() -> OkVocList:
    return OkVocList(data=[public_word(doc) for doc in db.list_words()])


@router.post("/voc/points/{word}", response_model=CallResult_UpdatePoints)
def update_points(word: Word, points: Annotated[Points, Query()]) -> CallResult_UpdatePoints:
    if not db.update_points(word, points):
        return ErrNotFound()
    return OkNull()
