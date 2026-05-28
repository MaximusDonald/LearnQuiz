"""Quiz session API routes."""

from datetime import datetime, timezone
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.progress import CourseProgress
from app.models.quiz import Question, QuestionType, Quiz
from app.models.quiz_session import QuizSession, UserAnswer
from app.models.user import User
from app.schemas.quiz_session import (
    CompleteQuizSessionResponse,
    QuizSessionCreateRequest,
    QuizSessionCreateResponse,
    QuizSessionResultResponse,
    ResultAnswerResponse,
    SessionQuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.gemini import analyze_answer


router = APIRouter(prefix="/api/quiz-sessions", tags=["quiz-sessions"])

STOPWORDS = {
    "quelle",
    "quelles",
    "quel",
    "quels",
    "comment",
    "pourquoi",
    "dans",
    "avec",
    "sans",
    "sont",
    "est",
    "les",
    "des",
    "une",
    "que",
    "quoi",
    "quand",
    "where",
    "what",
    "which",
    "from",
    "pour",
    "this",
    "that",
}


async def get_owned_quiz_or_404(
    quiz_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> Quiz:
    """Return a quiz only when it belongs to a course owned by the current user."""

    query = (
        select(Quiz)
        .options(selectinload(Quiz.questions), selectinload(Quiz.course))
        .join(Quiz.course)
        .where(Quiz.id == quiz_id, Quiz.course.has(user_id=user_id))
    )
    result = await session.execute(query)
    quiz = result.scalar_one_or_none()
    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )
    return quiz


async def get_owned_session_or_404(
    session_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> QuizSession:
    """Return a quiz session only when it belongs to the current user."""

    query = (
        select(QuizSession)
        .options(
            selectinload(QuizSession.quiz).selectinload(Quiz.questions),
            selectinload(QuizSession.answers).selectinload(UserAnswer.question),
        )
        .where(QuizSession.id == session_id, QuizSession.user_id == user_id)
    )
    result = await session.execute(query)
    quiz_session = result.scalar_one_or_none()
    if quiz_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz session not found.",
        )
    return quiz_session


def normalize_answer(answer: str) -> str:
    """Normalize answers for correctness checks."""

    return answer.strip().casefold()


def extract_weak_topics_from_answers(answers: list[UserAnswer]) -> list[str]:
    """Extract simple weak-topic keywords from incorrect answers' questions."""

    tokens: list[str] = []
    for answer in answers:
        if answer.is_correct or answer.question is None:
            continue
        words = re.findall(r"[A-Za-zÀ-ÿ]{4,}", answer.question.content.casefold())
        tokens.extend(word for word in words if word not in STOPWORDS)

    counts = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    sorted_topics = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [topic for topic, _count in sorted_topics[:8]]


def merge_weak_topics(
    existing_topics: list[str] | None,
    new_topics: list[str],
    limit: int = 8,
) -> list[str]:
    """Merge historical weak topics with the latest session topics."""

    counts: dict[str, int] = {}
    for topic in existing_topics or []:
        normalized = topic.strip()
        if normalized:
            counts[normalized] = counts.get(normalized, 0) + 1

    for topic in new_topics:
        normalized = topic.strip()
        if normalized:
            counts[normalized] = counts.get(normalized, 0) + 2

    ranked_topics = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [topic for topic, _count in ranked_topics[:limit]]


def evaluate_answer(question: Question, user_answer: str) -> bool:
    """Evaluate whether an answer should be considered correct."""

    if question.question_type in {QuestionType.MCQ, QuestionType.TRUE_FALSE, QuestionType.OPEN}:
        return normalize_answer(user_answer) == normalize_answer(question.correct_answer)
    return False


@router.post("", response_model=QuizSessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz_session(
    payload: QuizSessionCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizSessionCreateResponse:
    """Create a new session for a quiz owned by the current user."""

    quiz = await get_owned_quiz_or_404(payload.quiz_id, current_user.id, session)
    quiz_session = QuizSession(
        user_id=current_user.id,
        quiz_id=quiz.id,
        started_at=datetime.now(timezone.utc),
    )
    session.add(quiz_session)
    await session.commit()
    await session.refresh(quiz_session)

    ordered_questions = sorted(quiz.questions, key=lambda item: item.order_index)
    return QuizSessionCreateResponse(
        session_id=quiz_session.id,
        quiz_id=quiz.id,
        questions=[SessionQuestionResponse.model_validate(question) for question in ordered_questions],
    )


@router.post("/{session_id}/answers", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: UUID,
    payload: SubmitAnswerRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmitAnswerResponse:
    """Submit and evaluate one answer inside a quiz session."""

    quiz_session = await get_owned_session_or_404(session_id, current_user.id, session)
    question = next(
        (item for item in quiz_session.quiz.questions if item.id == payload.question_id),
        None,
    )
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in this quiz session.",
        )

    existing_answer = next(
        (item for item in quiz_session.answers if item.question_id == payload.question_id),
        None,
    )
    is_correct = evaluate_answer(question, payload.user_answer)
    ai_feedback = None

    if existing_answer is None:
        answer = UserAnswer(
            session_id=quiz_session.id,
            question_id=question.id,
            user_answer=payload.user_answer,
            is_correct=is_correct,
            ai_feedback=ai_feedback,
            answered_at=datetime.now(timezone.utc),
        )
        session.add(answer)
    else:
        answer = existing_answer
        answer.user_answer = payload.user_answer
        answer.is_correct = is_correct
        answer.ai_feedback = ai_feedback
        answer.answered_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(answer)

    return SubmitAnswerResponse(
        answer_id=answer.id,
        question_id=question.id,
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        ai_feedback=ai_feedback,
    )


@router.post("/{session_id}/complete", response_model=CompleteQuizSessionResponse)
async def complete_quiz_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompleteQuizSessionResponse:
    """Finalize a session, compute the score, and update course progress."""

    quiz_session = await get_owned_session_or_404(session_id, current_user.id, session)
    ordered_questions = sorted(quiz_session.quiz.questions, key=lambda item: item.order_index)
    total_questions = len(ordered_questions)
    correct_answers = sum(1 for answer in quiz_session.answers if answer.is_correct)
    score = (correct_answers / total_questions) if total_questions else 0.0

    quiz_session.completed_at = datetime.now(timezone.utc)
    quiz_session.score = score

    progress_query = select(CourseProgress).where(
        CourseProgress.user_id == current_user.id,
        CourseProgress.course_id == quiz_session.quiz.course_id,
    )
    progress_result = await session.execute(progress_query)
    course_progress = progress_result.scalar_one_or_none()
    weak_topics = extract_weak_topics_from_answers(quiz_session.answers)

    if course_progress is None:
        course_progress = CourseProgress(
            user_id=current_user.id,
            course_id=quiz_session.quiz.course_id,
            total_sessions=1,
            best_score=score,
            last_session_at=quiz_session.completed_at,
            weak_topics=weak_topics,
        )
        session.add(course_progress)
    else:
        course_progress.total_sessions += 1
        course_progress.best_score = max(course_progress.best_score or 0.0, score)
        course_progress.last_session_at = quiz_session.completed_at
        course_progress.weak_topics = merge_weak_topics(course_progress.weak_topics, weak_topics)

    await session.commit()

    return CompleteQuizSessionResponse(
        session_id=quiz_session.id,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_answers,
    )


@router.get("/{session_id}/results", response_model=QuizSessionResultResponse)
async def get_quiz_session_results(
    session_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizSessionResultResponse:
    """Return the results of a completed quiz session."""

    quiz_session = await get_owned_session_or_404(session_id, current_user.id, session)
    ordered_questions = sorted(quiz_session.quiz.questions, key=lambda item: item.order_index)
    answer_by_question_id = {answer.question_id: answer for answer in quiz_session.answers}
    answers: list[ResultAnswerResponse] = []

    for question in ordered_questions:
        user_answer = answer_by_question_id.get(question.id)
        if user_answer is None:
            continue

        answers.append(
            ResultAnswerResponse(
                question_id=question.id,
                content=question.content,
                question_type=question.question_type.value,
                options=question.options,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                user_answer=user_answer.user_answer,
                is_correct=user_answer.is_correct,
                ai_feedback=user_answer.ai_feedback,
            )
        )

    total_questions = len(ordered_questions)
    correct_answers = sum(1 for answer in answers if answer.is_correct)
    return QuizSessionResultResponse(
        session_id=quiz_session.id,
        quiz_id=quiz_session.quiz.id,
        quiz_title=quiz_session.quiz.title,
        score=quiz_session.score or 0.0,
        total_questions=total_questions,
        correct_answers=correct_answers,
        started_at=quiz_session.started_at,
        completed_at=quiz_session.completed_at,
        answers=answers,
    )
