from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.database import engine, get_db
from app.models import Work, Author, AuthorWork, Series, SeriesWork

# Import Pydantic schemas
from app.schemas import (
    WorkResponse,
    AuthorResponse,
    SeriesResponse,
    FullWorkResponse,
    FullAuthorResponse,
    FullSeriesResponse,
    WorkInSeriesResponse,
    SearchResponse,
)


app = FastAPI(
    title="Book API",
    description="API for books, authors and series",
    version="0.1.0"
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Book API is running!"
    }


# ============================================================
# WORKS
# ============================================================

@app.get(
    "/works/search",
    response_model=list[WorkResponse],
    summary="Search works",
    description="Search for works by title or series name."
)
def search_works(
    query: str,
    db: Session = Depends(get_db)
):
    query = query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    works = (
        db.query(Work)
        .outerjoin(
            SeriesWork,
            Work.work_id == SeriesWork.work_id
        )
        .outerjoin(
            Series,
            SeriesWork.series_id == Series.series_id
        )
        .filter(
            (Work.title.ilike(f"%{query}%")) |
            (Series.name.ilike(f"%{query}%"))
        )
        .distinct()
        .order_by(Work.title)
        .limit(20)
        .all()
    )

    return [
        {
            "work_id": work.work_id,
            "title": work.title,
            "description": work.description,
            "original_year": work.original_year,
            "cover_image_url": work.cover_image_url,
            "original_language": work.original_language
        }
        for work in works
    ]


@app.get(
    "/works/{work_id}",
    response_model=WorkResponse,
    summary="Get a work",
    description="Get basic information about a specific work."
)
def get_work(
    work_id: int,
    db: Session = Depends(get_db)
):
    work = db.get(Work, work_id)

    if work is None:
        raise HTTPException(
            status_code=404,
            detail="Work not found"
        )

    return {
        "work_id": work.work_id,
        "title": work.title,
        "description": work.description,
        "original_year": work.original_year,
        "cover_image_url": work.cover_image_url,
        "original_language": work.original_language
    }


@app.get(
    "/works/{work_id}/authors",
    response_model=list[AuthorResponse],
    summary="Get work authors",
    description="Get all authors associated with a work."
)
def get_work_authors(
    work_id: int,
    db: Session = Depends(get_db)
):
    authors = (
        db.query(Author)
        .join(
            AuthorWork,
            Author.author_id == AuthorWork.author_id
        )
        .filter(
            AuthorWork.work_id == work_id
        )
        .all()
    )

    return [
        {
            "author_id": author.author_id,
            "name": author.name,
            "birth": author.birth,
            "death": author.death,
            "image_url": author.image_url,
            "description": author.description
        }
        for author in authors
    ]


@app.get(
    "/works/{work_id}/series",
    response_model=list[SeriesResponse],
    summary="Get work series",
    description="Get all series associated with a work."
)
def get_work_series(
    work_id: int,
    db: Session = Depends(get_db)
):
    series = (
        db.query(Series)
        .join(
            SeriesWork,
            Series.series_id == SeriesWork.series_id
        )
        .filter(
            SeriesWork.work_id == work_id
        )
        .all()
    )

    return [
        {
            "series_id": series_item.series_id,
            "name": series_item.name,
            "description": series_item.description
        }
        for series_item in series
    ]


@app.get(
    "/works/{work_id}/full",
    response_model=FullWorkResponse,
    summary="Get full work",
    description="Get a work together with its authors and series."
)
def get_full_work(
    work_id: int,
    db: Session = Depends(get_db)
):
    work = db.get(Work, work_id)

    if work is None:
        raise HTTPException(
            status_code=404,
            detail="Work not found"
        )

    authors = (
        db.query(Author)
        .join(
            AuthorWork,
            Author.author_id == AuthorWork.author_id
        )
        .filter(
            AuthorWork.work_id == work_id
        )
        .all()
    )

    series = (
        db.query(Series, SeriesWork.position)
        .join(
            SeriesWork,
            Series.series_id == SeriesWork.series_id
        )
        .filter(
            SeriesWork.work_id == work_id
        )
        .all()
    )

    return {
        "work_id": work.work_id,
        "title": work.title,
        "description": work.description,
        "original_year": work.original_year,
        "cover_image_url": work.cover_image_url,
        "original_language": work.original_language,

        "authors": [
            {
                "author_id": author.author_id,
                "name": author.name,
                "birth": author.birth,
                "death": author.death,
                "image_url": author.image_url,
                "description": author.description
            }
            for author in authors
        ],

        "series": [
            {
                "series_id": item[0].series_id,
                "name": item[0].name,
                "position": item[1]
            }
            for item in series
        ]
    }


