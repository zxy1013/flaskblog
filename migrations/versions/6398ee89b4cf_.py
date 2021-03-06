"""empty message

Revision ID: 6398ee89b4cf
Revises: 250952c6c315
Create Date: 2021-03-23 17:08:50.240602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6398ee89b4cf'
down_revision = '250952c6c315'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('photo',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('photo_name', sa.String(length=50), nullable=False),
    sa.Column('photo_datetime', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('photo')
    # ### end Alembic commands ###
