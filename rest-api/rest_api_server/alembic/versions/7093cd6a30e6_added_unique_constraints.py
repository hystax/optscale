""""added_unique_constraints"

Revision ID: 7093cd6a30e6
Revises: 59ea8eab433e
Create Date: 2017-07-26 08:15:52.138341

"""
import datetime
import sqlalchemy as sa

from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import select, String, update, Text, func, and_

# revision identifiers, used by Alembic.
revision = '7093cd6a30e6'
down_revision = '00a6ba287712'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        for table_name in ['agent', 'cloudsite', 'drplan', 'group', 'vsphere_credential']:
            table_ = table(table_name,
                           column('id', String(36)),
                           column('customer_id', String(36)),
                           column('name', Text))
            inner_stmt = select(
                [table_.c.name, table_.c.customer_id, func.count('*').label('cnt')]
            ).group_by(table_.c.name, table_.c.customer_id).alias('inner_stmt')
            outer_stmt = select(
                [inner_stmt.c.name, inner_stmt.c.customer_id,
                                 inner_stmt.c.cnt]
            ).select_from(inner_stmt).where(inner_stmt.c.cnt > 1)
            for duplicates in session.execute(outer_stmt):
                stmt = select([table_]).where(and_(
                    table_.c.name == duplicates['name'],
                    table_.c.customer_id == duplicates['customer_id']))
                for duplicate in session.execute(stmt):
                    new_name = '%s_%f' % (
                        duplicate['name'],
                        datetime.datetime.utcnow().timestamp())
                    upd_stmt = update(table_).values(
                        name=new_name
                    ).where(table_.c.id == duplicate['id'])
                    session.execute(upd_stmt)

        for table_name in ['customer']:
            table_ = table(table_name,
                           column('id', String(36)),
                           column('partner_id', String(36)),
                           column('name', Text))
            inner_stmt = select(
                [table_.c.name, table_.c.partner_id, func.count('*').label('cnt')]
            ).group_by(table_.c.name, table_.c.partner_id).alias('inner_stmt')
            outer_stmt = select(
                [inner_stmt.c.name, inner_stmt.c.partner_id, inner_stmt.c.cnt]
            ).select_from(inner_stmt).where(inner_stmt.c.cnt > 1)
            for duplicates in session.execute(outer_stmt):
                stmt = select([table_]).where(and_(
                    table_.c.name == duplicates['name'],
                    table_.c.partner_id == duplicates['partner_id']))
                for duplicate in session.execute(stmt):
                    new_name = '%s_%f' % (
                        duplicate['name'],
                        datetime.datetime.utcnow().timestamp())
                    upd_stmt = update(table_).values(
                        name=new_name
                    ).where(table_.c.id == duplicate['id'])
                    session.execute(upd_stmt)

        for table_name in ['partner']:
            table_ = table(table_name,
                           column('id', String(36)),
                           column('name', Text))
            inner_stmt = select(
                [table_.c.name, func.count('*').label('cnt')]
            ).group_by(table_.c.name).alias('inner_stmt')
            outer_stmt = select(
                [inner_stmt.c.name, inner_stmt.c.cnt]
            ).select_from(inner_stmt).where(inner_stmt.c.cnt > 1)
            for duplicates in session.execute(outer_stmt):
                stmt = select([table_]).where(
                    table_.c.name == duplicates['name'])
                for duplicate in session.execute(stmt):
                    new_name = '%s_%f' % (
                        duplicate['name'],
                        datetime.datetime.utcnow().timestamp())
                    upd_stmt = update(table_).values(
                        name=new_name
                    ).where(table_.c.id == duplicate['id'])
                    session.execute(upd_stmt)

        session.commit()

        for table_name in ['agent', 'cloudsite', 'drplan', 'group',
                           'vsphere_credential', 'customer', 'partner']:
            stmt = "ALTER TABLE `%s` ROW_FORMAT=DYNAMIC;" % table_name
            session.execute(stmt)
    finally:
        session.close()

    op.drop_constraint('drplan_ibfk_1', 'drplan', type_='foreignkey')
    op.drop_index('idx_drplan_name_customer_unique', 'drplan')
    op.create_unique_constraint('uc_cstmr_name_del_at', 'drplan',
                                ['customer_id', 'name', 'deleted_at'])
    op.create_foreign_key('drplan_ibfk_customer', 'drplan', 'customer', ['customer_id'], ['id'])

    op.create_unique_constraint('uc_cstmr_name_del_at', 'agent',
                                ['customer_id', 'name', 'deleted_at'])
    op.create_unique_constraint('uc_cstmr_name_del_at', 'cloudsite',
                                ['customer_id', 'name', 'deleted_at'])
    op.create_unique_constraint('uc_cstmr_name_del_at', 'group',
                                ['customer_id', 'name', 'deleted_at'])
    op.create_unique_constraint('uc_cstmr_name_del', 'vsphere_credential',
                                ['customer_id', 'name', 'deleted_at'])
    op.create_unique_constraint('uc_prtnr_name_del_at', 'customer',
                                ['partner_id', 'name', 'deleted_at'])

    op.create_unique_constraint('uc_name_del_at', 'partner',
                                ['name', 'deleted_at'])


def downgrade():
    op.drop_constraint('drplan_ibfk_customer', 'drplan', type_='foreignkey')
    op.drop_constraint('uc_cstmr_name_del_at', 'drplan', type_='unique')
    op.create_foreign_key('drplan_ibfk_1', 'drplan', 'customer', ['customer_id'], ['id'])
    op.create_index('idx_drplan_name_customer_unique', 'drplan', ['customer_id', 'name', 'deleted_at'], unique=True)

    op.drop_constraint('vsphere_credential_ibfk_1', 'vsphere_credential', type_='foreignkey')
    op.drop_constraint('uc_cstmr_name_del', 'vsphere_credential', type_='unique')
    op.create_foreign_key('vsphere_credential_ibfk_1', 'vsphere_credential', 'customer', ['customer_id'], ['id'])

    op.drop_constraint('uc_name_del_at', 'partner', type_='unique')

    op.drop_constraint('group_ibfk_1', 'group', type_='foreignkey')
    op.drop_constraint('uc_cstmr_name_del_at', 'group', type_='unique')
    op.create_foreign_key('group_ibfk_1', 'group', 'customer', ['customer_id'], ['id'])

    op.drop_constraint('customer_ibfk_1', 'customer', type_='foreignkey')
    op.drop_constraint('uc_prtnr_name_del_at', 'customer', type_='unique')
    op.create_foreign_key('customer_ibfk_1', 'customer', 'partner', ['partner_id'], ['id'])

    op.drop_constraint('cloudsite_ibfk_1', 'cloudsite', type_='foreignkey')
    op.drop_constraint('uc_cstmr_name_del_at', 'cloudsite', type_='unique')
    op.create_foreign_key('cloudsite_ibfk_1', 'cloudsite', 'customer', ['customer_id'], ['id'])

    op.drop_constraint('agent_ibfk_1', 'agent', type_='foreignkey')
    op.drop_constraint('uc_cstmr_name_del_at', 'agent', type_='unique')
    op.create_foreign_key('agent_ibfk_1', 'agent', 'customer', ['customer_id'], ['id'])
