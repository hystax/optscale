""""keep_last_for_retention"

Revision ID: 8c5a8f3bf3d4
Revises: c1095c9b7b6a
Create Date: 2019-10-30 18:03:26.895979

"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import literal_column, and_
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, relationship

revision = '8c5a8f3bf3d4'
down_revision = 'c1095c9b7b6a'
branch_labels = None
depends_on = None


class Base(object):
    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        # pylint: disable=E1101
        return cls.__name__.lower()

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in sa.inspect(self).mapper.column_attrs}


def gen_id():
    return str(uuid.uuid4())


Base = declarative_base(cls=Base)


class Retention(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    owner_id = sa.Column(sa.String(36), nullable=True)
    interval = sa.Column(sa.Integer, nullable=False)
    keep_last = sa.Column(sa.Integer, nullable=False)
    daily = sa.Column(sa.Integer, nullable=False)
    weekly = sa.Column(sa.Integer, nullable=False)
    monthly = sa.Column(sa.Integer, nullable=False)
    annually = sa.Column(sa.Integer, nullable=False)


class Partner(Base):
    id = sa.Column(sa.String(36), primary_key=True, default=gen_id)
    deleted_at = sa.Column(sa.Integer, default=0, nullable=False)

    @hybrid_property
    def parent(self):
        return None


class Customer(Base):
    id = sa.Column(sa.String(36), primary_key=True, default=gen_id)
    deleted_at = sa.Column(sa.Integer, default=0, nullable=False)
    partner_id = sa.Column(sa.String(36), sa.ForeignKey('partner.id'),
                           nullable=False)
    partner = relationship("Partner", backref='customers')

    @hybrid_property
    def parent(self):
        return self.partner


class Group(Base):
    id = sa.Column(sa.String(36), primary_key=True, default=gen_id)
    deleted_at = sa.Column(sa.Integer, default=0, nullable=False)
    customer_id = sa.Column(sa.String(36), sa.ForeignKey('customer.id'))
    customer = relationship("Customer", backref="groups")

    @hybrid_property
    def parent(self):
        return self.customer


class Device(Base):
    id = sa.Column(sa.String(36), primary_key=True, default=gen_id)
    deleted_at = sa.Column(sa.Integer, default=0, nullable=False)
    group_id = sa.Column(sa.String(36), sa.ForeignKey('group.id'))
    group = relationship("Group", backref="devices")

    @hybrid_property
    def parent(self):
        return self.group


class Schedule(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    owner_id = sa.Column(sa.String(36), nullable=True)
    target_rpo = sa.Column(sa.Integer, nullable=False)


def get_owner_entry(session, owner_id):
    query = session.query(
        literal_column(repr(Device.__table__.name)).label("entry")
    ).distinct("entry").filter(and_(
        Device.id == owner_id, Device.deleted_at == 0
    )).union(session.query(
        literal_column(repr(Group.__table__.name)).label("entry")
    ).distinct("entry").filter(and_(
        Group.id == owner_id, Group.deleted_at == 0
    ))).union(session.query(
        literal_column(repr(Customer.__table__.name)).label("entry")
    ).distinct("entry").filter(and_(
        Customer.id == owner_id, Customer.deleted_at == 0
    ))).union(session.query(
        literal_column(repr(Partner.__table__.name)).label("entry")
    ).distinct("entry").filter(and_(
        Partner.id == owner_id, Partner.deleted_at == 0
    )))
    res = query.all()
    return res[0][0]


def get_owner(session, owner_id):
    db_models = {
        'device': Device,
        'group': Group,
        'customer': Customer,
        'partner': Partner
    }
    try:
        entry_type = get_owner_entry(session, owner_id)
    except IndexError:
        return None
    model = db_models.get(entry_type)
    item = session.query(model).filter(and_(
        model.id == owner_id,
        model.deleted_at == 0)).one_or_none()
    return item


def get_rpo_for_retention(session, owner_id):
    item = get_owner(session, owner_id)
    models_list = list()
    while not models_list:
        query = session.query(Schedule).filter(
            Schedule.owner_id == (item.id if item else None))
        models_list = query.all()
        item = item.parent if item else None
    schedule = models_list.pop()
    return schedule.target_rpo


def upgrade():
    op.add_column('retention', sa.Column('keep_last', sa.Integer,
                                         autoincrement=False, nullable=False))

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        for retention in session.query(Retention).all():
            rpo = get_rpo_for_retention(session, retention.owner_id)

            new_keep_last = (retention.interval * 3600 * 24) / rpo
            new_daily = retention.daily - retention.interval if retention.interval > 0 else 0
            new_weekly = retention.weekly - (((retention.daily - 1) // 7) + 1)
            new_monthly = retention.monthly - (((retention.weekly - 1) // 4) + 1)
            new_annually = retention.annually - (((retention.monthly - 1) // 12) + 1)

            retention.keep_last = new_keep_last if new_keep_last > 0 else 1
            retention.daily = 0 if new_daily < 0 else new_daily
            retention.weekly = 0 if new_weekly < 0 else new_weekly
            retention.monthly = 0 if new_monthly < 0 else new_monthly
            retention.annually = 0 if new_annually < 0 else new_annually
            session.add(retention)
        session.commit()
    finally:
        session.close()

    op.drop_column('retention', 'interval')


def downgrade():
    op.add_column('retention', sa.Column('interval', sa.Integer,
                                         autoincrement=False, nullable=False))

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        for retention in session.query(Retention).all():
            rpo = get_rpo_for_retention(session, retention.owner_id)

            retention.interval = (retention.keep_last * rpo) // (3600 * 24)
            retention.daily += retention.interval or 1
            retention.weekly += (((retention.daily - 1) // 7) + 1)
            retention.monthly += (((retention.weekly - 1) // 4) + 1)
            retention.annually += (((retention.monthly - 1) // 12) + 1)
            session.add(retention)
        session.commit()
    finally:
        session.close()

    op.drop_column('retention', 'keep_last')
