"""added 'active' to packages'

Revision ID: e2a0139cb6ef
Revises: b44049159cf9
Create Date: 2024-09-30 21:54:21.871525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2a0139cb6ef'
down_revision = 'b44049159cf9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('package', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('package', schema=None) as batch_op:
        batch_op.drop_column('active')

    # ### end Alembic commands ###
