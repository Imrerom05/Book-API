from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from app.database import engine, get_db
from app.models import Work, Author, AuthorWork, Series, SeriesWork

app = FastAPI(
    title="Book API",
    description="API for books, authors and series",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Book API is running!"
    }


@app.get("/works/search")
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
        .outerjoin(SeriesWork, Work.work_id == SeriesWork.work_id)
        .outerjoin(Series, SeriesWork.series_id == Series.series_id)
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


@app.get("/works/{work_id}")
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


@app.get("/works/{work_id}/authors")
def get_work_authors(
    work_id: int,
    db: Session = Depends(get_db)
):
    authors = (
        db.query(Author)
        .join(AuthorWork, Author.author_id == AuthorWork.author_id)
        .filter(AuthorWork.work_id == work_id)
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


@app.get("/works/{work_id}/series")
def get_work_series(
    work_id: int,
    db: Session = Depends(get_db)
):
    series = (
        db.query(Series)
        .join(SeriesWork, Series.series_id == SeriesWork.series_id)
        .filter(SeriesWork.work_id == work_id)
        .all()
    )

    return [
        {
            "series_id": series.series_id,
            "name": series.name,
            "description": series.description
        }
        for series in series
    ]



@app.get("/works/{work_id}/full")
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
        .join(AuthorWork, Author.author_id == AuthorWork.author_id)
        .filter(AuthorWork.work_id == work_id)
        .all()
    )

    series = (
        db.query(Series, SeriesWork.position)
        .join(SeriesWork, Series.series_id == SeriesWork.series_id)
        .filter(SeriesWork.work_id == work_id)
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


@app.get("/authors/search")
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
        .filter(Author.name.ilike(f"%{query}%"))
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

@app.get("/authors/{author_id}/full")
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
        .join(AuthorWork, Work.work_id == AuthorWork.work_id)
        .filter(AuthorWork.author_id == author_id)
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


@app.get("/authors/{author_id}/works")
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
        .join(AuthorWork, Work.work_id == AuthorWork.work_id)
        .filter(AuthorWork.author_id == author_id)
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



@app.get("/authors/{author_id}")
def get_author(
    author_id: int,
    db: Session = Depends(get_db)
):
    author = db.get(Author, author_id)

    if author is None:
        raise HTTPException(
            status_code=404,
            detail="Author not found"
        )

    return {
        "author_id": author.author_id,
        "name": author.name,
        "birth": author.birth,
        "death": author.death,
        "image_url": author.image_url,
        "description": author.description
    }


@app.get("/series/search")
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
        .filter(Series.name.ilike(f"%{query}%"))
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


@app.get("/series/{series_id}")
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



@app.get("/series/{series_id}/works")
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
        .join(SeriesWork, Work.work_id == SeriesWork.work_id)
        .filter(SeriesWork.series_id == series_id)
        .order_by(SeriesWork.position)
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



@app.get("/series/{series_id}/full")
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
        .join(SeriesWork, Work.work_id == SeriesWork.work_id)
        .filter(SeriesWork.series_id == series_id)
        .order_by(SeriesWork.position)
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


@app.get("/search")
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

    if type is None or type == "works":
        works = (
            db.query(Work)
            .outerjoin(SeriesWork, Work.work_id == SeriesWork.work_id)
            .outerjoin(Series, SeriesWork.series_id == Series.series_id)
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

    if type is None or type == "authors":
        authors = (
            db.query(Author)
            .filter(Author.name.ilike(f"%{search_query}%"))
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

    if type is None or type == "series":
        series_list = (
            db.query(Series)
            .filter(Series.name.ilike(f"%{search_query}%"))
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