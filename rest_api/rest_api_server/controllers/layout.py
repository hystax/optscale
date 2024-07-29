import logging
from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import true
from tools.optscale_exceptions.common_exc import NotFoundException
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Employee, Layout

LOG = logging.getLogger(__name__)


class LayoutsController(BaseProfilingController):
    def _get_model_type(self):
        return Layout

    def create(self, user_id, organization_id, **kwargs):
        emp_ctrl = EmployeeController(self.session, self._config)
        employee = emp_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id)
        kwargs['owner_id'] = employee.id
        return super().create(**kwargs)

    def get_layouts_for_user(self, organization_id, employee_id=None,
                             layout_id=None, layout_type=None,
                             include_shared=True, entity_id=None,
                             secret=False):
        if not employee_id and secret:
            # all layouts for all organization employees
            employee_q = self.session.query(Employee.id).filter(
                Employee.organization_id == organization_id).subquery()
            query = self.session.query(Layout).filter(
                Layout.owner_id.in_(employee_q))
        else:
            if include_shared:
                # layouts for current employee and layouts with shared=True for
                # other organization employees
                employee_q = self.session.query(Employee.id).filter(
                    Employee.organization_id == organization_id,
                    Employee.deleted_at == 0).subquery()
                query = self.session.query(Layout).filter(or_(
                    Layout.owner_id == employee_id,
                    and_(Layout.shared.is_(true()),
                         Layout.owner_id.in_(employee_q))
                ))
            else:
                # layouts for current employee
                query = self.session.query(Layout).filter(
                    Layout.owner_id == employee_id)
            if entity_id:
                query = query.filter(Layout.entity_id == entity_id)
            if layout_type:
                query = query.filter(Layout.type == layout_type)
        if layout_id:
            query = query.filter(Layout.id == layout_id)
        return query.all()

    def _get_employee_id(self, user_id, organization_id):
        if not user_id:
            return None
        emp_ctrl = EmployeeController(self.session, self._config)
        employee = emp_ctrl.get_employee_by_user_and_organization(
                user_id, organization_id)
        return employee.id

    def list(self, user_id, organization_id, layout_type=None,
             include_shared=False, entity_id=None, secret=False):
        self.check_organization(organization_id)
        employee_id = self._get_employee_id(user_id, organization_id)
        layouts = self.get_layouts_for_user(
            organization_id, employee_id=employee_id, layout_type=layout_type,
            include_shared=include_shared, entity_id=entity_id, secret=secret)
        result = {'layouts': [], 'current_employee_id': employee_id}
        for layout in layouts:
            layout = layout.to_dict()
            layout.pop('data', None)
            result['layouts'].append(layout)
        return result

    def edit(self, user_id, organization_id, layout_id, **kwargs):
        layout = self.get_item(user_id, organization_id, layout_id,
                               include_shared=False)
        if not layout:
            raise NotFoundException(
                Err.OE0002, [Layout.__name__, layout_id])
        return super().edit(layout_id, **kwargs)

    def get_item(self, user_id, organization_id, layout_id,
                 include_shared=True, secret=False):
        self.check_organization(organization_id)
        employee_id = self._get_employee_id(user_id, organization_id)
        layout = self.get_layouts_for_user(
            organization_id, employee_id=employee_id, layout_id=layout_id,
            include_shared=include_shared, secret=secret)
        if not layout:
            raise NotFoundException(
                Err.OE0002, [Layout.__name__, layout_id])
        return layout[0]

    def delete(self, user_id, organization_id, layout_id, secret=False):
        self.get_item(user_id, organization_id, layout_id,
                      include_shared=False, secret=secret)
        self.hard_delete(layout_id)


class LayoutsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LayoutsController
