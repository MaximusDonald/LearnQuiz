"""User model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKey


class User(UUIDPrimaryKey, TimestampMixin, Base):
    """Platform user authenticated locally or via Google OAuth."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    courses: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    quiz_sessions: Mapped[list["QuizSession"]] = relationship(
        "QuizSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    course_progress: Mapped[list["CourseProgress"]] = relationship(
        "CourseProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    course_messages: Mapped[list["CourseMessage"]] = relationship(
        "CourseMessage",
        back_populates="user",
        cascade="all, delete-orphan",
    )
