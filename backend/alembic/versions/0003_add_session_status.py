"""Add status column to quiz_sessions.

Adds a session_status enum type and a status column to the quiz_sessions table
to distinguish in-progress sessions from completed ones. Existing sessions
(which all have a completed_at value) are backfilled as 'completed'; any
sessions without completed_at are set to 'in_progress'.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_add_session_status"
down_revision: str | None = "0002_add_updated_at_triggers"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


session_status = postgresql.ENUM(
    "in_progress",
    "completed",
    name="session_status",
    create_type=False,
)


def upgrade() -> None:
    """Add session_status enum and status column to quiz_sessions."""

    bind = op.get_bind()
    session_status.create(bind, checkfirst=True)

    op.add_column(
        "quiz_sessions",
        sa.Column(
            "status",
            session_status,
            nullable=False,
            server_default="in_progress",
        ),
    )

    # Backfill: sessions that were completed before this migration.
    op.execute(
        """
        UPDATE quiz_sessions
        SET status = 'completed'
        WHERE completed_at IS NOT NULL;
        """
    )


def downgrade() -> None:
    """Remove the status column and session_status enum."""

    op.drop_column("quiz_sessions", "status")

    bind = op.get_bind()
    session_status.drop(bind, checkfirst=True)
