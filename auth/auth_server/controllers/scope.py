import logging

from ordered_set import OrderedSet
from auth.auth_server.auth_token.token_store import TokenStore
from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.models.models import Type

LOG = logging.getLogger(__name__)


class ScopeController(object):
    def __init__(self, db_session, config=None):
        self._session = db_session
        self._config = config
        self._db = None
        self.access_token_store = TokenStore(db_session)

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        self._session = val

    def _list_types(self):
        type_dict = dict()
        types = self.session.query(Type).filter(
            Type.deleted.is_(False)
        ).all()
        for type_ in types:
            type_dict[type_.name] = {
                'scope_type_id': type_.id,
                'assignable': type_.assignable}
        return type_dict

    def _action_resourses(self, action, filter_assignable=False, **kwargs):
        token = kwargs.get('token')
        base_controller = BaseController(self.session, self._config)
        user = base_controller.get_user(token)
        # get db assignments
        action_resources = self.access_token_store.action_resources(
            user, [action])
        if not action_resources:
            return []
        downward_hierarchy = base_controller.get_downward_hierarchy(
            'root', None)
        sorted_action_res = sorted(action_resources,
                                   key=base_controller.get_type_sorter())
        aset = OrderedSet(sorted_action_res)
        base_controller.render(sorted_action_res, aset, downward_hierarchy)
        payload = list(map(lambda x: (x[1], x[0]), aset))
        resources_info = base_controller.get_resources_info(payload)
        res_type_dict = self._list_types()
        resources = list(
            map(lambda x: {'scope_id': x[0], 'scope_type': x[1]}, aset))
        response = [dict(list(res.items()) + [(
            'scope_name', resources_info.get(res['scope_id'], {}).get(
                'name', 'Root' if res['scope_type'] == 'root' else None))] +
            list(res_type_dict.get(res['scope_type'],
                                   {'scope_type_id': None,
                                    'assignable': None}).items())
        ) for res in resources]
        if filter_assignable:
            response = list(filter(lambda x: x['assignable'], response))
        return response

    def scope_create_user(self, **kwargs):
        return self._action_resourses('CREATE_USER', True, **kwargs)

    def _get_types_map(self):
        types_map = dict()
        types = self.session.query(Type).filter(
            Type.deleted.is_(False)).all()
        for type_ in types:
            types_map[type_.name] = type_.id
        return types_map

    def scope_create_role(self, **kwargs):
        return self._action_resourses('CREATE_ROLE', True, **kwargs)

    def scope_assign_user(self, user_id, role_id, **kwargs):
        base_controller = BaseController(self.session, self._config)
        target_user = base_controller.get_user_by_id(user_id)
        role = base_controller.get_role_by_id(role_id)

        downward_hierarchy = base_controller.get_downward_hierarchy(
            target_user.type.name, target_user.scope_id)
        downward_hierarchy_ids = base_controller.get_downward_hierarchy_ids(
            downward_hierarchy)

        role_allowed_types = set(
            [role.lvl.id] + list(map(lambda x: x.id, role.lvl.parent_tree)))

        def _filter_scope(action_dict):
            return (action_dict['scope_type_id'] in role_allowed_types and
                    action_dict['scope_id'] in downward_hierarchy_ids)

        aset = self._action_resourses('ASSIGN_USER', **kwargs)
        aset = list(filter(_filter_scope, aset))
        return aset


class ScopeAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ScopeController
