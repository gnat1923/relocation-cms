"""empty message

Revision ID: 301f41697cf8
Revises: 101330f831b9
Create Date: 2024-09-18 20:52:48.692661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '301f41697cf8'
down_revision = '101330f831b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('create_date', sa.DateTime(), nullable=False))
        batch_op.create_index(batch_op.f('ix_assignee_create_date'), ['create_date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignee', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_assignee_create_date'))
        batch_op.drop_column('create_date')

    # ### end Alembic commands ###
