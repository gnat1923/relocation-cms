"""empty message

Revision ID: 492e1e458938
Revises: 088d905213ae
Create Date: 2024-10-05 17:27:08.423789

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '492e1e458938'
down_revision = '088d905213ae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nationality', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('booking_date', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('arrival_date', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('work_start_date', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('temp_flat', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('spouse', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('child', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('pets', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('hub', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('hr_contact', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('job_title', sa.String(length=200), nullable=True))
        batch_op.create_index(batch_op.f('ix_assignee_nationality'), ['nationality'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignee', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_assignee_nationality'))
        batch_op.drop_column('job_title')
        batch_op.drop_column('hr_contact')
        batch_op.drop_column('hub')
        batch_op.drop_column('pets')
        batch_op.drop_column('child')
        batch_op.drop_column('spouse')
        batch_op.drop_column('temp_flat')
        batch_op.drop_column('work_start_date')
        batch_op.drop_column('arrival_date')
        batch_op.drop_column('booking_date')
        batch_op.drop_column('nationality')

    # ### end Alembic commands ###
