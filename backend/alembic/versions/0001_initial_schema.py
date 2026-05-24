"""Initial schema for LearnQUIZ."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


course_file_type = postgresql.ENUM(
    "pdf",
    "txt",
    "md",
    name="course_file_type",
    create_type=False,
)
course_status = postgresql.ENUM(
    "processing",
    "ready",
    "error",
    name="course_status",
    create_type=False,
)
course_relation_type = postgresql.ENUM(
    "prerequisite",
    "sequel",
    "related",
    name="course_relation_type",
    create_type=False,
)
quiz_difficulty = postgresql.ENUM(
    "easy",
    "medium",
    "hard",
    name="quiz_difficulty",
    create_type=False,
)
question_type = postgresql.ENUM(
    "mcq",
    "true_false",
    "open",
    name="question_type",
    create_type=False,
)
course_message_role = postgresql.ENUM(
    "user",
    "assistant",
    name="course_message_role",
    create_type=False,
)


def upgrade() -> None:
    """Create the initial LearnQUIZ schema."""

    bind = op.get_bind()
    course_file_type.create(bind, checkfirst=True)
    course_status.create(bind, checkfirst=True)
    course_relation_type.create(bind, checkfirst=True)
    quiz_difficulty.create(bind, checkfirst=True)
    question_type.create(bind, checkfirst=True)
    course_message_role.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("google_id", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_google_id"), "users", ["google_id"], unique=True)

    op.create_table(
        "courses",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_name", sa.String(length=500), nullable=True),
        sa.Column("file_type", course_file_type, nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "status",
            course_status,
            server_default="processing",
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_courses_user_id"), "courses", ["user_id"], unique=False)

    op.create_table(
        "quizzes",
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column(
            "difficulty",
            quiz_difficulty,
            server_default="medium",
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quizzes_course_id"), "quizzes", ["course_id"], unique=False)

    op.create_table(
        "course_messages",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("role", course_message_role, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_course_messages_course_id"),
        "course_messages",
        ["course_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_course_messages_user_id"),
        "course_messages",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "course_progress",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("total_sessions", sa.Integer(), server_default="0", nullable=False),
        sa.Column("best_score", sa.Float(), nullable=True),
        sa.Column("last_session_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("weak_topics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_course_progress_course_id"),
        "course_progress",
        ["course_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_course_progress_user_id"),
        "course_progress",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "course_relations",
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("related_course_id", sa.UUID(), nullable=False),
        sa.Column("relation_type", course_relation_type, nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["related_course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_course_relations_course_id"),
        "course_relations",
        ["course_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_course_relations_related_course_id"),
        "course_relations",
        ["related_course_id"],
        unique=False,
    )

    op.create_table(
        "questions",
        sa.Column("quiz_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("question_type", question_type, nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_questions_quiz_id"),
        "questions",
        ["quiz_id"],
        unique=False,
    )

    op.create_table(
        "quiz_sessions",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("quiz_id", sa.UUID(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_quiz_sessions_quiz_id"),
        "quiz_sessions",
        ["quiz_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_quiz_sessions_user_id"),
        "quiz_sessions",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "user_answers",
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("ai_feedback", sa.Text(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["quiz_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_answers_question_id"),
        "user_answers",
        ["question_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_answers_session_id"),
        "user_answers",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the initial LearnQUIZ schema."""

    op.drop_index(op.f("ix_user_answers_session_id"), table_name="user_answers")
    op.drop_index(op.f("ix_user_answers_question_id"), table_name="user_answers")
    op.drop_table("user_answers")

    op.drop_index(op.f("ix_quiz_sessions_user_id"), table_name="quiz_sessions")
    op.drop_index(op.f("ix_quiz_sessions_quiz_id"), table_name="quiz_sessions")
    op.drop_table("quiz_sessions")

    op.drop_index(op.f("ix_questions_quiz_id"), table_name="questions")
    op.drop_table("questions")

    op.drop_index(op.f("ix_course_relations_related_course_id"), table_name="course_relations")
    op.drop_index(op.f("ix_course_relations_course_id"), table_name="course_relations")
    op.drop_table("course_relations")

    op.drop_index(op.f("ix_course_progress_user_id"), table_name="course_progress")
    op.drop_index(op.f("ix_course_progress_course_id"), table_name="course_progress")
    op.drop_table("course_progress")

    op.drop_index(op.f("ix_course_messages_user_id"), table_name="course_messages")
    op.drop_index(op.f("ix_course_messages_course_id"), table_name="course_messages")
    op.drop_table("course_messages")

    op.drop_index(op.f("ix_quizzes_course_id"), table_name="quizzes")
    op.drop_table("quizzes")

    op.drop_index(op.f("ix_courses_user_id"), table_name="courses")
    op.drop_table("courses")

    op.drop_index(op.f("ix_users_google_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    course_message_role.drop(bind, checkfirst=True)
    question_type.drop(bind, checkfirst=True)
    quiz_difficulty.drop(bind, checkfirst=True)
    course_relation_type.drop(bind, checkfirst=True)
    course_status.drop(bind, checkfirst=True)
    course_file_type.drop(bind, checkfirst=True)
