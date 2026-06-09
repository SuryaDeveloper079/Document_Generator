from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import User, Document, Diagram
from app.schemas.schemas import DiagramCreate, DiagramOut
from app.services.user_service import get_current_user
from app.tasks.celery_tasks import render_diagram_task

router = APIRouter(prefix="/documents/{doc_id}/diagrams", tags=["Diagrams"])


@router.post("", response_model=DiagramOut, status_code=status.HTTP_202_ACCEPTED)
async def create_diagram(doc_id: str, data: DiagramCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")
    diagram = Diagram(document_id=doc_id, title=data.title, diagram_type=data.diagram_type, tool=data.tool)
    db.add(diagram)
    await db.flush()
    await db.refresh(diagram)
    render_diagram_task.delay(diagram_id=diagram.id, description=data.description, diagram_type=data.diagram_type, tool=data.tool, document_id=doc_id)
    return diagram


@router.get("", response_model=List[DiagramOut])
async def list_diagrams(doc_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Diagram).where(Diagram.document_id == doc_id))
    return result.scalars().all()


@router.delete("/{diagram_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diagram(doc_id: str, diagram_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Diagram).where(Diagram.id == diagram_id, Diagram.document_id == doc_id))
    diagram = result.scalar_one_or_none()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    await db.delete(diagram)
