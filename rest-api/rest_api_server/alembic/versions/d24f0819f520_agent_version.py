""""agent_version"

Revision ID: d24f0819f520
Revises: f65dd9250246
Create Date: 2018-03-29 09:59:37.157756

"""
import uuid
from alembic import op
import sqlalchemy as sa
from enum import Enum
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = 'd24f0819f520'
down_revision = 'f65dd9250246'
branch_labels = None
depends_on = None


def gen_id():
    return str(uuid.uuid4())


class PermissionKeys(Enum):
    is_creatable = 'is_creatable'
    is_updatable = 'is_updatable'


class AgentTypes(Enum):
    BAGET = 'baget'
    CABRIO = 'cabrio'
    ELM = 'elm'
    OSA = 'osa'
    UNKNOWN = 'unknown'


class BaseMixin(object):
    deleted_at = Column(Integer, default=0, nullable=False)


class ImmutableMixin(BaseMixin):
    id = Column(String(36), primary_key=True, default=gen_id)


class Base(object):
    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        # pylint: disable=E1101
        return cls.__name__.lower()


Base = declarative_base(cls=Base)


class Agent(Base, ImmutableMixin):
    name = Column(String(256), nullable=True)
    type = Column(String(16), nullable=False)
    version = Column(String(32), nullable=True)
    update_to = Column(String(32), nullable=True)


def upgrade():
    op.add_column('agent', sa.Column(
        'type', sa.Enum('BAGET', 'CABRIO', 'ELM', 'OSA', 'UNKNOWN',
                        name='agent_type'), nullable=False))
    op.add_column('agent', sa.Column('update_to', sa.String(length=32),
                                     nullable=True))
    op.add_column('agent', sa.Column('version', sa.String(length=32),
                                     nullable=True))
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        agents = session.query(Agent).all()
        for agent in agents:
            if any(filter(lambda x: x in agent.name, ['cabrio', 'hvragent'])):
                agent.type = AgentTypes.CABRIO.value
            elif any(filter(lambda x: x in agent.name, [
                'baget', 'repman', 'hwragent', 'windows'])):
                agent.type = AgentTypes.BAGET.value
            elif any(filter(lambda x: x in agent.name, ['elm', 'linux'])):
                agent.type = AgentTypes.ELM.value
            elif any(filter(lambda x: x in agent.name, ['osa',
                                                        'openstack'])):
                agent.type = AgentTypes.OSA.value
            else:
                agent.type = AgentTypes.UNKNOWN.value
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('agent', 'version')
    op.drop_column('agent', 'update_to')
    op.drop_column('agent', 'type')
