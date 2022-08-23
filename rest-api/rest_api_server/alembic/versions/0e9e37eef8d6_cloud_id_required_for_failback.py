""""cloud_id_required_for_failback"

Revision ID: 0e9e37eef8d6
Revises: b2b5f61c00be
Create Date: 2019-12-04 17:22:47.025116

"""
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy import and_, or_, bindparam

# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '0e9e37eef8d6'
down_revision = 'b2b5f61c00be'
branch_labels = None
depends_on = None


cloud_table = sa.table("cloud",
                           sa.column('id', sa.String(36)),
                           sa.column('type', sa.Enum(
                               'openstack', 'openstack_cnr',
                               'openstack_huawei_cnr', 'aws_cnr',
                               'alibaba_cnr', 'vmware_cnr', 'azure_cnr',
                               'fake'
                           )),
                           sa.column('extra_args', sa.TEXT),
                           sa.column('managed', sa.Boolean))

failback_table = sa.table('failback',
                              sa.column('id', sa.String(36)),
                              sa.column('type', sa.Enum(
                                  'openstack', 'huawei', 'vmware')),
                              sa.column('cloud_id', sa.String(36)),
                              sa.column('project_id', sa.String(36)))


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        unmanaged_clouds_q = sa.select([cloud_table]).where(
            and_(
                or_(cloud_table.c.type == 'openstack_cnr',
                    cloud_table.c.type == 'openstack_huawei_cnr'),
                cloud_table.c.managed.is_(sa.false()))
        )

        unmanaged_clouds = {
            json.loads(c['extra_args']).get('project_id'): c['id']
            for c in session.execute(unmanaged_clouds_q)
        }

        failbacks_q = sa.select([failback_table]).where(
            and_(failback_table.c.type != 'vmware',
                 failback_table.c.cloud_id.is_(None))
        )

        fb_updates = []
        for fb_row in session.execute(failbacks_q):
            fb_updates.append({'_id': fb_row['id'],
                               'cloud_id': unmanaged_clouds[fb_row['project_id']]})

        fb_update_q = sa.update(failback_table).where(
            failback_table.c.id == bindparam('_id')
        ).values(cloud_id=bindparam('cloud_id'))

        if fb_updates:
            session.execute(fb_update_q, fb_updates)
        session.commit()
    finally:
        session.close()

    op.drop_constraint('failback_cloud_fk', 'failback', type_='foreignkey')
    op.alter_column('failback', 'cloud_id', existing_type=sa.String(36),
                    existing_nullable=True, nullable=False)
    op.create_foreign_key('failback_cloud_fk', 'failback', 'cloud',
                          ['cloud_id'], ['id'])


def downgrade():
    op.alter_column('failback', 'cloud_id', existing_type=sa.String(36),
                    existing_nullable=False, nullable=True)

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(sa.update(failback_table).where(
            failback_table.c.type != 'vmware'
        ).values(cloud_id=None))
        session.commit()
    finally:
        session.close()
