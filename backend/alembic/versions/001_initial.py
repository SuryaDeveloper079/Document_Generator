"""Initial migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(200), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_superuser", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("plan", sa.String(20), server_default="free", nullable=False),
        sa.Column("ai_calls_today", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ai_calls_reset_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table("refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("token", sa.String(500), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("projects",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(220), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("language", sa.String(50), server_default="python", nullable=False),
        sa.Column("visibility", sa.String(20), server_default="private", nullable=False),
        sa.Column("settings", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table("documents",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("doc_type", sa.String(50), server_default="readme", nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("source_code", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("source_file_key", sa.String(300), nullable=True),
        sa.Column("prompt_extras", sa.Text(), nullable=True),
        sa.Column("content_markdown", sa.Text(), nullable=True),
        sa.Column("content_html", sa.Text(), nullable=True),
        sa.Column("file_key", sa.String(300), nullable=True),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("tokens_used", sa.Integer(), server_default="0", nullable=False),
        sa.Column("generation_time_ms", sa.Integer(), server_default="0", nullable=False),
        sa.Column("task_id", sa.String(200), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("diagrams",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("diagram_type", sa.String(50), server_default="flowchart", nullable=False),
        sa.Column("tool", sa.String(20), server_default="mermaid", nullable=False),
        sa.Column("mermaid_code", sa.Text(), nullable=True),
        sa.Column("plantuml_code", sa.Text(), nullable=True),
        sa.Column("svg_url", sa.String(500), nullable=True),
        sa.Column("png_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("diagrams")
    op.drop_table("documents")
    op.drop_table("projects")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
