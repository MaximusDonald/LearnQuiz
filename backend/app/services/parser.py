"""Parsing service for uploaded course files."""

from io import BytesIO
from pathlib import Path

import fitz
from fastapi import HTTPException, status

from app.models.course import CourseFileType


MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_MIME_TYPES: dict[str, CourseFileType] = {
    "application/pdf": CourseFileType.PDF,
    "text/plain": CourseFileType.TXT,
    "text/markdown": CourseFileType.MD,
    "text/x-markdown": CourseFileType.MD,
}
ALLOWED_SUFFIXES: dict[str, CourseFileType] = {
    ".pdf": CourseFileType.PDF,
    ".txt": CourseFileType.TXT,
    ".md": CourseFileType.MD,
}


def resolve_course_file_type(filename: str | None, content_type: str | None) -> CourseFileType:
    """Resolve the logical course file type from MIME type or extension."""

    if content_type in ALLOWED_MIME_TYPES:
        return ALLOWED_MIME_TYPES[content_type]

    suffix = Path(filename or "").suffix.lower()
    if suffix in ALLOWED_SUFFIXES:
        return ALLOWED_SUFFIXES[suffix]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type. Only PDF, TXT, and MD files are allowed.",
    )


def validate_file_size(file_size: int) -> None:
    """Reject files larger than the project limit."""

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10MB limit.",
        )


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from a PDF using PyMuPDF."""

    with fitz.open(stream=BytesIO(file_bytes), filetype="pdf") as document:
        pages = [page.get_text("text") for page in document]
    return normalize_extracted_text("\n".join(pages))


def extract_text_file(file_bytes: bytes) -> str:
    """Extract text from a TXT/MD file."""

    return normalize_extracted_text(file_bytes.decode("utf-8", errors="ignore"))


def extract_course_text(file_bytes: bytes, file_type: CourseFileType) -> str:
    """Extract the raw text content from a supported course file."""

    if file_type == CourseFileType.PDF:
        text = extract_pdf_text(file_bytes)
    else:
        text = extract_text_file(file_bytes)

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file did not contain readable text.",
        )

    return text


def normalize_extracted_text(text: str) -> str:
    """Normalize extracted text for consistent storage."""

    sanitized = text.replace("\x00", "").replace("\ufeff", "")
    lines = [line.rstrip() for line in sanitized.splitlines()]
    collapsed = "\n".join(line for line in lines if line.strip())
    return collapsed.strip()
