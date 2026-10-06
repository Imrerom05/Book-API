from typing import Optional

from pydantic import BaseModel


# ============================================================
# WORK SCHEMAS
# ============================================================

class WorkResponse(BaseModel):
    """
    Basic information about a work/book.
    """

    work_id: int
    title: str
    description: Optional[str] = None
    original_year: Optional[int] = None
    cover_image_url: Optional[str] = None
    original_language: Optional[str] = None


# ============================================================
# AUTHOR SCHEMAS
# ============================================================

class AuthorResponse(BaseModel):
    """
    Basic information about an author.
    """

    author_id: int
    name: str
    birth: Optional[int] = None
    death: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


# ============================================================
# SERIES SCHEMAS
# ============================================================

class SeriesResponse(BaseModel):
    """
    Basic information about a series.
    """

    series_id: int
    name: str
    description: Optional[str] = None


# ============================================================
# SERIES ↔ WORK SCHEMAS
# ============================================================

class SeriesWorkResponse(BaseModel):
    """
    A series together with the position of a work
    inside that series.
    """

    series_id: int
    name: str
    position: Optional[int] = None


class WorkInSeriesResponse(BaseModel):
    """
    A work together with its position inside a series.
    """

    work_id: int
    title: str
    description: Optional[str] = None
    original_year: Optional[int] = None
    cover_image_url: Optional[str] = None
    original_language: Optional[str] = None
    position: Optional[int] = None


# ============================================================
# FULL WORK SCHEMA
# ============================================================

class FullWorkResponse(BaseModel):
    """
    Complete information about a work, including
    its authors and series.
    """

    work_id: int
    title: str
    description: Optional[str] = None
    original_year: Optional[int] = None
    cover_image_url: Optional[str] = None
    original_language: Optional[str] = None

    authors: list[AuthorResponse]
    series: list[SeriesWorkResponse]


# ============================================================
# FULL AUTHOR SCHEMA
# ============================================================

class FullAuthorResponse(BaseModel):
    """
    Complete information about an author, including
    all works associated with the author.
    """

    author_id: int
    name: str
    birth: Optional[int] = None
    death: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

    works: list[WorkResponse]


# ============================================================
# FULL SERIES SCHEMA
# ============================================================

class FullSeriesResponse(BaseModel):
    """
    Complete information about a series, including
    all works in the series and their positions.
    """

    series_id: int
    name: str
    description: Optional[str] = None

    works: list[WorkInSeriesResponse]


# ============================================================
# SEARCH RESPONSE
# ============================================================

class SearchResponse(BaseModel):
    """
    Combined search response.

    Depending on the requested type, one or more of these
    lists can contain results.
    """

    works: list[WorkResponse]
    authors: list[AuthorResponse]
    series: list[SeriesResponse]