"""Course and course relation models."""

import uuid
from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKey


def enum_values(enum_class: type[Enum]) -> list[str]:
    """Return SQL enum values from a Python Enum class."""

    return [member.value for member in enum_class]


class CourseFileType(str, Enum):
    """Allowed source file types for uploaded courses."""

    PDF = "pdf"
    TXT = "txt"
    MD = "md"


class CourseStatus(str, Enum):
    """Processing status for a course."""

    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class CourseRelationType(str, Enum):
    """Relationship type between two courses."""

    PREREQUISITE = "prerequisite"
    SEQUEL = "sequel"
    RELATED = "related"


class Course(UUIDPrimaryKey, TimestampMixin, Base):
    """Uploaded course content owned by a user."""

    __tablename__ = "courses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_type: Mapped[CourseFileType | None] = mapped_column(
        SqlEnum(
            CourseFileType,
            name="course_file_type",
            values_callable=enum_values,
        ),
        nullable=True,
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CourseStatus] = mapped_column(
        SqlEnum(
            CourseStatus,
            name="course_status",
            values_callable=enum_values,
        ),
        nullable=False,
        default=CourseStatus.PROCESSING,
        server_default=CourseStatus.PROCESSING.value,
    )

    user: Mapped["User"] = relationship("User", back_populates="courses")
    quizzes: Mapped[list["Quiz"]] = relationship(
        "Quiz",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    progress: Mapped[list["CourseProgress"]] = relationship(
        "CourseProgress",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["CourseMessage"]] = relationship(
        "CourseMessage",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    relations: Mapped[list["CourseRelation"]] = relationship(
        "CourseRelation",
        foreign_keys="CourseRelation.course_id",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    related_by: Mapped[list["CourseRelation"]] = relationship(
        "CourseRelation",
        foreign_keys="CourseRelation.related_course_id",
        back_populates="related_course",
        cascade="all, delete-orphan",
    )


class CourseRelation(UUIDPrimaryKey, TimestampMixin, Base):
    """Pedagogical relation between two courses."""

    __tablename__ = "course_relations"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    related_course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relation_type: Mapped[CourseRelationType] = mapped_column(
        SqlEnum(
            CourseRelationType,
            name="course_relation_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    course: Mapped["Course"] = relationship(
        "Course",
        foreign_keys=[course_id],
        back_populates="relations",
    )
    related_course: Mapped["Course"] = relationship(
        "Course",
        foreign_keys=[related_course_id],
        back_populates="related_by",
    )
