"""Add email templates table with versioning support

Revision ID: 003
Revises: 002
Create Date: 2025-07-24 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create email_templates table
    op.create_table('email_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('identifier', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier', 'version', name='uq_email_template_identifier_version')
    )
    
    # Create indexes
    op.create_index(op.f('ix_email_templates_id'), 'email_templates', ['id'], unique=False)
    op.create_index(op.f('ix_email_templates_identifier'), 'email_templates', ['identifier'], unique=False)
    op.create_index('ix_email_templates_identifier_active', 'email_templates', ['identifier', 'is_active'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_email_templates_identifier_active', table_name='email_templates')
    op.drop_index(op.f('ix_email_templates_identifier'), table_name='email_templates')
    op.drop_index(op.f('ix_email_templates_id'), table_name='email_templates')
    
    # Drop table
    op.drop_table('email_templates')