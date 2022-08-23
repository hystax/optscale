""""vmware_creds_to_clouds"

Revision ID: baa9439f17b2
Revises: 7611a658f311
Create Date: 2019-10-21 17:09:05.719564

"""
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy import and_

# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = 'baa9439f17b2'
down_revision = '7611a658f311'
branch_labels = None
depends_on = None


CRED_TABLE = sa.table(
    "vsphere_credential",
    sa.Column('id', sa.String(36)),
    sa.Column('name', sa.String(256)),
    sa.Column('customer_id', sa.String(36)),
    sa.Column('description', sa.TEXT()),
    sa.Column('endpoint', sa.String(256)),
    sa.Column('username', sa.String(256)),
    sa.Column('password', sa.LargeBinary()),
    sa.Column('salt', sa.String(36)),
    sa.Column('deleted_at', sa.Integer()),
)
CLOUD_TABLE = sa.table(
    'cloud',
    sa.Column('id', sa.String(36)),
    sa.Column('deleted_at', sa.Integer),
    sa.Column('type', sa.Enum('OPENSTACK', 'OPENSTACK_CNR',
                              'OPENSTACK_HUAWEI_CNR', 'AWS_CNR',
                              'ALIBABA_CNR', 'VMWARE_CNR', 'AZURE_CNR',
                              'FAKE')),
    sa.Column('name', sa.String(256)),
    sa.Column('endpoint', sa.String(256)),
    sa.Column('username', sa.String(256)),
    sa.Column('password', sa.String(256)),
    sa.Column('salt', sa.String(36)),
    sa.Column('extra_args', sa.TEXT),
    sa.Column('default', sa.Boolean),
    sa.Column('managed', sa.Boolean),
    sa.Column('customer_id', sa.String(36)),
    sa.Column('partner_id', sa.String(36)),
)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        clouds = []
        for row in session.execute(CRED_TABLE.select()):
            clouds.append({
                'id': row['id'],
                'deleted_at': row['deleted_at'],
                'type': 'VMWARE_CNR',
                'name': row['name'],
                'endpoint': row['endpoint'],
                'username': row['username'],
                'password': row['password'],
                'salt': row['salt'],
                'extra_args': json.dumps({'description': row['description']}),
                'default': False,
                'managed': False,
                'customer_id': row['customer_id'],
                'partner_id': None,
            })

        op.bulk_insert(CLOUD_TABLE, clouds)

        def update_cloud_id(table_name):
            table = sa.table(table_name,
                             sa.Column('id', sa.String(36)),
                             sa.Column('vsphere_credential_id', sa.String(36)),
                             sa.Column('cloud_id', sa.String(36)))

            for row in session.execute(table.select()):
                session.execute(sa.update(table).values(
                    cloud_id=row['vsphere_credential_id']).where(
                    table.c.id == row['id']))

        op.add_column('cloud_agent',
                      sa.Column('cloud_id', sa.String(36), nullable=True))
        op.drop_constraint('cloud_agent_ibfk_vsphere_credential',
                           'cloud_agent', type_='foreignkey')
        update_cloud_id('cloud_agent')
        op.create_foreign_key('cloud_agent_cloud_fk', 'cloud_agent', 'cloud',
                              ['cloud_id'], ['id'])

        op.add_column('esxi_datastore',
                      sa.Column('cloud_id', sa.String(36), nullable=False))
        op.drop_constraint('esxi_datastore_ibfk_1', 'esxi_datastore',
                           type_='foreignkey')
        update_cloud_id('esxi_datastore')
        op.create_foreign_key('datastore_cloud_fk', 'esxi_datastore', 'cloud',
                              ['cloud_id'], ['id'])

        op.add_column('esxi_host',
                      sa.Column('cloud_id', sa.String(36), nullable=False))
        op.drop_constraint('esxi_host_ibfk_1', 'esxi_host', type_='foreignkey')
        update_cloud_id('esxi_host')
        op.create_foreign_key('host_cloud_fk', 'esxi_host', 'cloud',
                              ['cloud_id'], ['id'])

        op.add_column('failback',
                      sa.Column('cloud_id', sa.String(36), nullable=True))
        op.drop_constraint('failback_ibfk_vscred', 'failback',
                           type_='foreignkey')
        update_cloud_id('failback')
        op.create_foreign_key('failback_cloud_fk', 'failback', 'cloud',
                              ['cloud_id'], ['id'])

        op.drop_column('cloud_agent', 'vsphere_credential_id')
        op.drop_column('esxi_datastore', 'vsphere_credential_id')
        op.drop_column('esxi_host', 'vsphere_credential_id')
        op.drop_column('failback', 'vsphere_credential_id')
        op.drop_table('vsphere_credential')
        session.commit()
    finally:
        session.close()


