import asyncio
import ssl
import os

# Fix Upstash - only supports DB 0
_rb = os.environ.get('CELERY_RESULT_BACKEND', '')
if _rb and '/1' in _rb:
    os.environ['CELERY_RESULT_BACKEND'] = _rb.replace('/1', '/0')

from celery import Celery
from celery.utils.log import get_task_logger
from app.core.config import settings

logger = get_task_logger(__name__)

# Force DB 0 on both URLs
broker_url = settings.CELERY_BROKER_URL.replace('/1', '/0')
result_url = settings.CELERY_RESULT_BACKEND.replace('/1', '/0')

celery_app = Celery(
    "ai_doc_generator",
    broker=broker_url,
    backend=result_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,
    broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
    redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
    broker_connection_retry_on_startup=True,
    task_routes={
        "app.tasks.celery_tasks.generate_document_task": {"queue": "documents"},
        "app.tasks.celery_tasks.render_diagram_task": {"queue": "diagrams"},
    },
)


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name="app.tasks.celery_tasks.generate_document_task", max_retries=3, default_retry_delay=30)
def generate_document_task(self, document_id, source_code, doc_type, language, prompt_extras, user_id, generate_diagrams, diagram_types):
    async def _run():
        from app.db.database import AsyncSessionLocal
        from app.models.models import Document, Diagram
        from app.services.claude_service import generate_documentation, generate_diagram_code
        from app.services.storage_service import storage
        from sqlalchemy import update
        async with AsyncSessionLocal() as db:
            try:
                result = await generate_documentation(
                    source_code=source_code,
                    doc_type=doc_type,
                    prompt_extras=prompt_extras,
                    language=language,
                )
                key = storage.document_key(user_id, document_id, "md")
                try:
                    storage.upload_text(result["content"], key)
                    url = storage.get_presigned_url(key, expires=86400 * 7)
                except Exception:
                    url = None
                await db.execute(
                    update(Document).where(Document.id == document_id).values(
                        status="completed",
                        content_markdown=result["content"],
                        file_key=key,
                        file_url=url,
                        model_used=result["model"],
                        tokens_used=result["tokens_total"],
                        generation_time_ms=result["time_ms"],
                    )
                )
                if generate_diagrams and diagram_types:
                    for dtype in diagram_types:
                        try:
                            dr = await generate_diagram_code(description=source_code[:2000], diagram_type=dtype, tool="mermaid")
                            db.add(Diagram(document_id=document_id, title=f"{dtype.title()} Diagram", diagram_type=dtype, tool="mermaid", mermaid_code=dr["code"]))
                        except Exception as e:
                            logger.warning(f"Diagram failed: {e}")
                await db.commit()
                return {"document_id": document_id, "status": "completed"}
            except Exception as exc:
                logger.error(f"Task failed: {exc}")
                try:
                    await db.execute(
                        update(Document).where(Document.id == document_id).values(
                            status="failed", error_message=str(exc)
                        )
                    )
                    await db.commit()
                except Exception:
                    pass
                raise self.retry(exc=exc)
    return run_async(_run())


@celery_app.task(bind=True, name="app.tasks.celery_tasks.render_diagram_task", max_retries=3, default_retry_delay=15)
def render_diagram_task(self, diagram_id, description, diagram_type, tool, document_id):
    async def _run():
        import httpx
        from app.db.database import AsyncSessionLocal
        from app.models.models import Diagram
        from app.services.claude_service import generate_diagram_code
        from app.services.storage_service import storage
        from sqlalchemy import update
        async with AsyncSessionLocal() as db:
            try:
                result = await generate_diagram_code(description, diagram_type, tool)
                svg_url = None
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        resp = await client.post(
                            f"{settings.NODE_SERVICE_URL}/render",
                            json={"code": result["code"], "tool": tool, "type": diagram_type},
                            headers={"X-API-Key": settings.NODE_SERVICE_API_KEY},
                        )
                        resp.raise_for_status()
                        key = storage.diagram_key(document_id, diagram_id, "svg")
                        storage.upload_text(resp.json().get("svg", ""), key, "image/svg+xml")
                        svg_url = storage.get_presigned_url(key, expires=86400 * 7)
                except Exception:
                    pass
                await db.execute(
                    update(Diagram).where(Diagram.id == diagram_id).values(
                        mermaid_code=result["code"] if tool == "mermaid" else None,
                        plantuml_code=result["code"] if tool == "plantuml" else None,
                        svg_url=svg_url,
                    )
                )
                await db.commit()
                return {"diagram_id": diagram_id}
            except Exception as exc:
                raise self.retry(exc=exc)
    return run_async(_run())
