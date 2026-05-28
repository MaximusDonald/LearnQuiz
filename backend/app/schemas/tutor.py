"""Pydantic schemas for the Tutor AI module."""

from uuid import UUID
from pydantic import BaseModel

class TutorFeedbackResponse(BaseModel):
    """Response returned when the AI tutor provides feedback for a wrong answer."""

    answer_id: UUID
    ai_feedback: str
