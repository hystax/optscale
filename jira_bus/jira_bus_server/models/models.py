import json
from datetime import datetime

from sqlalchemy import (
    inspect, Column, Integer, String, Text, UniqueConstraint, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from jira_bus_server.utils import ModelEncoder, gen_id

Uuid = String(36)


def get_current_timestamp():
    return int(datetime.utcnow().timestamp())


class Base(object):
    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

    def to_json(self):
        return json.dumps(self.to_dict(), cls=ModelEncoder)


Base = declarative_base(cls=Base)


class BaseModel:
    id = Column(Uuid, primary_key=True, default=gen_id)
    created_at = Column(Integer, default=get_current_timestamp, nullable=False)
    deleted_at = Column(Integer, default=0, nullable=False)

    @hybrid_property
    def deleted(self):
        return self.deleted_at != 0


class AppInstallation(BaseModel, Base):
    __tablename__ = 'app_installation'

    client_key = Column(String(128), nullable=False)
    shared_secret = Column(Text(), nullable=False)
    extra_payload = Column(Text(), nullable=False)

    organization_assignment = relationship(
        'OrganizationAssignment',
        back_populates='app_installation',
        uselist=False  # One to one relation at the moment
    )
    __table_args__ = (UniqueConstraint(
        'client_key', 'deleted_at',
        name='uc_client_key_deleted_at'),)


class OrganizationAssignment(BaseModel, Base):
    __tablename__ = 'organization_assignment'

    organization_id = Column(Uuid, nullable=False)
    app_installation_id = Column(
        Uuid, ForeignKey('app_installation.id'), nullable=False)

    app_installation = relationship(
        'AppInstallation',
        back_populates='organization_assignment'
    )
    __table_args__ = (UniqueConstraint(
        'organization_id', 'app_installation_id', 'deleted_at',
        name='uc_org_id_app_inst_id_del_at'),)


class UserAssignment(BaseModel, Base):
    __tablename__ = 'user_assignment'

    jira_account_id = Column(String(128), nullable=False)
    secret = Column(Uuid, default=gen_id, nullable=False)
    auth_user_id = Column(Uuid, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            'jira_account_id', 'deleted_at',
            name='uc_jira_account_id_deleted_at'),
        UniqueConstraint(
            'secret', 'deleted_at',
            name='uc_secret_deleted_at'),
    )

    def to_dict(self, secure=True):
        # noinspection PyUnresolvedReferences
        result = super().to_dict()

        if secure:
            result.pop('secret', None)
        return result
