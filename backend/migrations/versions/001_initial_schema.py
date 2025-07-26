"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create your initial tables here
    # Example:
    # op.create_table('example',
    #     sa.Column('id', sa.String(), nullable=False),
    #     sa.Column('created_at', sa.DateTime(), nullable=False),
    #     sa.Column('updated_at', sa.DateTime(), nullable=False),
    #     sa.PrimaryKeyConstraint('id')
    # )
    pass


def downgrade() -> None:
    # Drop your tables here
    # Example:
    # op.drop_table('example')
    pass