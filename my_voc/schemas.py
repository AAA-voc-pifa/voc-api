from typing import Literal

from pydantic import BaseModel, Field


class VocWord(BaseModel):
    word: str
    points: int = Field(description="整数")
    add_at: str = Field(description="ISO 8601，UTC")
    update_at: str = Field(description="ISO 8601，UTC")


class CallResult_Unauthorized(BaseModel):
    ok: Literal[False]
    error: Literal["未授权"]


class OkNull(BaseModel):
    ok: Literal[True] = True
    data: None = None


class OkExist(BaseModel):
    ok: Literal[True] = True
    data: bool = Field(description="false: 不在; true: 在")


class OkVocList(BaseModel):
    ok: Literal[True] = True
    data: list[VocWord]


class ErrNewVoc(BaseModel):
    ok: Literal[False] = False
    error: Literal["重复添加"] = "重复添加"


class ErrNotFound(BaseModel):
    ok: Literal[False] = False
    error: Literal["单词不存在"] = "单词不存在"


CallResult_NewVoc = OkNull | ErrNewVoc
CallResult_VocExist = OkExist
CallResult_DeleteVoc = OkNull | ErrNotFound
CallResult_VocList = OkVocList
CallResult_UpdatePoints = OkNull | ErrNotFound
