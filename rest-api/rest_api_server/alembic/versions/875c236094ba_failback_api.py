""""failback_api"

Revision ID: 875c236094ba
Revises: 7b30bd0800c2
Create Date: 2017-10-20 08:36:13.207982

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = '875c236094ba'
down_revision = '7b30bd0800c2'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    to_dynamic_stmt = "ALTER TABLE `failback` ROW_FORMAT=DYNAMIC;"
    session.execute(to_dynamic_stmt)
    session.close()

    op.add_column('failback', sa.Column('vsphere_credential_id',
                                        sa.String(length=36), nullable=False))
    op.create_foreign_key(
        'failback_ibfk_vscred', 'failback', 'vsphere_credential',
        ['vsphere_credential_id'], ['id'])
    op.alter_column('failback_device', 'esxi_datastore_id',
                    existing_type=sa.String(length=36), nullable=True)
    op.alter_column('failback_device', 'esxi_host_id',
                    existing_type=sa.String(length=36), nullable=True)


def downgrade():
    op.alter_column('failback_device', 'esxi_host_id',
                    existing_type=sa.String(length=36), nullable=True)
    op.alter_column('failback_device', 'esxi_datastore_id',
                    existing_type=sa.String(length=36), nullable=True)
    op.drop_constraint('failback_ibfk_vscred', 'failback', type_='foreignkey')
    op.drop_column('failback', 'vsphere_credential_id')
