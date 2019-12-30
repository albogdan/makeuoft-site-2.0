"""empty message

Revision ID: 01fab3a7cf0f
Revises: f5b12ea5a02c
Create Date: 2019-12-29 18:40:25.285140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01fab3a7cf0f'
down_revision = 'f5b12ea5a02c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('password_resets', 'token',
               existing_type=sa.VARCHAR(length=32),
               type_=sa.String(length=255),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('password_resets', 'token',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=32),
               existing_nullable=False)
    # ### end Alembic commands ###