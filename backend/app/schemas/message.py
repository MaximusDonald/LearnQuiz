"""Pydantic schemas for course Q&A messages."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CourseMessageCreateRequest(BaseModel):
    """Payload used to ask a new question about a course."""

    question: str = Field(min_length=1, max_length=5000)


class CourseMessageResponse(BaseModel):
    """Serializable course message."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    course_id: UUID
    role: str
    content: str
    created_at: datetime
    updated_at: datetime


class CourseMessageExchangeResponse(BaseModel):
    """Response returned after one user question and one assistant answer."""

    user_message: CourseMessageResponse
    assistant_message: CourseMessageResponse
