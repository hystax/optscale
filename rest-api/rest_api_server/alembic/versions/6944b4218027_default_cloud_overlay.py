""""default_cloud_overlay"

Revision ID: 6944b4218027
Revises: eacbccb73090
Create Date: 2018-08-20 11:24:16.204237

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, TEXT


# revision identifiers, used by Alembic.
revision = '6944b4218027'
down_revision = 'eacbccb73090'
branch_labels = None
depends_on = None


class Base(object):
    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        # pylint: disable=E1101
        return cls.__name__.lower()


Base = declarative_base(cls=Base)


class Customer(Base):
    id = Column(String(36), primary_key=True)
    cloud_overlay = Column(TEXT)


def upgrade():
    # this is because BLOB/TEXT column can't have a server default value
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        customers = session.query(Customer).all()
        for customer in customers:
            if not customer.cloud_overlay:
                customer.cloud_overlay = '{}'
                session.add(customer)
        session.commit()
    finally:
        session.close()

    op.alter_column('customer', 'cloud_overlay',
                    existing_type=sa.TEXT(), nullable=False)


def downgrade():
    op.alter_column('customer', 'cloud_overlay',
                    existing_type=sa.TEXT(), nullable=True)
