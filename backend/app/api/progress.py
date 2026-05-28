"""Progress dashboard API routes."""

from collections import Counter
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.course import Course
from app.models.progress import CourseProgress
from app.models.quiz import Quiz
from app.models.quiz_session import QuizSession
from app.models.user import User
from app.schemas.progress import (
    CourseProgressDetailResponse,
    CourseScorePointResponse,
    GlobalProgressResponse,
    RecentCourseProgressResponse,
)


router = APIRouter(prefix="/api", tags=["progress"])


def aggregate_topics(topic_lists: list[list[str] | None], limit: int = 8) -> list[str]:
    """Aggregate weak topics across many courses using simple counting."""

    counter: Counter[str] = Counter()
    for topics in topic_lists:
        if not topics:
            continue
        for topic in topics:
            normalized = topic.strip()
            if normalized:
                counter[normalized] += 1
    return [topic for topic, _count in counter.most_common(limit)]


@router.get("/progress", response_model=GlobalProgressResponse)
async def get_global_progress(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GlobalProgressResponse:
    """Return global progress statistics for the authenticated user."""

    total_courses_query = select(func.count(Course.id)).where(Course.user_id == current_user.id)
    total_courses = (await session.execute(total_courses_query)).scalar_one()

    sessions_query = (
        select(QuizSession)
        .options(selectinload(QuizSession.quiz))
        .join(QuizSession.quiz)
        .join(Quiz.course)
        .where(
            QuizSession.user_id == current_user.id,
            Course.user_id == current_user.id,
            QuizSession.completed_at.is_not(None),  # Exclude abandoned/in-progress sessions
        )
        .order_by(QuizSession.completed_at.desc().nullslast(), QuizSession.started_at.desc())
    )
    sessions = (await session.execute(sessions_query)).scalars().all()
    total_quiz_sessions = len(sessions)
    average_score = (
        sum(session_item.score or 0.0 for session_item in sessions) / total_quiz_sessions
        if total_quiz_sessions
        else 0.0
    )

    progress_query = (
        select(CourseProgress, Course)
        .join(Course, Course.id == CourseProgress.course_id)
        .where(CourseProgress.user_id == current_user.id, Course.user_id == current_user.id)
        .order_by(CourseProgress.last_session_at.desc().nullslast(), Course.created_at.desc())
    )
    progress_rows = (await session.execute(progress_query)).all()
    weak_topics = aggregate_topics([progress.weak_topics for progress, _course in progress_rows])
    latest_score_by_course_id: dict[UUID, float | None] = {}
    for session_item in sessions:
        quiz = session_item.quiz
        if quiz is None or quiz.course_id in latest_score_by_course_id:
            continue
        latest_score_by_course_id[quiz.course_id] = session_item.score

    progress_by_course_id: dict[UUID, CourseProgress] = {
        progress.course_id: progress for progress, _course in progress_rows
    }
    recent_course_rows = (
        await session.execute(
            select(Course)
            .where(Course.user_id == current_user.id)
            .order_by(Course.created_at.desc())
            .limit(5)
        )
    ).scalars().all()

    recent_courses = [
        RecentCourseProgressResponse(
            course_id=course.id,
            title=course.title,
            latest_score=latest_score_by_course_id.get(course.id),
            best_score=progress_by_course_id.get(course.id).best_score
            if progress_by_course_id.get(course.id)
            else None,
            total_sessions=progress_by_course_id.get(course.id).total_sessions
            if progress_by_course_id.get(course.id)
            else 0,
            last_session_at=progress_by_course_id.get(course.id).last_session_at
            if progress_by_course_id.get(course.id)
            else None,
        )
        for course in recent_course_rows
    ]

    return GlobalProgressResponse(
        total_courses=total_courses,
        total_quiz_sessions=total_quiz_sessions,
        average_score=average_score,
        weak_topics=weak_topics,
        recent_courses=recent_courses,
    )


@router.get("/courses/{course_id}/progress", response_model=CourseProgressDetailResponse)
async def get_course_progress(
    course_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseProgressDetailResponse:
    """Return detailed progress for a single owned course."""

    course_query = select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    course = (await session.execute(course_query)).scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

    progress_query = select(CourseProgress).where(
        CourseProgress.user_id == current_user.id,
        CourseProgress.course_id == course_id,
    )
    course_progress = (await session.execute(progress_query)).scalar_one_or_none()

    score_history_query = (
        select(QuizSession)
        .join(QuizSession.quiz)
        .where(
            QuizSession.user_id == current_user.id,
            Quiz.course_id == course_id,
            QuizSession.completed_at.is_not(None),  # Only count completed sessions
        )
        .order_by(QuizSession.completed_at.asc().nullslast(), QuizSession.started_at.asc())
    )
    session_items = (await session.execute(score_history_query)).scalars().all()

    # Always derive total_sessions from completed sessions in DB for consistency.
    total_sessions = len(session_items)
    if course_progress is not None and course_progress.total_sessions != total_sessions:
        # Self-heal: keep CourseProgress.total_sessions in sync with reality.
        course_progress.total_sessions = total_sessions
        await session.commit()
    average_score = (
        sum(item.score or 0.0 for item in session_items) / len(session_items)
        if session_items
        else 0.0
    )

    return CourseProgressDetailResponse(
        course_id=course_id,
        total_sessions=total_sessions,
        best_score=course_progress.best_score if course_progress else None,
        average_score=average_score,
        score_history=[
            CourseScorePointResponse(
                session_id=item.id,
                score=item.score or 0.0,
                completed_at=item.completed_at,
            )
            for item in session_items
        ],
        weak_topics=course_progress.weak_topics or [] if course_progress else [],
    )
