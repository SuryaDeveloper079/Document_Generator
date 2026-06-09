from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import Project, Document
from app.schemas.schemas import DocumentCreate, DocumentOut, DocumentListItem, TaskStatus
from app.services.storage_service import storage
from app.tasks.celery_tasks import generate_document_task
from celery.result import AsyncResult

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["Documents"])

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


async def _get_project_or_404(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _get_document_or_404(doc_id: str, project_id: str, db: AsyncSession) -> Document:
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.project_id == project_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("", response_model=DocumentOut, status_code=status.HTTP_202_ACCEPTED)
async def create_document(project_id: str, data: DocumentCreate, db: AsyncSession = Depends(get_db)):
    project = await _get_project_or_404(project_id, db)
    source_code = data.source_code or ""
    if data.source_url and not data.source_code:
        import httpx
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(str(data.source_url))
                resp.raise_for_status()
                source_code = resp.text[:100000]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")
    doc = Document(
        project_id=project_id,
        title=data.title,
        doc_type=data.doc_type,
        status="pending",
        source_code=source_code[:10000],
        source_url=str(data.source_url) if data.source_url else None,
        prompt_extras=data.prompt_extras,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    task = generate_document_task.delay(
        document_id=doc.id,
        source_code=source_code,
        doc_type=data.doc_type,
        language=project.language,
        prompt_extras=data.prompt_extras or "",
        user_id=DEFAULT_USER_ID,
        generate_diagrams=data.generate_diagrams,
        diagram_types=data.diagram_types,
    )
    doc.task_id = task.id
    return doc


@router.get("", response_model=List[DocumentListItem])
async def list_documents(project_id: str, db: AsyncSession = Depends(get_db)):
    await _get_project_or_404(project_id, db)
    result = await db.execute(select(Document).where(Document.project_id == project_id).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(project_id: str, doc_id: str, db: AsyncSession = Depends(get_db)):
    await _get_project_or_404(project_id, db)
    return await _get_document_or_404(doc_id, project_id, db)


@router.get("/{doc_id}/task-status", response_model=TaskStatus)
async def get_task_status(project_id: str, doc_id: str, db: AsyncSession = Depends(get_db)):
    await _get_project_or_404(project_id, db)
    doc = await _get_document_or_404(doc_id, project_id, db)
    if not doc.task_id:
        return TaskStatus(task_id="none", status=doc.status.upper())
    result = AsyncResult(doc.task_id)
    info = result.info or {}
    progress = info.get("progress") if isinstance(info, dict) else None
    return TaskStatus(
        task_id=doc.task_id,
        status=result.status,
        result=result.result if result.successful() else None,
        error=str(result.info) if result.failed() else None,
        progress=progress,
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(project_id: str, doc_id: str, db: AsyncSession = Depends(get_db)):
    await _get_project_or_404(project_id, db)
    doc = await _get_document_or_404(doc_id, project_id, db)
    if doc.file_key:
        storage.delete(doc.file_key)
    await db.delete(doc)
