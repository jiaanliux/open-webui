"""Add token usage tables

Revision ID: 999_add_token_usage_tables
Revises: 3781e22e8b01_update_message_table
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '999_add_token_usage_tables'
down_revision = '3781e22e8b01_update_message_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create token_usage table
    op.create_table('token_usage',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('chat_id', sa.String(), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True, default=0),
        sa.Column('completion_tokens', sa.Integer(), nullable=True, default=0),
        sa.Column('total_tokens', sa.Integer(), nullable=True, default=0),
        sa.Column('request_type', sa.String(), nullable=True),
        sa.Column('cost', sa.String(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_token_limits table
    op.create_table('user_token_limits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('daily_token_limit', sa.BigInteger(), nullable=True),
        sa.Column('monthly_token_limit', sa.BigInteger(), nullable=True),
        sa.Column('total_token_limit', sa.BigInteger(), nullable=True),
        sa.Column('daily_tokens_used', sa.BigInteger(), nullable=True, default=0),
        sa.Column('monthly_tokens_used', sa.BigInteger(), nullable=True, default=0),
        sa.Column('total_tokens_used', sa.BigInteger(), nullable=True, default=0),
        sa.Column('last_daily_reset', sa.BigInteger(), nullable=True),
        sa.Column('last_monthly_reset', sa.BigInteger(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('notify_at_percentage', sa.Integer(), nullable=True, default=80),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create indexes for better performance
    op.create_index('ix_token_usage_user_id', 'token_usage', ['user_id'])
    op.create_index('ix_token_usage_created_at', 'token_usage', ['created_at'])
    op.create_index('ix_user_token_limits_user_id', 'user_token_limits', ['user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_user_token_limits_user_id', table_name='user_token_limits')
    op.drop_index('ix_token_usage_created_at', table_name='token_usage')
    op.drop_index('ix_token_usage_user_id', table_name='token_usage')
    
    # Drop tables
    op.drop_table('user_token_limits')
    op.drop_table('token_usage') 