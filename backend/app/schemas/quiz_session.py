"""Pydantic schemas for quiz session creation, answers, and results."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class QuizSessionCreateRequest(BaseModel):
    """Payload used to create a quiz session."""

    quiz_id: UUID


class SessionQuestionResponse(BaseModel):
    """Serializable quiz question shown to the learner."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    question_type: str
    options: list[str] | None
    order_index: int


class QuizSessionCreateResponse(BaseModel):
    """Response returned when a quiz session starts."""

    session_id: UUID
    quiz_id: UUID
    questions: list[SessionQuestionResponse]


class SubmitAnswerRequest(BaseModel):
    """Payload used to submit one answer for a session question."""

    question_id: UUID
    user_answer: str = Field(min_length=1)


class SubmitAnswerResponse(BaseModel):
    """Evaluation result for one submitted answer."""

    answer_id: UUID
    question_id: UUID
    is_correct: bool
    correct_answer: str
    explanation: str | None
    ai_feedback: str | None


class CompleteQuizSessionResponse(BaseModel):
    """Response returned when finalizing a session."""

    session_id: UUID
    score: float
    total_questions: int
    correct_answers: int


class ResultAnswerResponse(BaseModel):
    """Detailed answer payload shown in the results page."""

    question_id: UUID
    content: str
    question_type: str
    options: list[str] | None
    correct_answer: str
    explanation: str | None
    user_answer: str
    is_correct: bool
    ai_feedback: str | None


class QuizSessionResultResponse(BaseModel):
    """Full session results for the quiz results page."""

    session_id: UUID
    quiz_id: UUID
    quiz_title: str | None
    score: float
    total_questions: int
    correct_answers: int
    started_at: datetime | None
    completed_at: datetime | None
    answers: list[ResultAnswerResponse]
