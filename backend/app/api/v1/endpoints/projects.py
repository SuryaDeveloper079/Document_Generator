from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from slugify import slugify
from app.db.database import get_db
from app.models.models import Project, Document
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter(prefix="/projects", tags=["Projects"])

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


async def _get_project_or_404(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    base_slug = slugify(f"project-{data.name}")
    slug = base_slug
    count = 1
    while True:
        existing = await db.execute(select(Project).where(Project.slug == slug))
        if not existing.scalar_one_or_none():
            break
        slug = f"{base_slug}-{count}"
        count += 1
    project = Project(
        owner_id=DEFAULT_USER_ID,
        name=data.name,
        slug=slug,
        description=data.description,
        language=data.language,
        visibility=data.visibility,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return {**project.__dict__, "document_count": 0}


@router.get("", response_model=List[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(Project.updated_at.desc()))
    projects = result.scalars().all()
    output = []
    for p in projects:
        count_result = await db.execute(select(func.count()).where(Document.project_id == p.id))
        output.append({**p.__dict__, "document_count": count_result.scalar() or 0})
    return output


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await _get_project_or_404(project_id, db)
    count_result = await db.execute(select(func.count()).where(Document.project_id == project.id))
    return {**project.__dict__, "document_count": count_result.scalar() or 0}


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: str, data: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    project = await _get_project_or_404(project_id, db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    await db.flush()
    count_result = await db.execute(select(func.count()).where(Document.project_id == project.id))
    return {**project.__dict__, "document_count": count_result.scalar() or 0}


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await _get_project_or_404(project_id, db)
    await db.delete(project)
