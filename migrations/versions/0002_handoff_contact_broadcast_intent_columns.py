"""handoff, contact, broadcast and intent entity columns

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-24 14:26:55.851994
"""
from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('broadcasts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('target_user_ids', sa.JSON(), server_default='[]', nullable=False))
        batch_op.add_column(sa.Column('status', sa.String(length=20), server_default='draft', nullable=False))

    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('handoff_requested_at', sa.DateTime(), nullable=True))

    with op.batch_alter_table('intents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('entities', sa.JSON(), server_default='[]', nullable=False))

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('agent_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_messages_agent_id_agents', 'agents', ['agent_id'], ['id'])

    with op.batch_alter_table('telegram_users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(length=200), nullable=True))



def downgrade() -> None:
    with op.batch_alter_table('telegram_users', schema=None) as batch_op:
        batch_op.drop_column('email')
        batch_op.drop_column('phone')

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_constraint('fk_messages_agent_id_agents', type_='foreignkey')
        batch_op.drop_column('agent_id')

    with op.batch_alter_table('intents', schema=None) as batch_op:
        batch_op.drop_column('entities')

    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.drop_column('handoff_requested_at')

    with op.batch_alter_table('broadcasts', schema=None) as batch_op:
        batch_op.drop_column('status')
        batch_op.drop_column('target_user_ids')

