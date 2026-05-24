"""Course management API routes."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.course import Course, CourseStatus
from app.models.course import CourseRelation, CourseRelationType
from app.models.progress import CourseMessage, CourseMessageRole
from app.models.quiz import Question, QuestionType, Quiz, QuizDifficulty
from app.schemas.message import (
    CourseMessageCreateRequest,
    CourseMessageExchangeResponse,
    CourseMessageResponse,
)
from app.models.user import User
from app.schemas.course import CourseListItemResponse, CourseResponse
from app.schemas.progress import (
    CourseRelationCreateRequest,
    RelatedCourseSummaryResponse,
)
from app.schemas.quiz import GenerationResponse, QuizResponse, SummaryResponse
from app.services.gemini import answer_question, generate_quiz, generate_summary
from app.services.parser import (
    extract_course_text,
    resolve_course_file_type,
    validate_file_size,
)


router = APIRouter(prefix="/api/courses", tags=["courses"])


async def get_owned_course_or_404(
    course_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> Course:
    """Return a course only when it belongs to the authenticated user."""

    query = select(Course).where(Course.id == course_id, Course.user_id == user_id)
    result = await session.execute(query)
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    return course


async def get_owned_course_with_quizzes_or_404(
    course_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> Course:
    """Return a user-owned course with quiz relationships preloaded."""

    query = (
        select(Course)
        .options(selectinload(Course.quizzes).selectinload(Quiz.questions))
        .where(Course.id == course_id, Course.user_id == user_id)
    )
    result = await session.execute(query)
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    return course


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseResponse:
    """Upload a course file, extract its text, and store it in the database."""

    file_bytes = await file.read()
    validate_file_size(len(file_bytes))
    file_type = resolve_course_file_type(file.filename, file.content_type)

    title = Path(file.filename or "Untitled course").stem or "Untitled course"
    course = Course(
        user_id=current_user.id,
        title=title,
        file_name=file.filename,
        file_type=file_type,
        raw_text="",
        status=CourseStatus.PROCESSING,
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)

    try:
        extracted_text = extract_course_text(file_bytes, file_type)
        course.raw_text = extracted_text
        course.status = CourseStatus.READY
        await session.commit()
        await session.refresh(course)
    except Exception:
        await session.rollback()

        persisted_course = await get_owned_course_or_404(course.id, current_user.id, session)
        persisted_course.status = CourseStatus.ERROR
        await session.commit()
        raise

    return CourseResponse.model_validate(course)


@router.get("", response_model=list[CourseListItemResponse])
async def list_courses(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CourseListItemResponse]:
    """List all courses owned by the authenticated user."""

    query = (
        select(Course)
        .where(Course.user_id == current_user.id)
        .order_by(Course.created_at.desc())
    )
    result = await session.execute(query)
    courses = result.scalars().all()
    return [CourseListItemResponse.model_validate(course) for course in courses]


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseResponse:
    """Return the detail view of a course owned by the current user."""

    course = await get_owned_course_or_404(course_id, current_user.id, session)
    return CourseResponse.model_validate(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a course owned by the current user."""

    course = await get_owned_course_or_404(course_id, current_user.id, session)
    await session.delete(course)
    await session.commit()


@router.post("/{course_id}/generate", response_model=GenerationResponse)
async def generate_course_assets(
    course_id: UUID,
    difficulty: QuizDifficulty = Query(default=QuizDifficulty.MEDIUM),
    n_questions: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GenerationResponse:
    """Generate and persist a summary plus a quiz for a user-owned course."""

    course = await get_owned_course_with_quizzes_or_404(course_id, current_user.id, session)
    summary = await generate_summary(course.raw_text)
    quiz_payload = await generate_quiz(course.raw_text, n_questions, difficulty.value)

    course.summary = summary
    quiz = Quiz(
        course_id=course.id,
        title=quiz_payload["title"],
        difficulty=difficulty,
    )
    session.add(quiz)
    await session.flush()

    for index, question_payload in enumerate(quiz_payload["questions"], start=1):
        question = Question(
            quiz_id=quiz.id,
            content=question_payload["content"],
            question_type=QuestionType.MCQ,
            options=question_payload["options"],
            correct_answer=question_payload["correct_answer"],
            explanation=question_payload["explanation"],
            order_index=index,
        )
        session.add(question)

    await session.commit()
    await session.refresh(course)

    quiz_query = (
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz.id, Quiz.course_id == course.id)
    )
    quiz_result = await session.execute(quiz_query)
    generated_quiz = quiz_result.scalar_one()
    return GenerationResponse(
        summary=summary,
        quiz=QuizResponse.model_validate(generated_quiz),
    )


