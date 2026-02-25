from fastapi import Query, Request
from pydantic import BaseModel


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100)
    ):
        self.page = page
        self.limit = limit
        self.skip = (page - 1) * limit


class PaginationLinks(BaseModel):
    first: str
    last: str
    prev: str | None
    next: str | None


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    links: PaginationLinks


def build_pagination(request: Request, page: int, limit: int, total: int) -> PaginationMeta:
    total_pages = max(1, -(-total // limit))  # ceiling division
    base_url = str(request.url.remove_query_params(["page", "limit"]))

    def make_url(p: int) -> str:
        return f"{base_url}?page={p}&limit={limit}"

    return PaginationMeta(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        links=PaginationLinks(
            first=make_url(1),
            last=make_url(total_pages),
            prev=make_url(page - 1) if page > 1 else None,
            next=make_url(page + 1) if page < total_pages else None
        )
    )