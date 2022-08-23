import croniter
from datetime import datetime
import enum
import json

from sqlalchemy import Column, Integer, String, Enum, TEXT, ForeignKey
from sqlalchemy import inspect, UniqueConstraint, or_
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.declarative.base import _declarative_constructor
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship

from katara_service.utils import ModelEncoder, gen_id


def get_current_timestamp():
    return int(datetime.utcnow().timestamp())


class ReportFormat(enum.Enum):
    html = 'html'


class TaskState(enum.Enum):
    created = 'created'
    started = 'started'
    getting_scopes = 'getting_scopes'
    got_scopes = 'got_scopes'
    getting_recipients = 'getting_recipients'
    got_recipients = 'got_recipients'
    generating_data = 'generating_data'
    generated_data = 'generated_data'
    putting_to_herald = 'putting_to_herald'
    completed = 'completed'
    error = 'error'


class PermissionKeys(Enum):
    is_creatable = 'is_creatable'
    is_updatable = 'is_updatable'


class RolePurpose(enum.Enum):
    optscale_member = 'optscale_member'
    optscale_engineer = 'optscale_engineer'
    optscale_manager = 'optscale_manager'


class ColumnPermissions(Enum):
    full = {PermissionKeys.is_creatable: True,
            PermissionKeys.is_updatable: True}
    create_only = {PermissionKeys.is_creatable: True,
                   PermissionKeys.is_updatable: False}
    update_only = {PermissionKeys.is_creatable: False,
                   PermissionKeys.is_updatable: True}
    none = {PermissionKeys.is_creatable: False,
            PermissionKeys.is_updatable: False}


class Base(object):
    def __init__(self, **kwargs):
        init_columns = list(filter(lambda x: x.info.get(
            PermissionKeys.is_creatable) is True, self.__table__.c))
        for col in init_columns:
            setattr(self, col.name, kwargs.get(col.name))
            kwargs.pop(col.name, None)
        _declarative_constructor(self, **kwargs)

    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        # pylint: disable=E1101
        return cls.__name__.lower()

    def to_dict(self, expanded=False):
        mapper = inspect(self).mapper
        if not expanded:
            return {c.key: getattr(self, c.key)
                    for c in mapper.column_attrs}
        else:
            model_columns = {c.key: getattr(self, c.key)
                             for c in mapper.columns if not c.foreign_keys}
            if mapper.mapped_table.foreign_keys:
                for relation in mapper.relationships:
                    try:
                        model_columns[relation.key] = getattr(
                            self, relation.key).to_dict(expanded)
                    except AttributeError:
                        model_columns[relation.key] = None
            return model_columns

    def to_json(self, expanded=False):
        return json.dumps(self.to_dict(expanded), cls=ModelEncoder)


Base = declarative_base(cls=Base, constructor=None)


class BaseModel(object):
    id = Column(String(36), primary_key=True, default=gen_id)
    created_at = Column(Integer, default=get_current_timestamp,
                        nullable=False)

    @hybrid_property
    def unique_fields(self):
        return list()

    @hybrid_method
    def get_uniqueness_filter(self, is_new=True):
        inner_filter = [getattr(self.__table__.columns, x) == getattr(self, x)
                        for x in self.unique_fields
                        if getattr(self, x) is not None]
        outer_filter = [
            or_(*inner_filter)
        ]

        if not is_new:
            outer_filter.append(self.__table__.columns.id != self.id)
        return outer_filter


class Schedule(Base, BaseModel):
    __tablename__ = 'schedule'

    report_id = Column(
        String(36), ForeignKey('report.id', ondelete='CASCADE'),
        nullable=False, info=ColumnPermissions.create_only)
    recipient_id = Column(
        String(36), ForeignKey('recipient.id', ondelete='CASCADE'),
        nullable=False, info=ColumnPermissions.create_only)
    crontab = Column(String(128), nullable=False,
                     info=ColumnPermissions.full)
    last_run = Column(Integer, default=0, nullable=False)
    next_run = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint(
        'report_id', 'recipient_id', 'crontab',
        name='uc_schedule_report_recipient_crontab'),)

    def __init__(self, report_id, recipient_id, crontab):
        now = get_current_timestamp()
        cron = croniter.croniter(crontab, now)
        next_run = cron.get_next(datetime)
        self.next_run = int(next_run.timestamp())
        self.created_at = now
        self.report_id = report_id
        self.recipient_id = recipient_id
        self.crontab = crontab

    @hybrid_property
    def unique_fields(self):
        return ['crontab']

    @hybrid_method
    def get_uniqueness_filter(self, is_new=True):
        outer_filter = super().get_uniqueness_filter(is_new)
        outer_filter.extend([
            self.__table__.columns.recipient_id == self.recipient_id,
            self.__table__.columns.report_id == self.report_id])
        return outer_filter


class Recipient(Base, BaseModel):
    __tablename__ = 'recipient'

    role_purpose = Column(Enum(RolePurpose), nullable=True,
                          info=ColumnPermissions.create_only)
    scope_id = Column(String(36), nullable=False,
                      info=ColumnPermissions.create_only)
    user_id = Column(String(36), nullable=True,
                     info=ColumnPermissions.create_only)
    meta = Column(TEXT(), default='{}', nullable=True,
                  info=ColumnPermissions.full)
    schedules = relationship(
        'Schedule', backref='recipient', passive_deletes=True)

    __table_args__ = (UniqueConstraint(
        'role_purpose', 'scope_id', 'user_id',
        name='uc_recipient_role_purpose_scope_user'),)

    @hybrid_property
    def unique_fields(self):
        return ['role_purpose', 'user_id']

    @hybrid_method
    def get_uniqueness_filter(self, is_new=True):
        outer_filter = super().get_uniqueness_filter(is_new)
        outer_filter.extend([
            self.__table__.columns.scope_id == self.scope_id])
        return outer_filter

    def __init__(self, scope_id, role_purpose=None, user_id=None, meta=None):
        # preliminary id
        self.id = gen_id()
        self.scope_id = scope_id
        self.role_purpose = role_purpose
        self.user_id = user_id
        self.meta = meta


class Report(Base, BaseModel):
    __tablename__ = 'report'

    name = Column(String(50), nullable=False)
    module_name = Column(String(128), nullable=False)
    report_format = Column(Enum(ReportFormat), nullable=False)
    description = Column(TEXT(), nullable=True)
    schedules = relationship(
        'Schedule', backref='report', passive_deletes=True)

    __table_args__ = (UniqueConstraint(
        'name', 'module_name',
        name='uc_report_name_module_name'),)


class Task(Base, BaseModel):
    __tablename__ = 'task'
    schedule_id = Column(String(36), ForeignKey('schedule.id', ondelete='SET NULL'),
                         nullable=True, info=ColumnPermissions.create_only)
    schedule = relationship('Schedule')
    completed_at = Column(Integer, nullable=True)
    state = Column(Enum(TaskState), default=TaskState.created,
                   nullable=False, info=ColumnPermissions.full)
    result = Column(TEXT(), nullable=True,
                    info=ColumnPermissions.full)
    parent_id = Column(String(36), nullable=True,
                       info=ColumnPermissions.create_only)

    def __init__(self, schedule_id=schedule_id,
                 state=TaskState.created.value,
                 result=None, parent_id=None):
        # preliminary id
        self.id = gen_id()
        self.created_at = get_current_timestamp()
        self.schedule_id = schedule_id
        self.state = state
        self.result = result
        self.parent_id = parent_id
