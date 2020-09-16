"""empty message

Revision ID: d0758c39fb0f
Revises: 4e5cc63464e4
Create Date: 2020-09-16 15:13:15.351661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0758c39fb0f'
down_revision = '4e5cc63464e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('available_from', sa.DateTime(), nullable=True))
    op.add_column('Artist', sa.Column('available_to', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'available_to')
    op.drop_column('Artist', 'available_from')
    # ### end Alembic commands ###
