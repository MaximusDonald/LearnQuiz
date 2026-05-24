"""Quiz and question models."""

import uuid
from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKey


def enum_values(enum_class: type[Enum]) -> list[str]:
    """Return SQL enum values from a Python Enum class."""

    return [member.value for member in enum_class]


class QuizDifficulty(str, Enum):
    """Supported difficulty levels for generated quizzes."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, Enum):
    """Supported question types."""

    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    OPEN = "open"


class Quiz(UUIDPrimaryKey, TimestampMixin, Base):
    """Generated quiz associated with a course."""

    __tablename__ = "quizzes"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    difficulty: Mapped[QuizDifficulty] = mapped_column(
        SqlEnum(
            QuizDifficulty,
            name="quiz_difficulty",
            values_callable=enum_values,
        ),
        nullable=False,
        default=QuizDifficulty.MEDIUM,
        server_default=QuizDifficulty.MEDIUM.value,
    )

    course: Mapped["Course"] = relationship("Course", back_populates="quizzes")
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["QuizSession"]] = relationship(
        "QuizSession",
        back_populates="quiz",
        cascade="all, delete-orphan",
    )


class Question(UUIDPrimaryKey, TimestampMixin, Base):
    """Question generated inside a quiz."""

    __tablename__ = "questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        SqlEnum(
            QuestionType,
            name="question_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )
    options: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    answers: Mapped[list["UserAnswer"]] = relationship(
        "UserAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )
