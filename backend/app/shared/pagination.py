"""
Utilidad de paginación genérica para queries SQLAlchemy.
"""

from pydantic import BaseModel, Field
from sqlalchemy.orm import Query


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int

    model_config = {"from_attributes": True}


def paginate(query: Query, params: PaginationParams) -> dict:
    """Aplica LIMIT/OFFSET a una query y retorna metadatos de paginación."""
    total = query.count()
    pages = max(1, (total + params.size - 1) // params.size)
    items = query.offset((params.page - 1) * params.size).limit(params.size).all()
    return {
        "items": items,
        "total": total,
        "page": params.page,
        "size": params.size,
        "pages": pages,
    }
