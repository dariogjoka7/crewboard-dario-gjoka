from typing import TypeVar, Generic, Sequence
from pydantic import BaseModel

from backend.routers.models.pagination import PaginationMeta

T = TypeVar("T")


class CommonQueryParams(BaseModel):
    skip: int = 0
    limit: int = 10


class BaseMessageResponse(BaseModel):
    message: str | None = None


class BaseListResponse(BaseModel, Generic[T]):
    data: Sequence[T] = []
    meta: PaginationMeta | None = None
