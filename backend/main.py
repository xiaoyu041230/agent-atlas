import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from sqlalchemy import create_engine, String, Text, select, func, or_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from backend.importer import load_snapshot

class Base(DeclarativeBase):
    pass

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(500))
    industry: Mapped[str] = mapped_column(String(200), index=True)
    framework: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1000), unique=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./atlas.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

def sync_projects():
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        existing = {p.url: p for p in session.scalars(select(Project))}
        for item in load_snapshot():
            if item["url"] in existing:
                for key, value in item.items():
                    setattr(existing[item["url"]], key, value)
            else:
                session.add(Project(**item))
        session.commit()

@asynccontextmanager
async def lifespan(app):
    sync_projects()
    yield

app = FastAPI(title="Agent Atlas API", lifespan=lifespan)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/facets")
def facets():
    with Session(engine) as session:
        return {key: list(session.scalars(select(getattr(Project, key)).distinct().order_by(getattr(Project, key)))) for key in ("industry", "framework")}

@app.get("/api/projects")
def projects(q: str = Query("", max_length=200), industry: str = "", framework: str = "", page: int = Query(1, ge=1), page_size: int = Query(12, ge=1, le=60), sort: str = Query("name", pattern="^(name|newest)$")):
    stmt = select(Project)
    if q.strip():
        stmt = stmt.where(or_(Project.name.icontains(q.strip(), autoescape=True), Project.description.icontains(q.strip(), autoescape=True)))
    if industry:
        stmt = stmt.where(Project.industry == industry)
    if framework:
        stmt = stmt.where(Project.framework == framework)
    with Session(engine) as session:
        total = session.scalar(select(func.count()).select_from(stmt.subquery()))
        order = (Project.name.asc(), Project.id.asc()) if sort == "name" else (Project.id.desc(),)
        rows = session.scalars(stmt.order_by(*order).offset((page-1)*page_size).limit(page_size))
        return {"items": [{key: getattr(p, key) for key in ("id", "name", "description", "industry", "framework", "url")} for p in rows], "total": total, "page": page, "page_size": page_size}


# Registered last so API routes take precedence over static asset routing.
from pathlib import Path
from fastapi.staticfiles import StaticFiles
frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
