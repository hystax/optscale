""""fix_inconsistency"

Revision ID: 8f454f913981
Revises: e8a9705b210d
Create Date: 2017-10-10 11:26:09.773177

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8f454f913981'
down_revision = 'e8a9705b210d'
branch_labels = None
depends_on = None


def upgrade():
    """
    Fixed database inconsistency
    :return:
    """
    op.alter_column('cloudsite', 'remove_project', existing_type=sa.Boolean(),
                    nullable=True)
    op.alter_column(
        'cloudsite', 'state', existing_type=sa.Enum(
            'PENDING', 'CREATING', 'UPDATING', 'DELETING', 'RUNNING',
            'ROLLING_BACK', 'ERROR'), nullable=True,
        existing_server_default=sa.text("'PENDING'"))
    op.create_unique_constraint('uc_cstmr_name_del', 'drplan',
                                ['customer_id', 'name', 'deleted_at'])
    op.drop_index('uc_cstmr_name_del_at', table_name='drplan')
    op.alter_column('ssh_key', 'ssh_key', existing_type=sa.TEXT(),
                    nullable=True)


def downgrade():
    op.alter_column('ssh_key', 'ssh_key', existing_type=sa.TEXT(),
                    nullable=False)
    op.create_index('uc_cstmr_name_del_at', 'drplan', [
        'customer_id', 'name', 'deleted_at'], unique=True)
    op.drop_constraint('uc_cstmr_name_del', 'drplan', type_='unique')
    op.alter_column('cloudsite', 'state',
                    existing_type=sa.Enum(
                        'PENDING', 'CREATING', 'UPDATING', 'DELETING',
                        'RUNNING', 'ROLLING_BACK', 'ERROR'), nullable=False,
                    existing_server_default=sa.text("'PENDING'"))
    op.alter_column('cloudsite', 'remove_project',
                    existing_type=sa.Boolean(), nullable=False)
