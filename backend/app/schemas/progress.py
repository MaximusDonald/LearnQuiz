"""Pydantic schemas for progress and course relations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RecentCourseProgressResponse(BaseModel):
    """Summary of a course with progress information for the dashboard."""

    course_id: UUID
    title: str
    latest_score: float | None
    best_score: float | None
    total_sessions: int
    last_session_at: datetime | None


class GlobalProgressResponse(BaseModel):
    """Global dashboard progress summary."""

    total_courses: int
    total_quiz_sessions: int
    average_score: float
    weak_topics: list[str]
    recent_courses: list[RecentCourseProgressResponse]


class CourseScorePointResponse(BaseModel):
    """One historical score point for a course."""

    session_id: UUID
    score: float
    completed_at: datetime | None


class CourseProgressDetailResponse(BaseModel):
    """Detailed progress summary for one course."""

    course_id: UUID
    total_sessions: int
    best_score: float | None
    average_score: float
    score_history: list[CourseScorePointResponse]
    weak_topics: list[str]


class CourseRelationCreateRequest(BaseModel):
    """Payload used to create a relation between two owned courses."""

    related_course_id: UUID
    relation_type: str


class RelatedCourseSummaryResponse(BaseModel):
    """Serializable course relation item."""

    relation_id: UUID
    relation_type: str
    course_id: UUID
    title: str
    status: str
    created_at: datetime
