"""baseline schema

Revision ID: 0001
Revises: 
Create Date: 2026-10-24 14:26:37.436156
"""
from alembic import op
import sqlalchemy as sa


revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('bots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('default_language', sa.String(length=5), nullable=False),
    sa.Column('welcome_message', sa.Text(), nullable=False),
    sa.Column('fallback_message', sa.Text(), nullable=False),
    sa.Column('support_contact', sa.String(length=200), nullable=False),
    sa.Column('working_status', sa.String(length=20), nullable=False),
    sa.Column('maintenance_mode', sa.Boolean(), nullable=False),
    sa.Column('system_prompt', sa.Text(), nullable=False),
    sa.Column('ai_model', sa.String(length=100), nullable=False),
    sa.Column('ai_temperature', sa.Float(), nullable=False),
    sa.Column('ai_max_length', sa.Integer(), nullable=False),
    sa.Column('response_style', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('faqs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('keywords', sa.Text(), nullable=False),
    sa.Column('language', sa.String(length=5), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('log_type', sa.String(length=20), nullable=False),
    sa.Column('actor', sa.String(length=100), nullable=False),
    sa.Column('action', sa.String(length=200), nullable=False),
    sa.Column('record_id', sa.Integer(), nullable=True),
    sa.Column('details', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('permissions', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('telegram_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('full_name', sa.String(length=200), nullable=False),
    sa.Column('language', sa.String(length=5), nullable=False),
    sa.Column('first_interaction_at', sa.DateTime(), nullable=False),
    sa.Column('last_interaction_at', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('telegram_users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_telegram_users_telegram_user_id'), ['telegram_user_id'], unique=True)

    op.create_table('unknown_questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('frequency', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('last_asked_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('question')
    )
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('commands',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.Column('response', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('permission', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('intents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('response', sa.Text(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('agents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=False),
    sa.Column('availability', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('admin_id')
    )
    op.create_table('broadcasts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('audience', sa.String(length=20), nullable=False),
    sa.Column('scheduled_at', sa.DateTime(), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('delivery_result', sa.JSON(), nullable=False),
    sa.Column('sent_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
    sa.ForeignKeyConstraint(['sent_by'], ['admins.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('knowledge_articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('keywords', sa.Text(), nullable=False),
    sa.Column('language', sa.String(length=5), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['admins.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('training_phrases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('intent_id', sa.Integer(), nullable=False),
    sa.Column('phrase', sa.Text(), nullable=False),
    sa.Column('language', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['intent_id'], ['intents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('conversations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('last_message_at', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('intent', sa.String(length=100), nullable=True),
    sa.Column('assigned_agent_id', sa.Integer(), nullable=True),
    sa.Column('support_status', sa.String(length=20), nullable=True),
    sa.Column('resolution_status', sa.String(length=20), nullable=False),
    sa.Column('session_step', sa.String(length=50), nullable=True),
    sa.Column('context', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['assigned_agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['telegram_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_conversations_user_id'), ['user_id'], unique=False)

    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('broadcast_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=30), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('delivery_status', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['broadcast_id'], ['broadcasts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['telegram_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('direction', sa.String(length=10), nullable=False),
    sa.Column('message_type', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('response_source', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['telegram_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_messages_conversation_id'), ['conversation_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_messages_user_id'), ['user_id'], unique=False)

    op.create_table('feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.Column('conversation_id', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['telegram_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('feedback')
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_messages_user_id'))
        batch_op.drop_index(batch_op.f('ix_messages_conversation_id'))

    op.drop_table('messages')
    op.drop_table('notifications')
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_conversations_user_id'))

    op.drop_table('conversations')
    op.drop_table('training_phrases')
    op.drop_table('knowledge_articles')
    op.drop_table('broadcasts')
    op.drop_table('agents')
    op.drop_table('intents')
    op.drop_table('commands')
    op.drop_table('admins')
    op.drop_table('unknown_questions')
    with op.batch_alter_table('telegram_users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_telegram_users_telegram_user_id'))

    op.drop_table('telegram_users')
    op.drop_table('roles')
    op.drop_table('logs')
    op.drop_table('faqs')
    op.drop_table('bots')
