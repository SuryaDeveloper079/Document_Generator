import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    plan: Mapped[str] = mapped_column(String(20), default="free")
    ai_calls_today: Mapped[int] = mapped_column(Integer, default=0)
    ai_calls_reset_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(50), default="python")
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), default="readme")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    source_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_file_key: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    prompt_extras: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_key: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    generation_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    task_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    project: Mapped["Project"] = relationship("Project", back_populates="documents")
    diagrams: Mapped[List["Diagram"]] = relationship("Diagram", back_populates="document", cascade="all, delete-orphan")


class Diagram(Base):
    __tablename__ = "diagrams"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    diagram_type: Mapped[str] = mapped_column(String(50), default="flowchart")
    tool: Mapped[str] = mapped_column(String(20), default="mermaid")
    mermaid_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plantuml_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    svg_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    png_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    document: Mapped["Document"] = relationship("Document", back_populates="diagrams")
