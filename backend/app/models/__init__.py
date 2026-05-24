"""Import all models here for Alembic auto-detection."""

from app.core.database import Base
from app.models.course import (
    Course,
    CourseFileType,
    CourseRelation,
    CourseRelationType,
    CourseStatus,
)
from app.models.mixins import TimestampMixin, UUIDPrimaryKey
from app.models.progress import CourseMessage, CourseMessageRole, CourseProgress
from app.models.quiz import Question, QuestionType, Quiz, QuizDifficulty
from app.models.quiz_session import QuizSession, UserAnswer
from app.models.user import User


__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKey",
    "User",
    "Course",
    "CourseRelation",
    "CourseFileType",
    "CourseStatus",
    "CourseRelationType",
    "Quiz",
    "Question",
    "QuizDifficulty",
    "QuestionType",
    "QuizSession",
    "UserAnswer",
    "CourseProgress",
    "CourseMessage",
    "CourseMessageRole",
]
