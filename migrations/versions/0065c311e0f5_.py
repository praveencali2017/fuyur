"""empty message

Revision ID: 0065c311e0f5
Revises: 
Create Date: 2020-09-17 21:12:19.570479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0065c311e0f5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('available_from', sa.DateTime(), nullable=True))
    op.add_column('artists', sa.Column('available_to', sa.DateTime(), nullable=True))
    op.add_column('artists', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('artists', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('artists', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('venues', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('venues', sa.Column('genres', sa.String(length=120), nullable=True))
    op.add_column('venues', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venues', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'website')
    op.drop_column('venues', 'seeking_talent')
    op.drop_column('venues', 'seeking_description')
    op.drop_column('venues', 'genres')
    op.drop_column('venues', 'created_at')
    op.drop_column('artists', 'website')
    op.drop_column('artists', 'seeking_description')
    op.drop_column('artists', 'created_at')
    op.drop_column('artists', 'available_to')
    op.drop_column('artists', 'available_from')
    # ### end Alembic commands ###
