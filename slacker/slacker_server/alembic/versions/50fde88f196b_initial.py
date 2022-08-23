""""initial"

Revision ID: 50fde88f196b
Revises:
Create Date: 2021-03-11 09:56:59.027286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50fde88f196b'
down_revision = None
branch_labels = None
depends_on = None

# wasn't able to find max length for ids in slack docs, so picked length to be
# able to create largest index
STRING_SIZE = 160


def upgrade():
    op.create_table(
        'slack_bots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('client_id', sa.String(STRING_SIZE), nullable=False),
        sa.Column('app_id', sa.String(STRING_SIZE), nullable=False),
        sa.Column('enterprise_id', sa.String(STRING_SIZE), nullable=True),
        sa.Column('enterprise_name', sa.String(STRING_SIZE), nullable=True),
        sa.Column('team_id', sa.String(STRING_SIZE), nullable=True),
        sa.Column('team_name', sa.String(STRING_SIZE), nullable=True),
        sa.Column('bot_token', sa.String(STRING_SIZE), nullable=True),
        sa.Column('bot_id', sa.String(STRING_SIZE), nullable=True),
        sa.Column('bot_user_id', sa.String(STRING_SIZE), nullable=True),
        sa.Column('bot_scopes', sa.String(STRING_SIZE), nullable=True),
        sa.Column('is_enterprise_install', sa.Boolean(), nullable=False),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('slack_bots_idx', 'slack_bots',
                    ['client_id', 'enterprise_id', 'team_id', 'installed_at'],
                    unique=False)
    op.create_table(
        'slack_installations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('client_id', sa.String(STRING_SIZE), nullable=False),
        sa.Column('app_id', sa.String(STRING_SIZE), nullable=False),
        sa.Column('enterprise_id', sa.String(STRING_SIZE), nullable=True),
        sa.Column('enterprise_name', sa.String(STRING_SIZE), nullable=True),
        sa.Column('enterprise_url', sa.String(STRING_SIZE), nullable=True),
        sa.Column('team_id', sa.String(STRING_SIZE), nullable=True),
        sa.Column('team_name', sa.String(STRING_SIZE), nullable=True),
        sa.Column('bot_token', sa.String(STRING_SIZE), nullable=True),
        sa.Column('bot_id', sa.String(STRING_SIZE), nullable=True),
        sa.Column('bot_user_id', sa.String(STRING_SIZE), nullable=True),
        sa.Column('bot_scopes', sa.String(STRING_SIZE), nullable=True),
        sa.Column('user_id', sa.String(STRING_SIZE), nullable=False),
        sa.Column('user_token', sa.String(STRING_SIZE), nullable=True),
        sa.Column('user_scopes', sa.String(STRING_SIZE), nullable=True),
        sa.Column('incoming_webhook_url', sa.String(STRING_SIZE),
                  nullable=True),
        sa.Column('incoming_webhook_channel', sa.String(STRING_SIZE),
                  nullable=True),
        sa.Column('incoming_webhook_channel_id', sa.String(STRING_SIZE),
                  nullable=True),
        sa.Column('incoming_webhook_configuration_url', sa.String(STRING_SIZE),
                  nullable=True),
        sa.Column('is_enterprise_install', sa.Boolean(), nullable=False),
        sa.Column('token_type', sa.String(STRING_SIZE), nullable=True),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'slack_installations_idx', 'slack_installations',
        ['client_id', 'enterprise_id', 'team_id', 'user_id', 'installed_at'],
        unique=False)
    op.create_table(
        'slack_oauth_states',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('state', sa.String(STRING_SIZE), nullable=False),
        sa.Column('expire_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('slack_oauth_states')
    op.drop_index('slack_installations_idx', table_name='slack_installations')
    op.drop_table('slack_installations')
    op.drop_index('slack_bots_idx', table_name='slack_bots')
    op.drop_table('slack_bots')
