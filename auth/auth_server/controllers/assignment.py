import json
import logging
import datetime
from sqlalchemy import and_, or_

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.role import RoleController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import (
    Assignment, Role, Type, User)
from tools.optscale_exceptions.common_exc import (ForbiddenException,
                                                  NotFoundException,
                                                  WrongArgumentsException)
from auth.auth_server.utils import check_action


LOG = logging.getLogger(__name__)


class AssignmentController(BaseController):
    def _get_model_type(self):
        return Assignment

    @staticmethod
    def _is_self_assign(user, item_user_id):
        return user.id == item_user_id

    def _get_input(self, **input):
        role_id = input.get('role_id')
        user_id = input.get('user_id')
        type_id = input.get('type_id')
        resource_id = input.get('resource_id')
        return role_id, user_id, type_id, resource_id

    def _check_assign_ability(self, token, user, item):
        action_resources = self.get_action_resources(
            token, ['ASSIGN_USER', 'ASSIGN_SELF'])
        if self._is_self_assign(user, item.user.id):
            if not check_action(action_resources, 'ASSIGN_SELF',
                                item.type.name, item.resource_id):
                raise ForbiddenException(Err.OA0012, [])
        else:
            if not check_action(action_resources, 'ASSIGN_USER',
                                item.type.name, item.resource_id):
                raise ForbiddenException(Err.OA0012, [])

    def _check_input(self, role_id, user_id, type_id, resource_id,
                     register=False):
        required_fields = [('role_id', role_id), ('user_id', user_id)]
        if not register:
            required_fields.append(('type_id', type_id))

        for attr_name, attr_value in required_fields:
            if attr_value is None:
                raise WrongArgumentsException(Err.OA0031, [attr_name])
        integers_filds = [('role_id', role_id)]
        if not register:
            integers_filds.append(('type_id', type_id))
        for attr_name, attr_value in integers_filds:
            if not isinstance(attr_value, int):
                raise WrongArgumentsException(Err.OA0049, [attr_name])

    def create(self, **kwargs):
        token = kwargs.pop('token')
        self.check_create_restrictions(**kwargs)
        role_id, user_id, type_id, resource_id = self._get_input(**kwargs)
        self._check_input(role_id, user_id, type_id, resource_id)
        user = self.get_user(token)
        user_to_assign = self.get_user_by_id(user_id)
        type = self.get_type(type_id)
        assignable_roles, _ = RoleController(self.session, self._config).list(
            user_id, **{'token': token})
        # filter assignable roles by assignment level
        assignable_roles = list(filter(
            lambda x: type_id in list(
                map(lambda y: y.id, x.lvl.parent_tree)) + [x.lvl_id],
            assignable_roles))
        if role_id not in list(map(lambda x: x.id, assignable_roles)):
            raise ForbiddenException(Err.OA0017, [role_id, user_id])
        if type_id not in [user_to_assign.type_id] + list(
                map(lambda x: x.id, user_to_assign.type.child_tree)):
            raise ForbiddenException(Err.OA0018, [])
        # all() just helps to aviod errors because of
        # possibility to have multiple simillar assignments now
        existent_item = self.session.query(Assignment).filter(
            and_(
                Assignment.type_id == type.id,
                Assignment.resource_id == resource_id,
                Assignment.role_id == role_id,
                Assignment.deleted.is_(False),
                Assignment.user_id == user_id
            )
        ).all()
        if existent_item:
            item = existent_item.pop()
        else:
            item = Assignment(user_to_assign, type=type,
                              resource_id=resource_id, role_id=role_id)
            self._check_assign_ability(token, user, item)
            self.session.add(item)
            self.session.commit()
        return item

    def delete(self, item_id, **kwargs):
        item, _ = self.get(item_id)
        if kwargs.get('token'):
            token = kwargs.get('token')
            user = self.get_user(token)
            self._check_assign_ability(token, user, item)
        item.deleted_at = datetime.datetime.utcnow().timestamp()
        self.session.add(item)
        self.session.commit()

    def get(self, item_id, **kwargs):
        item = self.session.query(Assignment).filter(
            and_(
                Assignment.id == item_id,
                Assignment.deleted.is_(False)
            )
        ).one_or_none()
        if not item:
            raise NotFoundException(Err.OA0019, [item_id])
        if 'token' in kwargs:
            token = kwargs.pop('token')
            action_resources = self.get_action_resources(
                token, ['LIST_ROLES', 'LIST_USERS'])
            common_res = set(action_resources.get('LIST_ROLES')).intersection(
                action_resources.get('LIST_USERS'))
            if not any(filter(lambda x: x == (item.type.name,
                                              item.resource_id), common_res)):
                raise ForbiddenException(Err.OA0012, [])
        payload = ((item.type.name, item.resource_id),)
        scope_info = self.get_resources_info(payload).get(item.resource_id, {})
        return item, scope_info

    def edit(self, item_id, **input):
        raise NotImplementedError

    def list(self, **kwargs):
        user_id = kwargs.get('user_id')
        if not user_id:
            raise WrongArgumentsException(Err.OA0032, ['user_id'])
        query_set = self.session.query(
            Assignment.id,
            Assignment.resource_id,
            Assignment.type_id,
            Role.scope_id,
            Role.name,
            Role.id
        ).join(
            Role, and_(
                Role.deleted.is_(False),
                Role.id == Assignment.role_id)
        ).filter(
            and_(
                Assignment.deleted.is_(False),
                Assignment.user_id == user_id
            )
        ).all()
        result = list()
        for item in query_set:
            (assignment_id, assignment_resource, assignment_resource_type,
             role_scope, role_name, role_id) = item

            result.append(
                dict(assignment_id=assignment_id,
                     assignment_resource=assignment_resource,
                     assignment_resource_type=assignment_resource_type,
                     role_scope=role_scope,
                     role_name=role_name,
                     role_id=role_id))
        return result

    def my_assignments(self, **kwargs):
        token = kwargs.get('token')
        user = self.get_user(token)
        return self.list(user_id=user.id)

    def register(self, **kwargs):
        self.check_create_restrictions(**kwargs)
        role_id, user_id, type_id, resource_id = self._get_input(**kwargs)
        self._check_input(role_id, user_id, type_id, resource_id, register=True)
        user_to_assign = self.get_user_by_id(user_id)
        type_ = self.get_type(type_id)
        existent_item = self.session.query(Assignment).filter(
            and_(
                Assignment.type_id == type_.id,
                Assignment.resource_id == resource_id,
                Assignment.role_id == role_id,
                Assignment.deleted.is_(False),
                Assignment.user_id == user_id
            )
        ).all()
        if existent_item:
            item = existent_item.pop()
        else:
            item = Assignment(user_to_assign, type=type_,
                              resource_id=resource_id, role_id=role_id)
            self.session.add(item)
            self.session.commit()
        return item


class AssignmentAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AssignmentController
