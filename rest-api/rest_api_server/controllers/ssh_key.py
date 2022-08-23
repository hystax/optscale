import logging
from sqlalchemy import exists, and_, true
from optscale_exceptions.common_exc import (
    NotFoundException, ConflictException, WrongArgumentsException,
    FailedDependency)
from rest_api_server.controllers.base import BaseController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from rest_api_server.models.models import SshKey, Organization, Employee
from rest_api_server.utils import gen_fingerprint

LOG = logging.getLogger(__name__)


class SshKeyController(BaseController):
    def _get_model_type(self):
        return SshKey

    def get_employee(self, employee_id):
        employee = self.session.query(Employee).filter(and_(
            Employee.id == employee_id,
            Employee.deleted.is_(False)
        )).one_or_none()
        if employee is None:
            raise NotFoundException(Err.OE0002,
                                    [Employee.__name__, employee_id])
        return employee

    def create(self, **kwargs):
        try:
            kwargs.update({'fingerprint': gen_fingerprint(kwargs['key'])})
        except Exception:
            raise WrongArgumentsException(Err.OE0507, [])
        default = kwargs.pop('default', False)
        default_key_exist = self.session.query(
            exists().where(
                and_(
                    self.model_type.deleted.is_(False),
                    self.model_type.employee_id == kwargs['employee_id'],
                    self.model_type.default == true()
                )
            )
        ).scalar()
        default = True if not default_key_exist else default
        kwargs['default'] = default
        result = super().create(**kwargs)
        if default:
            self._make_default(result)
        return result

    def edit(self, item_id, **kwargs):
        default = kwargs.get('default')
        result = super().edit(item_id, **kwargs)
        if default:
            self._make_default(result)
        return result

    def _make_default(self, ssh_key):
        self.session.query(self.model_type).filter(and_(
            self.model_type.default == true(),
            self.model_type.id != ssh_key.id,
            self.model_type.employee_id == ssh_key.employee_id
        )).update(
            values={self.model_type.default: False},
        )
        ssh_key.default = True
        self.session.commit()

    def _validate(self, item, is_new=True, **kwargs):
        if not self._is_employee_exists(item.employee_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, item.organization_id])
        query = self.session.query(exists().where(
            and_(*(item.get_uniqueness_filter(is_new)))))
        ssh_key_exist = query.scalar()
        if ssh_key_exist:
            raise ConflictException(Err.OE0506, [item.fingerprint])

    def _is_employee_exists(self, employee_id):
        return self.session.query(
            exists().where(and_(
                Employee.id == employee_id,
                Employee.deleted.is_(False)
            ))
        ).scalar()

    def delete(self, item_id):
        ssh_key = self.get(item_id)
        if ssh_key.default:
            another_ssh_key_exist = self.session.query(
                exists().where(
                    and_(
                        self.model_type.deleted.is_(False),
                        self.model_type.employee_id == ssh_key.employee_id,
                        self.model_type.id != ssh_key.id
                    )
                )
            ).scalar()
            if another_ssh_key_exist:
                raise FailedDependency(Err.OE0509, [])
        return super().delete(item_id)


class SshKeyAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return SshKeyController
