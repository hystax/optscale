""""removed_sites"

Revision ID: 6b5edd98bcef
Revises: 61039ec12750
Create Date: 2017-04-07 08:03:58.218721

"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import table, column
from sqlalchemy import select, String, join, update

# revision identifiers, used by Alembic.
revision = '6b5edd98bcef'
down_revision = '6f22d2753056'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # customer-site-group to customer-group
    op.add_column('group', sa.Column('customer_id', sa.String(length=36),
                                     nullable=True))
    op.drop_constraint('group_ibfk_1', 'group', type_='foreignkey')
    op.create_foreign_key(None, 'group', 'customer',
                          ['customer_id'], ['id'])
    try:
        group_table_join_part = table('group',
                                      column('site_id', String(36)),
                                      column('id', String(36)))
        site_table_join_part = table('site',
                                     column('customer_id', String(36)),
                                     column('id', String(36)))

        j = join(group_table_join_part, site_table_join_part,
                 group_table_join_part.c.site_id == site_table_join_part.c.id)
        stmt = select([group_table_join_part.c.id,
                       site_table_join_part.c.customer_id]).select_from(j)

        group_table = table('group',
                            column('customer_id', String(36)),
                            column('id', String(36)))
        for entry in session.execute(stmt):
            upd_stmt = update(group_table).values(
                customer_id=entry['customer_id']).where(
                group_table.c.id == entry['id'])
            session.execute(upd_stmt)

        session.commit()
    finally:
        session.close()

    # customer\
    # group-agent-device to group-device
    op.add_column('device',
                  sa.Column('group_id', sa.String(length=36), nullable=True))
    op.drop_constraint('device_ibfk_1', 'device', type_='foreignkey')
    op.drop_constraint('device_ibfk_2', 'device', type_='foreignkey')
    op.create_foreign_key(None, 'device', 'group', ['group_id'], ['id'])
    try:
        device_table_join_part = table('device',
                                       column('agent_id', String(36)),
                                       column('id', String(36)))
        agent_table_join_part = table('agent',
                                      column('group_id', String(36)),
                                      column('id', String(36)))
        j = join(
            device_table_join_part, agent_table_join_part,
            device_table_join_part.c.agent_id == agent_table_join_part.c.id)
        stmt = select([device_table_join_part.c.id,
                       agent_table_join_part.c.group_id]).select_from(j)

        device_table = table('device',
                             column('group_id', String(36)),
                             column('id', String(36)))
        for entry in session.execute(stmt):
            upd_stmt = update(device_table).values(
                group_id=entry['group_id']).where(
                device_table.c.id == entry['id'])
            session.execute(upd_stmt)
        session.commit()
    finally:
        session.close()

    op.drop_column('device', 'customer_id')
    op.drop_column('device', 'agent_id')

    # agent-customer
    op.add_column('agent', sa.Column('customer_id', sa.String(length=36),
                                     nullable=True))
    op.drop_constraint('agent_ibfk_1', 'agent', type_='foreignkey')
    op.create_foreign_key(None, 'agent', 'customer',
                          ['customer_id'], ['id'])
    try:
        agent_table_join_part = table('agent',
                                      column('group_id', String(36)),
                                      column('id', String(36)))
        group_table_join_part = table('group',
                                      column('site_id', String(36)),
                                      column('id', String(36)))
        site_table_join_part = table('site',
                                     column('customer_id', String(36)),
                                     column('id', String(36)))

        j = join(
            group_table_join_part, agent_table_join_part,
            group_table_join_part.c.id == agent_table_join_part.c.group_id
        ).join(
            site_table_join_part,
            site_table_join_part.c.id == group_table_join_part.c.site_id)
        stmt = select([agent_table_join_part.c.id,
                       site_table_join_part.c.customer_id]).select_from(j)

        agent_table = table('agent',
                            column('customer_id', String(36)),
                            column('id', String(36)))
        for entry in session.execute(stmt):
            upd_stmt = update(agent_table).values(
                customer_id=entry['customer_id']).where(
                agent_table.c.id == entry['id'])
            session.execute(upd_stmt)
        session.commit()
    finally:
        session.close()

    op.drop_column('group', 'site_id')
    op.drop_constraint('site_ibfk_1', 'site', type_='foreignkey')
    op.drop_column('agent', 'group_id')
    op.drop_table('site')


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # group-device to group-agent-devic & customer-device
    try:
        op.drop_constraint('agent_ibfk_1', 'agent', type_='foreignkey')
        op.add_column('agent', sa.Column('group_id', mysql.VARCHAR(
            collation='utf8mb4_unicode_ci', length=36), nullable=True))
        op.create_foreign_key(None, 'agent', 'group', ['group_id'], ['id'])
        agent_table = table(
            'agent',
            column('id', String(36)),
            column('customer_id', String(36)),
            column('group_id', String(36)))
        group_table = table(
            'group',
            column('id', String(36)),
            column('customer_id', String(36)))
        stmt = select([group_table])
        for group in session.execute(stmt):
            upd_stmt = update(agent_table).values(group_id=group['id']).where(
                agent_table.c.customer_id == group['customer_id'])
            session.execute(upd_stmt)

        op.add_column('device', sa.Column('agent_id', mysql.VARCHAR(
            collation='utf8mb4_unicode_ci', length=36), nullable=True))
        op.add_column('device', sa.Column('customer_id', mysql.VARCHAR(
            collation='utf8mb4_unicode_ci', length=36), nullable=True))
        op.drop_constraint('device_ibfk_1', 'device', type_='foreignkey')
        op.create_foreign_key(None, 'device', 'customer', ['customer_id'],
                              ['id'])
        op.create_foreign_key(None, 'device', 'agent', ['agent_id'], ['id'])

        agent_table = table(
            'agent',
            column('id', String(36)),
            column('customer_id', String(36)),
            column('group_id', String(36)))
        device_table = table(
            'device',
            column('id', String(36)),
            column('customer_id', String(36)),
            column('group_id', String(36)),
            column('agent_id', String(36)))
        stmt = select([agent_table])
        agents = session.execute(stmt)
        for agent in agents:
            upd_stmt = update(device_table).values(
                customer_id=agent['customer_id'], agent_id=agent['id']).where(
                device_table.c.group_id == agent['group_id'])
            session.execute(upd_stmt)
        session.commit()
    finally:
        session.close()

    op.drop_column('agent', 'customer_id')
    op.drop_column('device', 'group_id')

    # customer-group to customer-site-group
    sites_table = op.create_table(
        'site',
        sa.Column('deleted', mysql.TINYINT(display_width=1),
                  autoincrement=False, nullable=True),
        sa.Column('id',
                  mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=36),
                  nullable=False),
        sa.Column('state',
                  mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=256),
                  nullable=True),
        sa.Column('meta', mysql.TEXT(collation='utf8mb4_unicode_ci'),
                  nullable=True),
        sa.Column('default', mysql.TINYINT(display_width=1),
                  autoincrement=False, nullable=True),
        sa.Column('customer_id',
                  mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=36),
                  nullable=True),
        sa.Column('name',
                  mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=256),
                  nullable=False),
        sa.Column('description', mysql.TEXT(collation='utf8mb4_unicode_ci'),
                  nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.id'],
                                name='site_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    try:
        customer_table = table(
            'customer',
            column('id', String(36)))
        stmt = select([customer_table])
        customers = session.execute(stmt)

        sites = []
        count = 0
        for customer in customers:
            count += 1
            site = {
                'deleted': 0,
                'id': str(uuid.uuid4()),
                'state': 'new',
                'meta': None,
                'default': 1,
                'customer_id': customer['id'],
                'name': 'Site_%s' % str(count),
                'description': None
            }
            sites.append(site)
        op.bulk_insert(sites_table, sites)

        op.drop_constraint('group_ibfk_1', 'group', type_='foreignkey')
        op.add_column('group', sa.Column('site_id', mysql.VARCHAR(
            collation='utf8mb4_unicode_ci', length=36), nullable=True))
        op.create_foreign_key(None, 'group', 'site', ['site_id'], ['id'])
        group_table = table(
            'group',
            column('id', String(36)),
            column('site_id', String(36)),
            column('customer_id', String(36)))

        for site in sites:
            stmt = update(group_table).values(site_id=site['id']).where(
                group_table.c.customer_id == site['customer_id'])
            session.execute(stmt)
        session.commit()
    finally:
        session.close()

    op.drop_column('group', 'customer_id')
