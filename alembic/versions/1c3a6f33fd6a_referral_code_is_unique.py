"""referral code is unique

Revision ID: 1c3a6f33fd6a
Revises: d074c00eeeff
Create Date: 2025-01-28 19:58:40.937871

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1c3a6f33fd6a"
down_revision: Union[str, None] = "d074c00eeeff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_referrals_referral_code", table_name="referrals")
    op.create_index(
        op.f("ix_referrals_referral_code"), "referrals", ["referral_code"], unique=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_referrals_referral_code"), table_name="referrals")
    op.create_index(
        "ix_referrals_referral_code", "referrals", ["referral_code"], unique=False
    )
    # ### end Alembic commands ###
