"""Persist session agent state

Revision ID: 8ce1abd5c49c
Revises: af4531c554d3
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8ce1abd5c49c"
down_revision: Union[str, Sequence[str], None] = "af4531c554d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column(
            "last_agent",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "sessions",
        sa.Column(
            "hint_level",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("sessions", "hint_level")
    op.drop_column("sessions", "last_agent")
