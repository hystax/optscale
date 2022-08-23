from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
import time
import datetime
import logging
import requests
from ordered_set import OrderedSet
from sqlalchemy.orm.exc import MultipleResultsFound

from auth_server.exceptions import Err
from auth_server.models.models import Token, Type, User, Role, PermissionKeys
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            UnauthorizedException,
                                            NotFoundException,
                                            ForbiddenException)
from optscale_exceptions.http_exc import handle503
from auth_server.auth_token.token_store import TokenStore

from auth_server.utils import Config, popkey, get_digest
from rest_api_client.client_v2 import Client as RestApiClient

LOG = logging.getLogger(__name__)


class BaseController(object):
    def __init__(self, db_session, config=None):
        self._session = db_session
        self._config = config
        self._db = None
        self._model_type = None
        self.access_token_store = TokenStore(db_session)
        self._restapi_client = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        self._session = val

    @property
    def model_type(self):
        if self._model_type is None:
            self._model_type = self._get_model_type()
        return self._model_type

    @property
    def restapi_client(self):
        if self._restapi_client is None:
            self._restapi_client = RestApiClient(
                url=Config().restapi_url,
                secret=Config().cluster_secret)
        return self._restapi_client

    @property
    def model_column_list(self):
        return list(map(lambda x: str(x.name),
                        self.model_type.__table__.columns))

    def _check_input(self, **input):
        raise NotImplementedError

    @property
    def create_restrictions(self):
        return self._get_restrictions(PermissionKeys.is_creatable)

    @property
    def update_restrictions(self):
        return self._get_restrictions(PermissionKeys.is_updatable)

    def _get_restrictions(self, filter_by):
        res = list(
            map(lambda x: x.name, list(
                filter(lambda x: x.info.get(filter_by) is True,
                       self._get_model_type().__table__.c))))
        return res

    def check_update_restrictions(self, **kwargs):
        self._check_restrictions(self.update_restrictions, **kwargs)

    def check_create_restrictions(self, **kwargs):
        self._check_restrictions(self.create_restrictions, **kwargs)

    def _check_restrictions(self, restrictions, **kwargs):
        immutables = list(filter(
            lambda x: x not in restrictions, self.model_column_list))
        immutables_matches = list(filter(lambda x: x in kwargs, immutables))
        if immutables_matches:
            matches_string = ', '.join(immutables_matches)
            LOG.warning('immutable parameters %s: %s' %
                        (self.model_type, matches_string))
            raise WrongArgumentsException(Err.OA0021, [matches_string])
        unexpected_params = list(filter(
            lambda x:
            x not in self.model_column_list and x not in restrictions,
            kwargs.keys()))
        if unexpected_params:
            unexpected_string = ', '.join(unexpected_params)
            LOG.warning('Unexpected parameters %s: %s' %
                        (self.model_type, unexpected_string))
            raise WrongArgumentsException(Err.OA0022, [unexpected_string])

    def _get_model_type(self):
        raise NotImplementedError

    def get_user(self, token):
        token = self.session.query(Token).get(get_digest(token))
        if not token or not token.valid_until > datetime.datetime.utcnow():
            raise UnauthorizedException(Err.OA0023, [])
        return token.user

    def get_user_by_id(self, id):
        user = self.session.query(User).get(id)
        if not user or user.deleted:
            raise NotFoundException(Err.OA0024, [id])
        return user

    def get_users_by_ids(self, ids):
        users = self.session.query(User).filter(
            User.id.in_(ids),
            User.deleted.is_(False),
        ).all()
        user_ids = {u.id for u in users}
        not_found_users = set(ids) - user_ids
        if not_found_users:
            raise NotFoundException(Err.OA0024, [not_found_users.pop()])
        return users

    def get_role_by_id(self, id):
        role = self.session.query(Role).get(id)
        if not role or role.deleted:
            raise NotFoundException(Err.OA0025, [id])
        return role

    def get_type_by_name(self, type_name):
        scope_types = self.session.query(Type).filter_by(name=type_name).all()
        if not scope_types:
            raise WrongArgumentsException(Err.OA0020, [type_name])
        return scope_types[0]

    def get_type(self, type_id):
        scope_type = self.session.query(Type).get(type_id)
        if not scope_type:
            raise WrongArgumentsException(Err.OA0026, [type_id])
        return scope_type

    @property
    def context_level(self):
        root_node = self.session.query(Type).filter_by(
            name='root').one_or_none()
        if not root_node:
            raise ValueError('No root node')
        type_list = [root_node.name] + list(map(lambda x: x.name,
                                                root_node.child_tree))

        return dict(zip(range(len(type_list)), type_list))

    def check_permissions(self, token, res_type, scope_id, action):
        try:
            context = self.get_context(res_type, scope_id)
            scope_type_name = self.context_level[len(context)]
            try:
                scope_type = self.session.query(Type).filter(
                    and_(
                        Type.deleted.is_(False),
                        Type.name == scope_type_name,
                    )
                ).one_or_none()
            except MultipleResultsFound as e:
                raise WrongArgumentsException(Err.OA0061, [str(e)])
            if not scope_type:
                raise WrongArgumentsException(Err.OA0027, [scope_type_name])

            if res_type not in context:
                scope_id = None
            # get initiator user
            user = self.get_user(token)
            assignments = TokenStore(session=self.session).check_permissions(
                user, action, context, scope_type, scope_id)
            LOG.info("Access granted: %s" % ','.join(map(lambda x: str(x),
                                                         assignments)))
            return assignments

        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 404:
                raise NotFoundException(Err.OA0028, [res_type, scope_id])
            if exc.response.status_code == 400:
                raise ForbiddenException(Err.OA0012, [])
            raise

    def get_types(self):
        return self.session.query(Type).filter(
            Type.deleted.is_(False)).all()

    def render(self, action_resources, action_set, hierarchy):
        types = self.get_types()
        ordered_types = [x.name for x in sorted(types, key=lambda x: x.id)]
        # map of any hierarchy id <> related hierarchy part
        id_item_hierarchy_map = {}
        for i, type_ in enumerate(ordered_types):
            # todo: create common approach without hardcode
            # in root case id will be "null"
            if i == 0:
                id_item_hierarchy_map[None] = hierarchy[type_]['null']
            elif i == len(ordered_types) - 1:  # last type doesn't have children
                continue
            else:
                for _id in id_item_hierarchy_map.copy().keys():
                    if type_ in id_item_hierarchy_map[_id]:
                        id_item_hierarchy_map.update(
                            id_item_hierarchy_map[_id][type_])

        def render_item(res_id, res_type, action):
            if res_type == ordered_types[-1]:
                return
            down_hierarchy = id_item_hierarchy_map.get(res_id, {})
            next_type = ordered_types[ordered_types.index(res_type) + 1]
            for child_id in down_hierarchy.get(next_type, []):
                action_set.add((child_id, next_type, action))
                render_item(child_id, next_type, action)

        for res_id, res_type, action in action_resources:
            render_item(res_id, res_type, action)

    def format_user_action_resources(self, action_resources, action_list):
        response = self.get_downward_hierarchy('root', None)
        aset = OrderedSet(action_resources)

        self.render(action_resources, aset, response)

        result = dict(map(lambda k: (k, list()), action_list))
        for i in aset:
            res_id, res_type, action = i
            result[action].append((res_type, res_id))
        return result

    def get_action_resources(self, token=None, action_list=list(),
                             user_id=None):
        """
        Returns List of actions with corresponding resources
        :return:
         {ACTION_NAME: [(type, uuid), (type, uuid)]}
        """
        if not isinstance(action_list, list):
            return TypeError('action_list should be list')
        if user_id:
            user = self.get_user_by_id(user_id)
        else:
            user = self.get_user(token)
        action_resources = TokenStore(session=self.session).action_resources(
            user, action_list)
        return self.format_user_action_resources(action_resources, action_list)

    def get_bulk_action_resources(self, user_ids, action_list=None):
        if action_list is None:
            action_list = []
        self.get_users_by_ids(user_ids)
        user_action_resources = TokenStore(
            session=self.session).bulk_action_resources(user_ids, action_list)
        result = {}
        for user_id, action_resources in user_action_resources.items():
            result[user_id] = self.format_user_action_resources(
                action_resources, action_list)
        return result

    @handle503
    def get_resources_info(self, payload):
        code, res_info = self.restapi_client.resources_get(payload)
        return res_info

    @handle503
    def get_context(self, res_type, uuid):
        if not uuid:
            return {}
        code, context = self.restapi_client.context_get(res_type, uuid)
        return context

    @handle503
    def get_downward_hierarchy(self, res_type, uuid):
        code, hierarchy = self.restapi_client.auth_hierarchy_get(
            res_type, uuid)
        return hierarchy

    def get_type_sorter(self):
        types = self.get_types()
        sorter_dict = {}
        for type_ in types:
            sorter_dict[type_.name] = type_.id
        return lambda x: sorter_dict.get(x[1])

    def get_downward_hierarchy_ids(self, downward_hierarchy):
        res = []

        def nested_dict_iter(nested):
            for key, value in nested.items():
                if self.get_type_sorter()((None, key)) is None:
                    key = key if key != 'null' else None
                    res.append(key)
                if isinstance(value, dict):
                    nested_dict_iter(value)
                else:
                    res.extend(value)

        nested_dict_iter(downward_hierarchy)
        return res

    def create(self, **kwargs):
        model_type = self._get_model_type()

        item = model_type(**kwargs)
        popkey(kwargs, 'password')
        LOG.info("Creating %s with parameters %s", model_type.__name__,
                 kwargs)

        self.session.add(item)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OA0061, [str(ex)])
        return item

    def get(self, item_id, **kwargs):
        query = self.session.query(self.model_type).filter(
            self.model_type.id == item_id,
            self.model_type.deleted.is_(False))
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        res = query.all()
        if len(res) > 1:
            raise WrongArgumentsException(Err.OA0029, [])
        if len(res) == 1:
            return res[0]

    def edit(self, item_id, **kwargs):
        try:
            if kwargs:
                self.session.query(
                    self.model_type).filter_by(id=item_id).update(kwargs)
                self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OA0061, [str(ex)])
        return self.get(item_id)

    def delete(self, item_id, **kwargs):
        LOG.info("Deleting %s with id %s", self.model_type.__name__, item_id)
        self.edit(item_id, deleted_at=time.time())

    def list(self, **kwargs):
        query = self.session.query(self.model_type).filter(
            self.model_type.deleted.is_(False))
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        return query.all()