# ============================================================
# AUTHORS
# ============================================================

@app.get(
    "/authors/search",
    response_model=list[AuthorResponse],
    summary="Search authors",
    description="Search for authors by name."
)
def search_authors(
    query: str,
    db: Session = Depends(get_db)
):
    query = query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    authors = (
        db.query(Author)
        .filter(
            Author.name.ilike(f"%{query}%")
        )
        .order_by(Author.name)
        .limit(20)
        .all()
    )

    return [
        {
            "author_id": author.author_id,
            "name": author.name,
            "birth": author.birth,
            "death": author.death,
            "image_url": author.image_url,
            "description": author.description
        }
        for author in authors
    ]


@app.get(
    "/authors/{author_id}/full",
    response_model=FullAuthorResponse,
    summary="Get full author",
    description="Get an author together with all of their works."
)
def get_full_author(
    author_id: int,
    db: Session = Depends(get_db)
):
    author = db.get(Author, author_id)

    if author is None:
        raise HTTPException(
            status_code=404,
            detail="Author not found"
        )

    works = (
        db.query(Work)
        .join(
            AuthorWork,
            Work.work_id == AuthorWork.work_id
        )
        .filter(
            AuthorWork.author_id == author_id
        )
        .order_by(Work.title)
        .all()
    )

    return {
        "author_id": author.author_id,
        "name": author.name,
        "birth": author.birth,
        "death": author.death,
        "image_url": author.image_url,
        "description": author.description,

        "works": [
            {
                "work_id": work.work_id,
                "title": work.title,
                "description": work.description,
                "original_year": work.original_year,
                "cover_image_url": work.cover_image_url,
                "original_language": work.original_language
            }
            for work in works
        ]
    }


@app.get(
    "/authors/{author_id}/works",
    response_model=list[WorkResponse],
    summary="Get author's works",
    description="Get all works associated with an author."
)
def get_author_works(
    author_id: int,
    db: Session = Depends(get_db)
):
    author = db.get(Author, author_id)

    if author is None:
        raise HTTPException(
            status_code=404,
            detail="Author not found"
        )

    works = (
        db.query(Work)
        .join(
            AuthorWork,
            Work.work_id == AuthorWork.work_id
        )
        .filter(
            AuthorWork.author_id == author_id
        )
        .order_by(Work.title)
        .all()
    )

    return [
        {
            "work_id": work.work_id,
            "title": work.title,
            "description": work.description,
            "original_year": work.original_year,
            "cover_image_url": work.cover_image_url,
            "original_language": work.original_language
        }
        for work in works
    ]


# ============================================================
# SERIES
# ============================================================

@app.get(
    "/series/search",
    response_model=list[SeriesResponse],
    summary="Search series",
    description="Search for series by name."
)
def search_series(
    query: str,
    db: Session = Depends(get_db)
):
    query = query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    series_list = (
        db.query(Series)
        .filter(
            Series.name.ilike(f"%{query}%")
        )
        .order_by(Series.name)
        .limit(20)
        .all()
    )

    return [
        {
            "series_id": item.series_id,
            "name": item.name,
            "description": item.description
        }
        for item in series_list
    ]


@app.get(
    "/series/{series_id}",
    response_model=SeriesResponse,
    summary="Get a series",
    description="Get basic information about a specific series."
)
def get_series(
    series_id: int,
    db: Session = Depends(get_db)
):
    item = db.get(Series, series_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Series not found"
        )

    return {
        "series_id": item.series_id,
        "name": item.name,
        "description": item.description
    }