def downgrade():
    op.create_table('vsphere_credential',
                    sa.Column('id', sa.String(36), nullable=False),
                    sa.Column('name', sa.String(256), nullable=False),
                    sa.Column('customer_id', sa.String(36), nullable=True),
                    sa.Column('description', sa.TEXT(), nullable=True),
                    sa.Column('endpoint', sa.String(256), nullable=False),
                    sa.Column('username', sa.String(256), nullable=False),
                    sa.Column('password', sa.LargeBinary(), nullable=False),
                    sa.Column('salt', sa.String(36), nullable=False),
                    sa.Column('deleted_at', sa.Integer(), autoincrement=False,
                              nullable=False),
                    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'],
                                            name='vsphere_credential_ibfk_1'),
                    sa.PrimaryKeyConstraint('id'))

    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        creds = []
        for row in session.execute(CLOUD_TABLE.select().where(
                CLOUD_TABLE.c.type == 'VMWARE_CNR')):
            creds.append({
                'id': row['id'],
                'deleted_at': row['deleted_at'],
                'name': row['name'],
                'endpoint': row['endpoint'],
                'username': row['username'],
                'password': row['password'],
                'salt': row['salt'],
                'description': json.loads(row['extra_args']).get('description'),
                'customer_id': row['customer_id'],
            })

        op.bulk_insert(CRED_TABLE, creds)

        def update_cred_id(table_name):
            table = sa.table(table_name,
                             sa.Column('id', sa.String(36)),
                             sa.Column('vsphere_credential_id', sa.String(36)),
                             sa.Column('cloud_id', sa.String(36)))

            for row in session.execute(table.select()):
                session.execute(sa.update(table).values(
                    vsphere_credential_id=row['cloud_id']).where(
                    table.c.id == row['id']))

        op.add_column('failback',
                      sa.Column('vsphere_credential_id', sa.String(36),
                                nullable=True))
        op.drop_constraint('failback_cloud_fk', 'failback', type_='foreignkey')
        update_cred_id('failback')
        op.create_foreign_key(
            'failback_ibfk_vscred', 'failback', 'vsphere_credential',
            ['vsphere_credential_id'], ['id'])

        op.add_column('esxi_host', sa.Column('vsphere_credential_id',
                                             sa.String(36), nullable=False))
        op.drop_constraint('host_cloud_fk', 'esxi_host', type_='foreignkey')
        update_cred_id('esxi_host')
        op.create_foreign_key('esxi_host_ibfk_1', 'esxi_host', 'vsphere_credential',
                              ['vsphere_credential_id'], ['id'])

        op.add_column('esxi_datastore', sa.Column('vsphere_credential_id',
                                                  sa.String(36), nullable=False))
        op.drop_constraint('datastore_cloud_fk', 'esxi_datastore',
                           type_='foreignkey')
        update_cred_id('esxi_datastore')
        op.create_foreign_key('esxi_datastore_ibfk_1', 'esxi_datastore', 'vsphere_credential',
                              ['vsphere_credential_id'], ['id'])

        op.add_column('cloud_agent', sa.Column('vsphere_credential_id',
                                               sa.String(36), nullable=True))
        op.drop_constraint(
            'cloud_agent_cloud_fk', 'cloud_agent', type_='foreignkey')
        update_cred_id('cloud_agent')
        op.create_foreign_key(
            'cloud_agent_ibfk_vsphere_credential', 'cloud_agent',
            'vsphere_credential', ['vsphere_credential_id'], ['id'])

        session.execute(CLOUD_TABLE.delete().where(
            CLOUD_TABLE.c.id.in_([cred['id'] for cred in creds])))
        session.commit()
    finally:
        session.close()

    op.drop_column('failback', 'cloud_id')
    op.drop_column('esxi_host', 'cloud_id')
    op.drop_column('esxi_datastore', 'cloud_id')
    op.drop_column('cloud_agent', 'cloud_id')
