"""Pydantic schemas for course management endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CourseResponse(BaseModel):
    """Serializable course payload returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    file_name: str | None
    file_type: str | None
    raw_text: str
    summary: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class CourseListItemResponse(BaseModel):
    """Lightweight course payload for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    file_name: str | None
    file_type: str | None
    status: str
    created_at: datetime
    updated_at: datetime
