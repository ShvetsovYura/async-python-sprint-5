"""initial-db

Revision ID: 269ac2d3dc27
Revises: Sh
Create Date: 2022-12-04 00:42:44.154288

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '269ac2d3dc27'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users', sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=True),
                    sa.Column('hashed_password', sa.String(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('id'))
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=True)

    op.create_table('files', sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('subpath', sa.String(length=100), nullable=True),
                    sa.Column('size', sa.Integer(), nullable=True),
                    sa.Column('is_downloadable', sa.Boolean(), nullable=True),
                    sa.Column('author', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['author'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name', 'subpath', name='uix_subpaths'))
    op.create_index(op.f('ix_files_created_at'), 'files', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_files_created_at'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_table('users')
