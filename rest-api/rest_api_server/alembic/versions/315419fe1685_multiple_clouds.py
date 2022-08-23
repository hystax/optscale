""""multiple_clouds"

Revision ID: 315419fe1685
Revises: c1095c9b7b6a
Create Date: 2019-10-04 14:29:32.537990

"""
import enum
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import or_, and_
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, Session

# revision identifiers, used by Alembic.
revision = '315419fe1685'
down_revision = '7277dc51aa0f'
branch_labels = None
depends_on = None


class CloudTypes(enum.Enum):
    OPENSTACK = 'openstack'
    OPENSTACK_CNR = 'openstack_cnr'
    OPENSTACK_HUAWEI_CNR = 'openstack_huawei_cnr'
    AWS_CNR = 'aws_cnr'
    ALIBABA_CNR = 'alibaba_cnr'
    VMWARE_CNR = 'vmware_cnr'
    AZURE_CNR = 'azure_cnr'
    FAKE = 'fake'


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


class Mountpoint(Base):
    id = sa.Column(sa.String(36), primary_key=True, default=gen_id)
    deleted_at = sa.Column(sa.Integer, default=0, nullable=False)
    mountpoint = sa.Column(sa.TEXT, nullable=False)
    size = sa.Column(sa.BigInteger, nullable=False, default=0)
    is_cnr = sa.Column(sa.Boolean, nullable=False, default=True)
    default = sa.Column(sa.Boolean, nullable=False, default=False)


class Customer(Base):
    id = sa.Column(sa.String(36), primary_key=True, default=gen_id)
    deleted_at = sa.Column(sa.Integer, default=0, nullable=False)
    name = sa.Column(sa.String(255))
    email = sa.Column(sa.String(255))
    active = sa.Column(sa.Boolean, default=True)
    address = sa.Column(sa.String(255), nullable=False, default='')
    phone = sa.Column(sa.String(255), nullable=False, default='')
    default_group_id = sa.Column(sa.String(36))
    partner_id = sa.Column(sa.String(36), sa.ForeignKey('partner.id'), nullable=False)
    partner = relationship("Partner", backref='customers')
    mountpoint_id = sa.Column(sa.String(36), sa.ForeignKey('mountpoint.id'),
                              nullable=False)
    mountpoint = relationship("Mountpoint", backref='customers')
    cloud_id = sa.Column(sa.String(36), sa.ForeignKey('cloud.id'), nullable=True)
    cloud = relationship("Cloud", backref='customers', foreign_keys=[cloud_id])
    cloud_overlay = sa.Column(sa.TEXT, nullable=False, default='{}')

    __table_args__ = (sa.UniqueConstraint("partner_id", "name", "deleted_at",
                                          name="uc_prtnr_name_del_at"),)


class Partner(Base):
    id = sa.Column(sa.String(36), primary_key=True, default=gen_id)
    deleted_at = sa.Column(sa.Integer, default=0, nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(255))

    __table_args__ = (sa.UniqueConstraint("name", "deleted_at",
                                          name="uc_name_del_at"),)


class Cloud(Base):
    id = sa.Column(sa.String(36), primary_key=True, default=gen_id)
    deleted_at = sa.Column(sa.Integer, default=0, nullable=False)
    type = sa.Column(sa.Enum(CloudTypes), default=CloudTypes.OPENSTACK_CNR,
                     nullable=False)
    name = sa.Column(sa.String(256), nullable=False)
    endpoint = sa.Column(sa.String(256), nullable=True)
    username = sa.Column(sa.String(256), nullable=True)
    password = sa.Column(sa.String(256), nullable=True)
    salt = sa.Column(sa.String(36), nullable=True)
    extra_args = sa.Column(sa.TEXT)
    default = sa.Column(sa.Boolean, nullable=False, default=False)
    managed = sa.Column(sa.Boolean, default=True, nullable=False)
    customer_id = sa.Column(sa.String(36), sa.ForeignKey('customer.id'),
                            nullable=True)
    customer = relationship("Customer", backref="clouds",
                            foreign_keys=[customer_id])
    partner_id = sa.Column(sa.String(36), sa.ForeignKey('partner.id'),
                           nullable=True)
    partner = relationship("Partner", backref="clouds")

    __table_args__ = (sa.UniqueConstraint("name", "deleted_at",
                                          name="uc_cloud_name_del_at"),)


def upgrade():
    op.add_column('cloud', sa.Column('customer_id', sa.String(length=36),
                                     nullable=True))
    op.add_column('cloud', sa.Column('managed', sa.Boolean(), nullable=False,
                                     default=True))
    op.add_column('cloud', sa.Column('partner_id', sa.String(length=36),
                                     nullable=True))
    op.create_foreign_key('cloud_customer_fk', 'cloud', 'customer',
                          ['customer_id'], ['id'])
    op.create_foreign_key('cloud_partner_fk', 'cloud', 'partner',
                          ['partner_id'], ['id'])
    op.create_unique_constraint('uc_cloud_name_del_at_customer_partner',
                                'cloud', ['name', 'deleted_at', 'customer_id',
                                          'partner_id'])
    op.drop_index('uc_cloud_name_del_at', table_name='cloud')

    bind = op.get_bind()
    session = Session(bind=bind)
    default_cloud = session.query(Cloud).filter(
        Cloud.deleted_at == 0, Cloud.default.is_(True)).one_or_none()

    if default_cloud is None:
        session.close()
        return

    partner_table = sa.table("partner", sa.column('id', sa.String(36)))
    partner_cloud_map = {}

    # making a copy of default cloud for each partner
    for i, row in enumerate(session.execute(sa.select([partner_table.c.id]))):
        partner_id = row['id']
        if i == 0:
            partner_cloud_map[partner_id] = default_cloud
            continue
        new_cloud_dict = default_cloud.to_dict()
        new_cloud_dict['id'] = gen_id()
        new_cloud_dict['name'] = new_cloud_dict['id']
        new_cloud = Cloud(**new_cloud_dict)
        partner_cloud_map[partner_id] = new_cloud

    try:
        for partner_id, cloud in partner_cloud_map.items():
            cloud.partner_id = partner_id
            session.add(cloud)
            p_customers = session.query(Customer).filter(
                Customer.partner_id == partner_id,
                or_(Customer.cloud_id == default_cloud.id,
                    Customer.cloud_id.is_(None))).all()
            for customer in p_customers:
                customer.cloud_id = cloud.id
                session.add(customer)

        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        default_clouds = session.query(Cloud).filter(
            Cloud.deleted_at == 0, Cloud.default.is_(True)).all()

        deleted_cloud_ids = [c.id for c in default_clouds[1:]]

        customers = session.query(Customer).filter(Customer.deleted_at == 0).all()
        for customer in customers:
            if customer.cloud_id in deleted_cloud_ids:
                customer.cloud_id = default_clouds[0].id
                session.add(customer)

        for cloud in default_clouds[1:]:
            session.delete(cloud)

        session.commit()
    finally:
        session.close()

    op.create_index('uc_cloud_name_del_at', 'cloud', ['name', 'deleted_at'],
                    unique=True)
    op.drop_constraint('uc_cloud_name_del_at_customer_partner', 'cloud',
                       type_='unique')
    op.drop_constraint('cloud_customer_fk', 'cloud', type_='foreignkey')
    op.drop_constraint('cloud_partner_fk', 'cloud', type_='foreignkey')
    op.drop_column('cloud', 'partner_id')
    op.drop_column('cloud', 'managed')
    op.drop_column('cloud', 'customer_id')
