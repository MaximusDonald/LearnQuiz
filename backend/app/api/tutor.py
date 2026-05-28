"""Tutor AI API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.quiz_session import UserAnswer
from app.models.user import User
from app.schemas.tutor import TutorFeedbackResponse
from app.services.gemini import analyze_answer

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


@router.post("/{answer_id}/analyze", response_model=TutorFeedbackResponse)
async def generate_feedback(
    answer_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TutorFeedbackResponse:
    """Generate pedagogical feedback from the Tutor AI for an incorrect answer."""

    query = (
        select(UserAnswer)
        .options(selectinload(UserAnswer.question), selectinload(UserAnswer.session))
        .where(UserAnswer.id == answer_id)
    )
    result = await session.execute(query)
    user_answer = result.scalar_one_or_none()

    if user_answer is None or user_answer.session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User answer not found.",
        )

    if user_answer.is_correct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate feedback for a correct answer.",
        )

    if user_answer.ai_feedback:
        return TutorFeedbackResponse(
            answer_id=user_answer.id,
            ai_feedback=user_answer.ai_feedback,
        )

    feedback = await analyze_answer(
        question=user_answer.question.content,
        correct_answer=user_answer.question.correct_answer,
        user_answer=user_answer.user_answer,
    )

    user_answer.ai_feedback = feedback
    await session.commit()

    return TutorFeedbackResponse(
        answer_id=user_answer.id,
        ai_feedback=feedback,
    )
