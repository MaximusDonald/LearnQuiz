"""Add database-level updated_at triggers."""

from collections.abc import Sequence

from alembic import op


revision: str = "0002_add_updated_at_triggers"
down_revision: str | None = "0001_initial_schema"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


TABLES = (
    "users",
    "courses",
    "course_relations",
    "quizzes",
    "questions",
    "quiz_sessions",
    "user_answers",
    "course_progress",
    "course_messages",
)


def upgrade() -> None:
    """Create a shared trigger function and attach it to all tables."""

    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    for table_name in TABLES:
        op.execute(
            f"""
            CREATE TRIGGER trg_{table_name}_updated_at
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    """Drop the updated_at triggers and shared trigger function."""

    for table_name in reversed(TABLES):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_updated_at ON {table_name};")

    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")