@app.get(
    "/series/{series_id}/works",
    response_model=list[WorkInSeriesResponse],
    summary="Get series works",
    description="Get all works in a series ordered by their position."
)
def get_series_works(
    series_id: int,
    db: Session = Depends(get_db)
):
    item = db.get(Series, series_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Series not found"
        )

    works = (
        db.query(Work, SeriesWork.position)
        .join(
            SeriesWork,
            Work.work_id == SeriesWork.work_id
        )
        .filter(
            SeriesWork.series_id == series_id
        )
        .order_by(
            SeriesWork.position
        )
        .all()
    )

    return [
        {
            "work_id": work.work_id,
            "title": work.title,
            "description": work.description,
            "original_year": work.original_year,
            "cover_image_url": work.cover_image_url,
            "original_language": work.original_language,
            "position": position
        }
        for work, position in works
    ]


@app.get(
    "/series/{series_id}/full",
    response_model=FullSeriesResponse,
    summary="Get full series",
    description="Get a series together with all works in the series."
)
def get_full_series(
    series_id: int,
    db: Session = Depends(get_db)
):
    item = db.get(Series, series_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Series not found"
        )

    works = (
        db.query(Work, SeriesWork.position)
        .join(
            SeriesWork,
            Work.work_id == SeriesWork.work_id
        )
        .filter(
            SeriesWork.series_id == series_id
        )
        .order_by(
            SeriesWork.position
        )
        .all()
    )

    return {
        "series_id": item.series_id,
        "name": item.name,
        "description": item.description,

        "works": [
            {
                "work_id": work.work_id,
                "title": work.title,
                "original_year": work.original_year,
                "cover_image_url": work.cover_image_url,
                "position": position
            }
            for work, position in works
        ]
    }


# ============================================================
# GLOBAL SEARCH
# ============================================================

@app.get(
    "/search",
    response_model=SearchResponse,
    summary="Search everything",
    description=(
        "Search across works, authors and series. "
        "Optionally specify a type: works, authors or series."
    )
)
def search_all(
    query: str,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    search_query = query.strip()

    if not search_query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    if type is not None:
        type = type.strip().lower()

        if type not in ["works", "authors", "series"]:
            raise HTTPException(
                status_code=400,
                detail="Type must be works, authors, or series"
            )

    results = {
        "works": [],
        "authors": [],
        "series": []
    }

    # --------------------------------------------------------
    # WORKS
    # --------------------------------------------------------

    if type is None or type == "works":
        works = (
            db.query(Work)
            .outerjoin(
                SeriesWork,
                Work.work_id == SeriesWork.work_id
            )
            .outerjoin(
                Series,
                SeriesWork.series_id == Series.series_id
            )
            .filter(
                (Work.title.ilike(f"%{search_query}%")) |
                (Series.name.ilike(f"%{search_query}%"))
            )
            .distinct()
            .order_by(Work.title)
            .limit(20)
            .all()
        )

        results["works"] = [
            {
                "work_id": work.work_id,
                "title": work.title,
                "description": work.description,
                "original_year": work.original_year,
                "cover_image_url": work.cover_image_url,
                "original_language": work.original_language
            }
            for work in works
        ]

    # --------------------------------------------------------
    # AUTHORS
    # --------------------------------------------------------

    if type is None or type == "authors":
        authors = (
            db.query(Author)
            .filter(
                Author.name.ilike(f"%{search_query}%")
            )
            .order_by(Author.name)
            .limit(20)
            .all()
        )

        results["authors"] = [
            {
                "author_id": author.author_id,
                "name": author.name,
                "birth": author.birth,
                "death": author.death,
                "image_url": author.image_url,
                "description": author.description
            }
            for author in authors
        ]

    # --------------------------------------------------------
    # SERIES
    # --------------------------------------------------------

    if type is None or type == "series":
        series_list = (
            db.query(Series)
            .filter(
                Series.name.ilike(f"%{search_query}%")
            )
            .order_by(Series.name)
            .limit(20)
            .all()
        )

        results["series"] = [
            {
                "series_id": series.series_id,
                "name": series.name,
                "description": series.description
            }
            for series in series_list
        ]

    return results