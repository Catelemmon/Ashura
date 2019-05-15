"""update convert table

Revision ID: 1894200c814f
Revises: f58a91543535
Create Date: 2019-05-15 15:43:07.563558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1894200c814f'
down_revision = 'f58a91543535'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('convert',
                    sa.Column('convert_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('origin_file', sa.String(length=200), nullable=False),
                    sa.Column('des_file', sa.String(length=200), nullable=True),
                    sa.Column('vf_file', sa.String(length=200), nullable=False),
                    sa.Column('convert_type', sa.Integer(), nullable=False),
                    sa.Column('convert_status', sa.Integer(), nullable=False),
                    sa.Column('convert_infos', sa.JSON, nullable=True),
                    sa.Column('begin_time', sa.DateTime(), nullable=True),
                    sa.Column('end_time', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('convert_id')
                    )


def downgrade():
    pass
