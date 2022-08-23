""""failback"

Revision ID: b08a738a829f
Revises: 8862cb9204a8
Create Date: 2017-10-16 09:30:04.055501

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b08a738a829f'
down_revision = '8862cb9204a8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('esxi_datastore',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('vsphere_credential_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('size', sa.BigInteger(), nullable=True),
    sa.Column('free', sa.BigInteger(), nullable=True),
    sa.Column('maintenance_mode', sa.Enum(
        'inMaintenance', 'enteringMaintenance', 'normal'), nullable=False),
    sa.Column('accessible', sa.Boolean(), nullable=True),
    sa.Column('overall_status', sa.Enum('GRAY', 'GREEN', 'RED', 'YELLOW'),
              nullable=False),
    sa.Column('update_time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(
        ['vsphere_credential_id'], ['vsphere_credential.id'], ),
                    sa.PrimaryKeyConstraint('id'))
    op.create_table('esxi_host',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('vsphere_credential_id', sa.String(length=36), nullable=False),
    sa.Column('hostname', sa.String(length=256), nullable=False),
    sa.Column('address', sa.String(length=39), nullable=False),
    sa.Column('update_time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['vsphere_credential_id'],
                            ['vsphere_credential.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('failback',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('customer_id', sa.String(length=36), nullable=False),
    sa.Column('cloudsite_id', sa.String(length=36), nullable=True),
    sa.Column('plan', sa.TEXT(), nullable=False),
    sa.Column('state', sa.Enum('INCOMPLETE', 'IDLE', 'READY', 'RUNNING',
                               'SYNCHRONIZED'), nullable=False),
    sa.Column('update_time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cloudsite_id'], ['cloudsite.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('failback_device',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(length=36),nullable=False),
    sa.Column('device_id', sa.String(length=36), nullable=True),
    sa.Column('failback_id', sa.String(length=36), nullable=False),
    sa.Column('esxi_host_id', sa.String(length=36), nullable=False),
    sa.Column('esxi_datastore_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('hardware', sa.TEXT(), nullable=False),
    sa.Column('sync_status', sa.TEXT(), nullable=True),
    sa.Column('update_time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['device.id'], ),
    sa.ForeignKeyConstraint(['esxi_datastore_id'], ['esxi_datastore.id'], ),
    sa.ForeignKeyConstraint(['esxi_host_id'], ['esxi_host.id'], ),
    sa.ForeignKeyConstraint(['failback_id'], ['failback.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('failback_snapshot',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('drive_id', sa.String(length=36), nullable=False),
    sa.Column('snapshot_id', sa.String(length=36), nullable=True),
    sa.Column('type', sa.Enum('BACKUP', 'FATCOW'), nullable=False),
    sa.Column('generation', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['drive_id'], ['drive.id'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('agent', sa.Column(
        'last_seen', sa.Integer(), nullable=False))
    op.add_column('drive', sa.Column('endpoint', sa.TEXT(), nullable=True))


def downgrade():
    op.drop_column('drive', 'endpoint')
    op.drop_column('agent', 'last_seen')
    op.drop_table('failback_snapshot')
    op.drop_table('failback_device')
    op.drop_table('failback')
    op.drop_table('esxi_host')
    op.drop_table('esxi_datastore')
