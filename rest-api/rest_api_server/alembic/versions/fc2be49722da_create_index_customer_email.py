""""create_index_customer_email"

Revision ID: fc2be49722da
Revises: 3085a95a06a1
Create Date: 2017-03-24 12:01:08.724857

"""
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, select, insert
from sqlalchemy import MetaData, Column, Table

# revision identifiers, used by Alembic.
revision = 'fc2be49722da'
down_revision = '3085a95a06a1'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    meta = MetaData()

    customer_table = Table('customer', meta,
                           Column('deleted', Integer),
                           Column('id', String(36)),
                           Column('state', String(256)),
                           Column('name', String(256)),
                           Column('email', String(256)),
                           Column('password', String(20)),
                           Column('partner_id', String(36)))
    stmt = select([customer_table])

    temp_table_name = 'customer_%s' % str(uuid.uuid4())[:5]
    # create temp table for customers
    temp_customer = Table(temp_table_name, meta,
                          Column('deleted', Integer),
                          Column('id', String(36)),
                          Column('state', String(256)),
                          Column('name', String(256)),
                          Column('email', String(256)),
                          Column('password', String(20)),
                          Column('partner_id', String(36)))
    temp_customer.create(session.get_bind())
    try:
        customers = session.execute(stmt)
        for customer in customers:
            ins_stmt = insert(temp_customer).values(
                deleted=customer['deleted'],
                id=customer['id'],
                state=customer['state'],
                name=customer['name'],
                email=customer['email'],
                password=customer['password'],
                partner_id=customer['partner_id'])
            session.execute(ins_stmt)
        session.commit()

        # delete f-keys from customer
        op.drop_constraint('cloudsite_ibfk_1', 'cloudsite', type_='foreignkey')
        op.drop_constraint('drplan_ibfk_1', 'drplan', type_='foreignkey')
        op.drop_constraint('site_ibfk_1', 'site', type_='foreignkey')
        op.drop_constraint('device_ibfk_1', 'device', type_='foreignkey')
        op.drop_index('customer_id', table_name='drplan')

        # delete customer table
        op.drop_table('customer')

        op.create_table('customer',
                        sa.Column('deleted', sa.Boolean(), nullable=True),
                        sa.Column('id', sa.String(length=36), nullable=False),
                        sa.Column('state', sa.String(length=256),
                                  nullable=True),
                        sa.Column('name', sa.String(length=256),
                                  nullable=True),
                        sa.Column('email', sa.String(length=256),
                                  nullable=True),
                        sa.Column('password', sa.String(length=20),
                                  nullable=True),
                        sa.Column('partner_id', sa.String(length=36),
                                  nullable=True),
                        sa.ForeignKeyConstraint(['partner_id'],
                                                ['partner.id'], ),
                        sa.PrimaryKeyConstraint('id'),
                        mysql_row_format='DYNAMIC')
        op.create_index(op.f('ix_customer_email'), 'customer', ['email'],
                        unique=True)

        # copy data from temp table to customer table
        sql = select([temp_customer])
        customer_set = session.execute(sql)
        for customer in customer_set:
            ins_stmt = insert(customer_table).values(
                deleted=customer['deleted'],
                id=customer['id'],
                state=customer['state'],
                name=customer['name'],
                email=customer['email'],
                password=customer['password'],
                partner_id=customer['partner_id'])
            session.execute(ins_stmt)

        session.commit()

        # create f-keys for customer
        op.create_foreign_key('site_ibfk_1', 'site', 'customer',
                              ['customer_id'], ['id'])
        op.create_foreign_key('drplan_ibfk_1', 'drplan', 'customer',
                              ['customer_id'], ['id'])
        op.create_foreign_key('device_ibfk_1', 'device', 'customer',
                              ['customer_id'], ['id'])
        op.create_foreign_key('cloudsite_ibfk_1', 'cloudsite', 'customer',
                              ['customer_id'], ['id'])
        op.create_index('customer_id', 'drplan', ['customer_id', 'name'],
                        unique=True)

        # drop temp table
        temp_customer.drop(session.get_bind(), checkfirst=True)
    finally:
        session.close()


def downgrade():
    op.drop_index(op.f('ix_customer_email'), table_name='customer')
