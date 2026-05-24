"""Gemini service for summaries, quizzes, answer analysis, and course Q&A."""

from __future__ import annotations

import asyncio
import json
import logging
import re
import warnings
from collections.abc import Iterable
from typing import Any, Sequence

from fastapi import HTTPException, status

from app.core.config import settings
from app.services.prompts import PROMPTS
from app.services.quiz_engine import GeneratedQuiz, validate_generated_quiz


try:
    from google import genai as google_genai
except ImportError:  # pragma: no cover - exercised only when the new SDK is unavailable.
    google_genai = None

if google_genai is None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        import google.generativeai as legacy_genai
else:  # pragma: no cover - exercised only when the new SDK is installed.
    legacy_genai = None


logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 800_000
SUMMARY_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemma-4-31b-it",
    "models/gemma-4-26b-a4b-it",
]
QUIZ_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemma-4-31b-it",
    "models/gemma-4-26b-a4b-it",
]
FAST_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash",
    "models/gemini-2.0-flash-lite",
]

genai_client = google_genai.Client(api_key=settings.GEMINI_API_KEY) if google_genai and settings.GEMINI_API_KEY else None
if settings.GEMINI_API_KEY:
    if legacy_genai is not None:
        legacy_genai.configure(api_key=settings.GEMINI_API_KEY)


def ensure_gemini_api_key() -> None:
    """Raise a clear API error when Gemini is not configured."""

    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key is not configured.",
        )


def normalize_model_name(model_name: str) -> str:
    """Strip the SDK prefix when the new client expects bare model ids."""

    return model_name.removeprefix("models/")


def is_invalid_api_key_error(error: Exception) -> bool:
    """Detect invalid Gemini API key failures from SDK exceptions."""

    message = str(error)
    return "API key not valid" in message or "API_KEY_INVALID" in message


def is_quota_error(error: Exception) -> bool:
    """Detect Gemini quota exhaustion errors."""

    message = str(error)
    return "quota" in message.lower() or "ResourceExhausted" in message or "429" in message


def is_model_unavailable_error(error: Exception) -> bool:
    """Detect unsupported or unavailable model errors."""

    message = str(error)
    return "is not found" in message or "not supported for generateContent" in message


def parse_json_response(text: str) -> dict[str, Any]:
    """Clean fenced code blocks and parse a JSON Gemini response."""

    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)


def chunk_text(text: str, chunk_size: int = MAX_TEXT_LENGTH) -> list[str]:
    """Split large course text into chunks compatible with Gemini requests."""

    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks


def _generate_content_sync(model_name: str, prompt: str) -> str:
    """Call the sync Gemini SDK and return text."""

    ensure_gemini_api_key()

    if genai_client is not None:
        response = genai_client.models.generate_content(
            model=normalize_model_name(model_name),
            contents=prompt,
        )
        return (getattr(response, "text", "") or "").strip()

    if legacy_genai is None:
        raise RuntimeError("No Gemini SDK is available.")

    model = legacy_genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return (response.text or "").strip()


async def generate_model_response(model_name: str, prompt: str) -> str:
    """Generate content using the available Gemini client."""

    if genai_client is not None:
        return await asyncio.to_thread(_generate_content_sync, model_name, prompt)

    ensure_gemini_api_key()
    if legacy_genai is None:
        raise RuntimeError("No Gemini SDK is available.")

    model = legacy_genai.GenerativeModel(model_name)
    response = await model.generate_content_async(prompt)
    return (response.text or "").strip()


async def generate_text_response(
    *,
    model_name: str | Sequence[str],
    prompt: str,
    expect_json: bool = False,
    max_attempts: int = 2,
) -> str:
    """Call Gemini and return the raw text response."""

    model_names = [model_name] if isinstance(model_name, str) else list(model_name)
    last_error: Exception | None = None

    for selected_model in model_names:
        for attempt in range(1, max_attempts + 1):
            try:
                text = await generate_model_response(selected_model, prompt)
                if not text:
                    raise ValueError("Gemini returned an empty response.")

                if expect_json:
                    parse_json_response(text)

                return text
            except (Exception, json.JSONDecodeError) as exc:
                last_error = exc
                logger.exception(
                    "Gemini request failed with model %s on attempt %s/%s: %s",
                    selected_model,
                    attempt,
                    max_attempts,
                    exc,
                )

                if is_invalid_api_key_error(exc):
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Gemini API key is invalid or rejected by Google.",
                    ) from exc

                if is_quota_error(exc) or is_model_unavailable_error(exc):
                    break

    detail = "Gemini returned invalid JSON." if expect_json else "AI generation failed."
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=detail,
    ) from last_error


async def summarize_chunks(chunks: Iterable[str]) -> list[str]:
    """Generate a summary for each course chunk independently."""

    partial_summaries: list[str] = []
    for chunk in chunks:
        prompt = PROMPTS["summary"].format(text=chunk)
        partial_summaries.append(
            await generate_text_response(model_name=SUMMARY_MODELS, prompt=prompt),
        )
    return partial_summaries


async def generate_summary(text: str) -> str:
    """Generate a structured markdown summary for a course."""

    chunks = chunk_text(text)
    partial_summaries = await summarize_chunks(chunks)
    if len(partial_summaries) == 1:
        return partial_summaries[0]

    aggregate_prompt = PROMPTS["summary_aggregate"].format(
        text="\n\n".join(partial_summaries),
    )
    return await generate_text_response(
        model_name=SUMMARY_MODELS,
        prompt=aggregate_prompt,
    )


async def generate_quiz(text: str, n_questions: int, difficulty: str) -> dict[str, Any]:
    """Generate a validated quiz JSON payload from course content."""

    chunks = chunk_text(text)
    quiz_source_text = text
    if len(chunks) > 1:
        partial_summaries = await summarize_chunks(chunks)
        quiz_source_text = "\n\n".join(partial_summaries)

    prompt = PROMPTS["quiz"].format(
        text=quiz_source_text,
        n_questions=n_questions,
        difficulty=difficulty,
    )
    raw_response = await generate_text_response(
        model_name=QUIZ_MODELS,
        prompt=prompt,
        expect_json=True,
    )

    try:
        payload = parse_json_response(raw_response)
        quiz: GeneratedQuiz = validate_generated_quiz(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.exception("Invalid quiz JSON from Gemini: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini returned an invalid quiz structure.",
        ) from exc

    return quiz.model_dump()


async def analyze_answer(question: str, correct_answer: str, user_answer: str) -> str:
    """Generate a kind, pedagogical feedback message for a learner answer."""

    prompt = PROMPTS["answer_analysis"].format(
        question=question,
        correct_answer=correct_answer,
        user_answer=user_answer,
    )
    return await generate_text_response(model_name=FAST_MODELS, prompt=prompt)


async def answer_question(
    course_text: str,
    history: list[dict[str, str]],
    question: str,
) -> str:
    """Answer a question about a course using the course text and conversation history."""

    history_text = "\n".join(
        f"{item.get('role', 'user')}: {item.get('content', '')}"
        for item in history
    )
    source_text = "\n\n".join(chunk_text(course_text))[:MAX_TEXT_LENGTH]
    prompt = PROMPTS["course_qa"].format(
        history=history_text or "Aucun historique.",
        course_text=source_text,
        question=question,
    )
    return await generate_text_response(model_name=FAST_MODELS, prompt=prompt)
