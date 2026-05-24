"""Pydantic schemas for quiz responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QuestionResponse(BaseModel):
    """Serializable quiz question."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    question_type: str
    options: list[str] | None
    correct_answer: str
    explanation: str | None
    order_index: int
    created_at: datetime
    updated_at: datetime


class QuizResponse(BaseModel):
    """Serializable quiz with its questions."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None
    difficulty: str
    created_at: datetime
    updated_at: datetime
    questions: list[QuestionResponse]


class SummaryResponse(BaseModel):
    """Course summary response payload."""

    course_id: UUID
    summary: str | None


class GenerationResponse(BaseModel):
    """Response returned after summary and quiz generation."""

    summary: str
    quiz: QuizResponse
