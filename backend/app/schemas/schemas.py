from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, model_validator, ConfigDict
import re
from pydantic import Field


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    # password: str
    password: str = Field(min_length=8,max_length=72)
    full_name: Optional[str] = None
    

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]{3,50}$", v):
            raise ValueError("Username must be 3-50 chars: letters, numbers, _ or -")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    plan: str
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "python"
    visibility: str = "private"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    language: str
    visibility: str
    created_at: datetime
    updated_at: datetime
    document_count: int = 0


class DocumentCreate(BaseModel):
    title: str
    doc_type: str = "readme"
    source_code: Optional[str] = None
    source_url: Optional[str] = None
    prompt_extras: Optional[str] = None
    generate_diagrams: bool = False
    diagram_types: List[str] = []

    @model_validator(mode="after")
    def check_source(self) -> "DocumentCreate":
        if not self.source_code and not self.source_url:
            raise ValueError("Either source_code or source_url must be provided")
        return self


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: str
    project_id: str
    title: str
    doc_type: str
    status: str
    content_markdown: Optional[str] = None
    file_url: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: int
    generation_time_ms: int
    task_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    doc_type: str
    status: str
    tokens_used: int
    created_at: datetime


class DiagramCreate(BaseModel):
    title: str
    diagram_type: str = "flowchart"
    tool: str = "mermaid"
    description: str


class DiagramOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    document_id: str
    title: str
    diagram_type: str
    tool: str
    mermaid_code: Optional[str] = None
    svg_url: Optional[str] = None
    created_at: datetime


class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    progress: Optional[int] = None
