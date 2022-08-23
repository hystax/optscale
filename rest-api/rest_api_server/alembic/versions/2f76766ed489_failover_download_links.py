""""failover_download_links"

Revision ID: 2f76766ed489
Revises: 21c11090f310
Create Date: 2019-08-28 14:04:45.585686

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '2f76766ed489'
down_revision = '21c11090f310'
branch_labels = None
depends_on = None

fb_states = sa.Enum('INCOMPLETE', 'IDLE', 'READY', 'RUNNING',
                    'SYNCHRONIZED', 'ERROR', 'CANCEL', 'CANCELLED',
                    'CANCELLING', 'PREPARING')
old_cs_types = sa.Enum('CLOUD_SITE', 'DUMMY_SITE', 'DUMMY_FAILBACK')
new_cs_types = sa.Enum('CLOUD_SITE', 'DUMMY_SITE', 'DUMMY_FAILBACK',
                       'DUMMY_FAILOVER')


def upgrade():
    fb_table = table('failback', column('state', fb_states))
    op.execute(
        fb_table.update().where(fb_table.c.state.is_(None)).values(
            state='ERROR'))
    op.alter_column('failback', 'state',
                    existing_type=fb_states, nullable=False)
    op.alter_column(
        'cloudsite', 'cs_type', existing_type=new_cs_types, nullable=False,
        existing_server_default=sa.text("'CLOUD_SITE'"))


def downgrade():
    op.alter_column('failback', 'state',
                    existing_type=fb_states, nullable=True)
    ct = sa.sql.table('cloudsite', sa.sql.column('cs_type', new_cs_types))
    op.execute(ct.update().where(ct.c.cs_type.in_(
        ['DUMMY_FAILOVER'])).values(cs_type='DUMMY_SITE'))
    op.alter_column(
        'cloudsite', 'cs_type', existing_type=old_cs_types, nullable=False,
        existing_server_default=sa.text("'CLOUD_SITE'"))
