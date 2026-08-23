"""use clock_timestamp for evaluation created_at tie-break

Revision ID: 1a0e63a1620a
Revises: 1912016ddf95
Create Date: 2026-08-23 12:25:22.268879

Hand-written: Alembic's autogenerate doesn't diff server_default SQL
expressions, so it produced an empty migration for this change.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1a0e63a1620a'
down_revision: Union[str, None] = '1912016ddf95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "evaluations",
        "created_at",
        server_default=sa.text("clock_timestamp()"),
    )


def downgrade() -> None:
    op.alter_column(
        "evaluations",
        "created_at",
        server_default=sa.text("now()"),
    )
