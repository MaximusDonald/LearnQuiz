"""Quiz session and user answer models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, Float, ForeignKey, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKey


def enum_values(enum_class: type[Enum]) -> list[str]:
    """Return SQL enum values from a Python Enum class."""

    return [member.value for member in enum_class]


class SessionStatus(str, Enum):
    """Lifecycle status of a quiz session."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class QuizSession(UUIDPrimaryKey, TimestampMixin, Base):
    """A user's attempt on a generated quiz."""

    __tablename__ = "quiz_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[SessionStatus] = mapped_column(
        SqlEnum(
            SessionStatus,
            name="session_status",
            values_callable=enum_values,
        ),
        nullable=False,
        default=SessionStatus.IN_PROGRESS,
        server_default=SessionStatus.IN_PROGRESS.value,
    )

    user: Mapped["User"] = relationship("User", back_populates="quiz_sessions")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="sessions")
    answers: Mapped[list["UserAnswer"]] = relationship(
        "UserAnswer",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class UserAnswer(UUIDPrimaryKey, TimestampMixin, Base):
    """Answer submitted by a user for a quiz question."""

    __tablename__ = "user_answers"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    session: Mapped["QuizSession"] = relationship(
        "QuizSession",
        back_populates="answers",
    )
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="answers",
    )
