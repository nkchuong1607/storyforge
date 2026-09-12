"""Pagination helpers."""

import math
from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationMeta


@dataclass(frozen=True)
class PageParams:
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def clamp_page_params(page: int, page_size: int, *, max_page_size: int = 100) -> PageParams:
    safe_page = max(page, 1)
    safe_size = min(max(page_size, 1), max_page_size)
    return PageParams(page=safe_page, page_size=safe_size)


def build_pagination(page: int, page_size: int, total_items: int) -> PaginationMeta:
    total_pages = math.ceil(total_items / page_size) if total_items else 0
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )


def paginated(items: list[T], page: int, page_size: int, total_items: int) -> PaginatedResponse[T]:
    return PaginatedResponse(
        items=items,
        pagination=build_pagination(page, page_size, total_items),
    )
