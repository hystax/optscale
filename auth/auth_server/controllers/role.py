import logging
import time
from sqlalchemy import and_
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import IntegrityError
from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import (Role, Action, RoleAction,
                                            ActionGroup, RolePurpose)
from auth.auth_server.utils import (check_action, get_input, unique_list,
                                    check_string_attribute, is_uuid,
                                    pop_or_raise, get_context_values)
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  NotFoundException,
                                                  ForbiddenException,
                                                  ConflictException)

LOG = logging.getLogger(__name__)


class RoleController(BaseController):
    def _get_model_type(self):
        return Role

    def _get_role_by_id(self, id_):
        role = self.session.query(Role).get(id_)
        if not role or role.deleted:
            raise NotFoundException(Err.OA0030, [id_])
        return role

    def _get_input(self, **input_):
        keys = ['name', 'type_id', 'lvl_id', 'shared', 'is_active', 'scope_id',
                'deleted_at', 'description']
        return get_input(keys, **input_)

    def _check_input(self, name, type_id, lvl_id, is_active, scope_id,
                     description, is_edit=False):
        if not is_edit:
            for attr_name, attr_value in (('name', name),
                                          ('type_id', type_id),
                                          ('lvl_id', lvl_id)):
                if attr_value is None:
                    raise WrongArgumentsException(Err.OA0031, [attr_name])
        if name is not None:
            check_string_attribute('name', name)
        if type_id is not None and not isinstance(type_id, int):
            raise WrongArgumentsException(Err.OA0049, ['type_id'])
        if description:
            check_string_attribute('description', description)
        if lvl_id is not None:
            if not isinstance(lvl_id, int):
                raise WrongArgumentsException(Err.OA0049, ['lvl_id'])
            res_type = self.get_type(type_id)
            allowed_lvls = ([x.id for x in res_type.child_tree] + [type_id])
            if lvl_id not in allowed_lvls:
                raise WrongArgumentsException(Err.OA0034, [res_type.name])
        if scope_id is not None:
            if not isinstance(scope_id, str):
                raise WrongArgumentsException(Err.OA0033, ['scope_id'])
            if not scope_id or not is_uuid(scope_id):
                raise WrongArgumentsException(Err.OA0054, [])

    def _is_self_edit(self, user, current_role_id):
        assignments = [a.role_id for a in user.assignments]
        return int(current_role_id) in assignments

    def _check_edit_permissions(self, token, current_role):
        user = self.get_user(token)
        is_self_edit = self._is_self_edit(user, current_role.id)
        action_resources = self.get_action_resources(
            token, ['EDIT_ROLES', 'EDIT_OWN_ROLES', 'EDIT_SUBLEVEL_ROLES'])

        if is_self_edit:
            return check_action(action_resources, 'EDIT_OWN_ROLES',
                                current_role.type.name, current_role.scope_id)
        else:
            edit_roles = check_action(action_resources, 'EDIT_ROLES',
                                      current_role.type.name,
                                      current_role.scope_id)
            if edit_roles:
                return True
            else:
                if user.type_id in [x.id for x in
                                    current_role.type.parent_tree]:
                    return check_action(action_resources,
                                        'EDIT_SUBLEVEL_ROLES',
                                        current_role.type.name,
                                        current_role.scope_id)
        return False

    def _check_role_exists(self, name, type_id, scope_id):
        roles = self.session.query(Role).filter(
            and_(
                Role.name == name,
                Role.type_id == type_id,
                Role.scope_id == scope_id,
                Role.deleted.is_(False)
            )
        ).all()
        if roles:
            raise ConflictException(Err.OA0035, [name])

    def get(self, item_id, **kwargs):
        query = self.session.query(self.model_type).filter(
            self.model_type.id == item_id,
            self.model_type.deleted.is_(False))
        filter_params = self._get_input(**kwargs)
        if len(filter_params) > 0:
            query = query.filter_by(filter_params)
        try:
            role = query.one_or_none()
        except MultipleResultsFound as e:
            raise WrongArgumentsException(Err.OA0061, [str(e)])
        if not role:
            return None
        if 'token' in kwargs:
            token = kwargs.pop('token')
            user = self.get_user(token)
            if not self._is_self_edit(user, item_id):
                action_resources = self.get_action_resources(
                    token, ['LIST_ROLES'])
                if not check_action(action_resources, 'LIST_ROLES',
                                    role.type.name, role.scope_id):
                    context = self.get_context(user.type.name, user.scope_id)
                    context_values = get_context_values(context) + [None]
                    if not (role.shared and role.scope_id in context_values):
                        raise ForbiddenException(Err.OA0012, [])
                    if (role.shared and user.type_id not in [role.lvl_id] +
                            list(map(lambda x: x.id, role.lvl.parent_tree))):
                        raise ForbiddenException(Err.OA0012, [])

        lvls = ([x.id for x in role.lvl.child_tree] + [role.lvl_id])
        action_groups = self.session.query(ActionGroup).join(
            Action,
            and_(
                ActionGroup.id == Action.action_group_id,
                Action.deleted.is_(False)
            )).filter(
            and_(
                Action.type_id.in_(lvls),
                ActionGroup.deleted.is_(False)
            )
        ).all()
        role_actions = self.session.query(RoleAction).join(
            Role,
            and_(
                RoleAction.role_id == Role.id,
                Role.deleted.is_(False),
            )
        ).join(
            Action,
            and_(
                RoleAction.action_id == Action.id,
                Action.deleted.is_(False)
            )
        ).filter(
            and_(
                RoleAction.role_id == role.id,
                Role.lvl_id.in_(lvls)
            )).all()
        allowed_actions = [role_action.action for role_action in role_actions]
        actions = {
            # TODO: Add unit tests for exclude action for same ag
            action_group.name: {
                action.name: action in allowed_actions for action in
                filter(lambda x: x.type_id in lvls,
                       action_group.actual_actions)
            } for action_group in action_groups}
        payload = ((role.type.name, role.scope_id), )
        scope_info = self.get_resources_info(payload).get(role.scope_id, {})

        return {"id": role.id,
                "name": role.name,
                "type_id": role.type_id,
                "lvl_id": role.lvl_id,
                "is_active": role.is_active,
                "description": role.description,
                "shared": role.shared,
                "scope_id": role.scope_id,
                "scope_name": scope_info.get('name'),
                "actions": actions
                }

    def create(self, **kwargs):
        token = kwargs.pop('token')
        self.check_create_restrictions(**kwargs)
        filtered_input = self._get_input(**kwargs)
        self._check_input(filtered_input.get("name"),
                          filtered_input.get("type_id"),
                          filtered_input.get("lvl_id"),
                          filtered_input.get("is_active"),
                          filtered_input.get("scope_id"),
                          filtered_input.get("description"))
        name = filtered_input.get('name')
        type_id = filtered_input.get('type_id')
        scope_id = filtered_input.get('scope_id')
        type_ = self.get_type(filtered_input["type_id"])
        self.check_permissions(token,
                               type_.name,
                               filtered_input.get("scope_id"),
                               action='CREATE_ROLE')
        self._check_role_exists(name, type_id, scope_id)
        role = super().create(**filtered_input)
        return role

    def delete(self, item_id, **kwargs):
        token = kwargs.get('token')
        role = self._get_role_by_id(item_id)
        type_ = self.get_type(role.type_id)
        self.check_permissions(token, type_.name,
                               role.scope_id, action='DELETE_ROLE')
        role.deleted_at = time.time()
        self.session.add(role)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OA0061, [str(ex)])

    def edit(self, item_id, **input_):
        current_role = self._get_role_by_id(item_id)
        token = input_.pop('token')
        new_actions_grouped = pop_or_raise(input_, 'actions')
        self.check_update_restrictions(**input_)
        self._check_input(input_.get("name"),
                          input_.get("type_id"),
                          input_.get("lvl_id"),
                          input_.get("is_active"),
                          input_.get("scope_id"),
                          input_.get("description"),
                          is_edit=True)
        if not self._check_edit_permissions(token, current_role):
            raise ForbiddenException(Err.OA0012, [])
        if new_actions_grouped is not None:
            allowed_lvls = ([x.id for x in current_role.lvl.child_tree] +
                            [current_role.lvl_id])
            allowed_actions = self.session.query(Action).filter(
                Action.type_id.in_(allowed_lvls)
            ).all()
            allowed_actions = {r.name: r for r in allowed_actions}
            new_actions = {}
            action_groups = self.session.query(ActionGroup).all()
            action_groups_names = list(map(lambda x: x.name, action_groups))
            for action_group, v in new_actions_grouped.items():
                if action_group not in action_groups_names:
                    raise WrongArgumentsException(Err.OA0051, [action_group])
                new_actions.update(v)
            for action_name, state in new_actions.items():
                if action_name not in allowed_actions:
                    raise WrongArgumentsException(Err.OA0036, [action_name])
                if state:
                    if (allowed_actions[action_name] not in
                            current_role.actions):
                        current_role.assign_action(
                            allowed_actions[action_name])
                else:
                    if allowed_actions[action_name] in current_role.actions:
                        current_role.remove_action(
                            allowed_actions[action_name])

        filtered_input = self._get_input(**input_)
        if filtered_input:
            self.session.query(self.model_type).filter_by(id=item_id).update(
                filtered_input)
        self.session.add(current_role)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OA0061, [str(ex)])
        return self.get(item_id)

    def list_assignable_to_user_id(self, assignable_to_id, action_resources,
                                   list_roles):
        user = self.get_user_by_id(assignable_to_id)
        if not ((user.type.name, user.scope_id) in action_resources[
            'LIST_ROLES'] and (user.type.name, user.scope_id) in
                action_resources['LIST_USERS']):
            return []
        context = self.get_context(user.type.name, user.scope_id)
        context_values = get_context_values(context)
        downward_hierarchy = self.get_downward_hierarchy(user.type.name,
                                                         user.scope_id)
        shared_roles = [r for r in list_roles if
                        r.shared and r.scope_id in list(context_values) +
                        [None] and r.lvl_id in list(map(
                            lambda x: x.id, user.type.child_tree)) +
                        [user.type_id]]

        downward_ids = self.get_downward_hierarchy_ids(downward_hierarchy)
        filtered_list_roles = [r for r in list_roles if
                               r.scope_id in downward_ids]
        # TODO: unit test
        return unique_list(filtered_list_roles + shared_roles)

    def list_assignable_to_current_user(self, current_user,
                                        action_resources,
                                        list_roles):
        context = self.get_context(
            current_user.type.name, current_user.scope_id)
        context_values = get_context_values(context) + [None]
        shared_roles = [r for r in list_roles if
                        r.shared and r.scope_id in context_values and
                        r.lvl_id in list(
                            map(lambda x: x.id, current_user.type.child_tree)
                        ) + [current_user.type_id]]
        filtered_list_roles = list(filter(
            lambda x: (x.type.name, x.scope_id) in action_resources[
                'LIST_ROLES'], list_roles))
        # TODO: unit test
        return unique_list(filtered_list_roles + shared_roles)

    def list(self, assignable, **kwargs):
        token = kwargs.pop('token')
        current_user = self.get_user(token)
        action_resources = self.get_action_resources(token, ['LIST_ROLES',
                                                             'LIST_USERS'])
        list_roles = super().list(**kwargs)

        if assignable:
            queryset = self.list_assignable_to_user_id(assignable,
                                                       action_resources,
                                                       list_roles)
        else:
            queryset = self.list_assignable_to_current_user(current_user,
                                                            action_resources,
                                                            list_roles)

        payload = list(map(lambda x: (x.type.name, x.scope_id), queryset))
        resources_info = self.get_resources_info(payload)
        return queryset, resources_info

    def get_purposed_role(self, purpose):
        self._validate_purpose(purpose)
        query = self.session.query(self.model_type).filter(
            self.model_type.deleted.is_(False),
            self.model_type.purpose == purpose
        )
        role = query.one_or_none()
        if not role:
            raise NotFoundException(Err.OA0057, [purpose])
        return role

    @staticmethod
    def _validate_purpose(purpose):
        if not purpose:
            raise WrongArgumentsException(Err.OA0031, ['purpose'])
        try:
            RolePurpose(purpose)
        except ValueError:
            raise WrongArgumentsException(Err.OA0058, [purpose])


class RoleAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RoleController
