"""Course progress and course message models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum
from sqlalchemy import Float, ForeignKey, Integer, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKey


def enum_values(enum_class: type[Enum]) -> list[str]:
    """Return SQL enum values from a Python Enum class."""

    return [member.value for member in enum_class]


class CourseMessageRole(str, Enum):
    """Role of a message in a course Q&A conversation."""

    USER = "user"
    ASSISTANT = "assistant"


class CourseProgress(UUIDPrimaryKey, TimestampMixin, Base):
    """Aggregated learning progress for a user on a course."""

    __tablename__ = "course_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    total_sessions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    best_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_session_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    weak_topics: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="course_progress")
    course: Mapped["Course"] = relationship("Course", back_populates="progress")


class CourseMessage(UUIDPrimaryKey, TimestampMixin, Base):
    """Conversation message tied to a course."""

    __tablename__ = "course_messages"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[CourseMessageRole] = mapped_column(
        SqlEnum(
            CourseMessageRole,
            name="course_message_role",
            values_callable=enum_values,
        ),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="course_messages")
    course: Mapped["Course"] = relationship("Course", back_populates="messages")
