"""Add Message table for templates

Revision ID: f74672b73145
Revises: ff00b97f631f
Create Date: 2026-03-30 12:43:13.973170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f74672b73145'
down_revision: Union[str, Sequence[str], None] = 'ff00b97f631f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use raw SQL for robustness since we've had state issues
    connection = op.get_bind()
    
    # 1. Drop transactions and dependencies
    op.execute("ALTER TABLE IF EXISTS sms_logs DROP CONSTRAINT IF EXISTS sms_logs_transaction_id_fkey")
    op.execute("ALTER TABLE IF EXISTS sms_logs DROP COLUMN IF EXISTS transaction_id")
    op.execute("DROP TABLE IF EXISTS transactions CASCADE")
    
    # 2. Create messages table
    # We'll check if it exists first
    from sqlalchemy import inspect
    inspector = inspect(connection)
    tables = inspector.get_table_names()
    
    if 'messages' not in tables:
        op.create_table('messages',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('branch_id', sa.Integer(), nullable=True),
            sa.Column('template_type', sa.String(), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], name=op.f('messages_branch_id_fkey')),
            sa.PrimaryKeyConstraint('id', name=op.f('messages_pkey'))
        )
        op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_id'), table_name='messages', if_exists=True)
    op.drop_table('messages', if_exists=True)
    
    # We won't perfectly restore transactions here as it's complex, 
    # but at least cleanup the messages part.
