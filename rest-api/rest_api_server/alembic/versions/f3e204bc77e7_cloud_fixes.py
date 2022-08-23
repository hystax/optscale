""""cloud_fixes"

Revision ID: f3e204bc77e7
Revises: 430da541e0be
Create Date: 2018-05-16 08:39:08.109154

"""
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import (update, String, select, Integer, LargeBinary, insert,
                        func)
from cryptography.fernet import Fernet
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f3e204bc77e7'
down_revision = '430da541e0be'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('cloud_volume', 'cloud_agent_id',
                    existing_type=sa.String(36), nullable=True)
    op.add_column('mountpoint', sa.Column('is_cnr', sa.Boolean(),
                                          nullable=False, default=False))


def _encrypt_password(password, salt):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    return fernet.encrypt((password + salt).encode())


def downgrade():
    op.drop_column('mountpoint', 'is_cnr')

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_volume_table = table('cloud_volume',
                                   column('cloud_agent_id', String(20)),
                                   column('id', String(36)))
        sql = select([func.count()]).select_from(cloud_volume_table).where(
            cloud_volume_table.c.cloud_agent_id.is_(None))
        invalid_volumes_count = session.execute(sql).scalar()
        if invalid_volumes_count > 0:
            cloud_table = table('cloud',
                                column('deleted_at', Integer),
                                column('id', String(36)),
                                column('type', String(256)),
                                column('name', String(256)),
                                column('endpoint', String(256)),
                                column('password', LargeBinary),
                                column('salt', String(36)),
                                column('extra_args', Integer),
                                column('default', Integer))

            password = 'my-migration-pass'
            salt = str(uuid.uuid4())
            password = _encrypt_password(password, salt)
            cloud_id = str(uuid.uuid4())
            ins_stmt = insert(cloud_table).values(
                deleted_at=1,
                id=cloud_id,
                type='OPENSTACK',
                name='Migration fix',
                endpoint='127.0.0.1',
                password=password,
                salt=salt,
                extra_args='',
                default=0)
            session.execute(ins_stmt)
            cloud_agent_table = table('cloud_agent',
                                      column('deleted_at', Integer),
                                      column('id', String(36)),
                                      column('cloud_id', String(36)),
                                      column('api_url', String(256)),
                                      column('iscsi_address', String(256)))
            cloud_agent_id = str(uuid.uuid4())
            ins_stmt = insert(cloud_agent_table).values(
                deleted_at=1,
                id=cloud_agent_id,
                cloud_id=cloud_id,
                api_url='',
                iscsi_address='')
            session.execute(ins_stmt)
            upd_stmt = update(cloud_volume_table).values(
                cloud_agent_id=cloud_agent_id).where(
                cloud_volume_table.c.cloud_agent_id.is_(None))
            session.execute(upd_stmt)
            session.commit()
    finally:
        session.close()
    op.drop_constraint('cloud_volume_ibfk_1', 'cloud_volume', type_='foreignkey')
    op.alter_column('cloud_volume', 'cloud_agent_id',
                    existing_type=sa.String(36), nullable=False)
    op.create_foreign_key('cloud_volume_ibfk_1', 'cloud_volume', 'cloud_agent',
                          ['cloud_agent_id'], ['id'])
    # ### end Alembic commands ###
