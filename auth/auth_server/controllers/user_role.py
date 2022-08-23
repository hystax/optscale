import logging
from sqlalchemy import and_

from auth_server.controllers.base import BaseController
from auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth_server.models.models import Assignment, Role, User
from auth_server.utils import (load_payload, check_kwargs_is_empty, check_list_attribute)

LOG = logging.getLogger(__name__)


class UserRoleController(BaseController):
    def _get_model_type(self):
        return Role

    def get(self, **kwargs):
        payload = kwargs.pop('payload')
        check_kwargs_is_empty(**kwargs)
        payload_dict = load_payload(payload)
        user_ids = payload_dict.get('user_ids')
        role_purposes = payload_dict.get('role_purposes')
        scope_ids = payload_dict.get('scope_ids')
        check_list_attribute('user_ids', user_ids, required=False)
        check_list_attribute('role_purposes', role_purposes, required=False)
        check_list_attribute('scope_ids', scope_ids, required=False)
        result = list()
        query = self.session.query(
            Assignment.id,
            Assignment.resource_id,
            Assignment.type_id,
            Role.scope_id,
            Role.name,
            Role.id,
            Role.purpose,
            User.id.label('user_id'),
            User.email,
            User.display_name
        ).join(
            User, and_(
                User.deleted.is_(False),
                Assignment.user_id == User.id
            )
        ).join(
            Role, and_(
                Role.deleted.is_(False),
                Role.id == Assignment.role_id)
        ).filter(
                Assignment.deleted.is_(False),
        )
        if user_ids:
            query = query.filter(
                User.id.in_(user_ids)
            )
        if role_purposes:
            query = query.filter(
                Role.purpose.in_(role_purposes)
            )
        if scope_ids:
            query = query.filter(
                Assignment.resource_id.in_(scope_ids)
            )
        query_set = query.all()
        for item in query_set:
            (assignment_id, assignment_resource_id, assignment_type_id,
             role_scope_id, role_name, role_id, role_purpose, user_id,
             user_email, user_display_name) = item
            result.append(
                dict(
                    assignment_id=assignment_id,
                    assignment_resource_id=assignment_resource_id,
                    assignment_type_id=assignment_type_id,
                    role_scope_id=role_scope_id,
                    role_name=role_name,
                    role_id=role_id,
                    role_purpose=role_purpose,
                    user_id=user_id,
                    user_email=user_email,
                    user_display_name=user_display_name
                )
            )
        return result


class UserRoleAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return UserRoleController