@router.get("/{course_id}/summary", response_model=SummaryResponse)
async def get_course_summary(
    course_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SummaryResponse:
    """Return the generated summary for a user-owned course."""

    course = await get_owned_course_or_404(course_id, current_user.id, session)
    return SummaryResponse(course_id=course.id, summary=course.summary)


@router.get("/{course_id}/quizzes", response_model=list[QuizResponse])
async def get_course_quizzes(
    course_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[QuizResponse]:
    """Return all generated quizzes for a user-owned course."""

    course = await get_owned_course_with_quizzes_or_404(course_id, current_user.id, session)
    ordered_quizzes = sorted(course.quizzes, key=lambda item: item.created_at, reverse=True)
    return [QuizResponse.model_validate(quiz) for quiz in ordered_quizzes]


@router.post("/{course_id}/relations", response_model=RelatedCourseSummaryResponse, status_code=status.HTTP_201_CREATED)
async def create_course_relation(
    course_id: UUID,
    payload: CourseRelationCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RelatedCourseSummaryResponse:
    """Create a relation between two user-owned courses."""

    course = await get_owned_course_or_404(course_id, current_user.id, session)
    related_course = await get_owned_course_or_404(
        payload.related_course_id,
        current_user.id,
        session,
    )

    if course.id == related_course.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A course cannot be related to itself.",
        )

    try:
        relation_type = CourseRelationType(payload.relation_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid relation type.",
        ) from exc

    existing_query = select(CourseRelation).where(
        CourseRelation.course_id == course.id,
        CourseRelation.related_course_id == related_course.id,
        CourseRelation.relation_type == relation_type,
    )
    existing = (await session.execute(existing_query)).scalar_one_or_none()
    if existing is not None:
        return RelatedCourseSummaryResponse(
            relation_id=existing.id,
            relation_type=existing.relation_type.value,
            course_id=related_course.id,
            title=related_course.title,
            status=related_course.status.value,
            created_at=existing.created_at,
        )

    relation = CourseRelation(
        course_id=course.id,
        related_course_id=related_course.id,
        relation_type=relation_type,
    )
    session.add(relation)
    await session.commit()
    await session.refresh(relation)

    return RelatedCourseSummaryResponse(
        relation_id=relation.id,
        relation_type=relation.relation_type.value,
        course_id=related_course.id,
        title=related_course.title,
        status=related_course.status.value,
        created_at=relation.created_at,
    )


@router.get("/{course_id}/relations", response_model=list[RelatedCourseSummaryResponse])
async def get_course_relations(
    course_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RelatedCourseSummaryResponse]:
    """Return related courses for one owned course."""

    await get_owned_course_or_404(course_id, current_user.id, session)
    query = (
        select(CourseRelation, Course)
        .join(Course, Course.id == CourseRelation.related_course_id)
        .where(CourseRelation.course_id == course_id, Course.user_id == current_user.id)
        .order_by(CourseRelation.created_at.desc())
    )
    rows = (await session.execute(query)).all()
    return [
        RelatedCourseSummaryResponse(
            relation_id=relation.id,
            relation_type=relation.relation_type.value,
            course_id=related_course.id,
            title=related_course.title,
            status=related_course.status.value,
            created_at=relation.created_at,
        )
        for relation, related_course in rows
    ]


@router.get("/{course_id}/messages", response_model=list[CourseMessageResponse])
async def get_course_messages(
    course_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CourseMessageResponse]:
    """Return the Q&A history for a user-owned course."""

    await get_owned_course_or_404(course_id, current_user.id, session)
    query = (
        select(CourseMessage)
        .where(
            CourseMessage.course_id == course_id,
            CourseMessage.user_id == current_user.id,
        )
        .order_by(CourseMessage.created_at.asc())
    )
    result = await session.execute(query)
    messages = result.scalars().all()
    return [CourseMessageResponse.model_validate(message) for message in messages]


@router.post("/{course_id}/messages", response_model=CourseMessageExchangeResponse)
async def create_course_message(
    course_id: UUID,
    payload: CourseMessageCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseMessageExchangeResponse:
    """Ask a contextual question about a course and persist the exchange."""

    course = await get_owned_course_or_404(course_id, current_user.id, session)
    history_query = (
        select(CourseMessage)
        .where(
            CourseMessage.course_id == course.id,
            CourseMessage.user_id == current_user.id,
        )
        .order_by(CourseMessage.created_at.desc())
        .limit(15)
    )
    history_result = await session.execute(history_query)
    recent_messages = list(reversed(history_result.scalars().all()))
    history = [
        {
            "role": message.role.value,
            "content": message.content,
        }
        for message in recent_messages
    ]

    assistant_answer = await answer_question(
        course_text=course.raw_text,
        history=history,
        question=payload.question,
    )

    user_message = CourseMessage(
        user_id=current_user.id,
        course_id=course.id,
        role=CourseMessageRole.USER,
        content=payload.question,
    )
    assistant_message = CourseMessage(
        user_id=current_user.id,
        course_id=course.id,
        role=CourseMessageRole.ASSISTANT,
        content=assistant_answer,
    )
    session.add(user_message)
    session.add(assistant_message)
    await session.commit()
    await session.refresh(user_message)
    await session.refresh(assistant_message)

    return CourseMessageExchangeResponse(
        user_message=CourseMessageResponse.model_validate(user_message),
        assistant_message=CourseMessageResponse.model_validate(assistant_message),
    )
