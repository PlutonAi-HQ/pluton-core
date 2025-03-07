"""add referral

Revision ID: d074c00eeeff
Revises: 38bbe2f7c972
Create Date: 2025-01-28 10:48:55.632668

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d074c00eeeff"
down_revision: Union[str, None] = "38bbe2f7c972"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "referrals",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("owner_id", sa.String(), nullable=True),
        sa.Column("referral_code", sa.String(), nullable=True),
        sa.Column(
            "referred_user_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id"),
    )
    op.create_index(op.f("ix_referrals_id"), "referrals", ["id"], unique=False)
    op.create_index(
        op.f("ix_referrals_referral_code"), "referrals", ["referral_code"], unique=False
    )
    op.add_column("users", sa.Column("used_ref_code", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "used_ref_code")
    op.drop_index(op.f("ix_referrals_referral_code"), table_name="referrals")
    op.drop_index(op.f("ix_referrals_id"), table_name="referrals")
    op.drop_table("referrals")
    # ### end Alembic commands ###
