import time
import logging
import requests
from ordered_set import OrderedSet
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound

from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import (Token, Type, User, Role,
                                            PermissionKeys, VerificationCode)
from auth.auth_server.auth_token.token_store import TokenStore
from auth.auth_server.utils import Config, popkey, get_digest
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  UnauthorizedException,
                                                  NotFoundException,
                                                  ForbiddenException)
from tools.optscale_exceptions.http_exc import handle503
from optscale_client.rest_api_client.client_v2 import Client as RestApiClient
import tools.optscale_time as opttime

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

    def _check_input(self, **input_):
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
            LOG.warning('immutable parameters %s: %s',
                        self.model_type, matches_string)
            raise WrongArgumentsException(Err.OA0021, [matches_string])
        unexpected_params = list(filter(
            lambda x:
            x not in self.model_column_list and x not in restrictions,
            kwargs.keys()))
        if unexpected_params:
            unexpected_string = ', '.join(unexpected_params)
            LOG.warning('Unexpected parameters %s: %s',
                        self.model_type, unexpected_string)
            raise WrongArgumentsException(Err.OA0022, [unexpected_string])

    def _get_model_type(self):
        raise NotImplementedError

    def get_user(self, token):
        token = self.session.query(Token).get(get_digest(token))
        if not token or not token.valid_until > opttime.utcnow():
            raise UnauthorizedException(Err.OA0023, [])
        return token.user

    def get_user_by_id(self, id_):
        user = self.session.query(User).get(id_)
        if not user or user.deleted:
            raise NotFoundException(Err.OA0024, [id_])
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

    def get_role_by_id(self, id_):
        role = self.session.query(Role).get(id_)
        if not role or role.deleted:
            raise NotFoundException(Err.OA0025, [id_])
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
            LOG.info("Access granted: %s", ','.join(
                str(x) for x in assignments))
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

    def render(self, action_resources, aset, hierarchy):
        def render_item(node, action, collect=False):
            if isinstance(node, dict):
                for entity_type, entities in node.items():
                    if isinstance(entities, dict):
                        for entity_id, children in entities.items():
                            start_collect = collect or entity_id == target_id
                            if start_collect:
                                aset.add((entity_id, entity_type, action))
                            render_item(children, action, start_collect)
                    elif isinstance(entities, list):
                        for entity_id in entities:
                            aset.add((entity_id, entity_type, action))

        for target_id, target_type, action in action_resources:
            render_item(hierarchy, action)

    def format_user_action_resources(self, action_resources, action_list):
        resource_set = set()
        aset = OrderedSet()
        for id_, res_type, _ in action_resources:
            resource_set.add((id_, res_type))

        ordered_set = sorted(resource_set, key=self.get_type_sorter())
        for id_, res_type in ordered_set:
            if id_ in [x[0] for x in aset]:
                # downward hierarchy was derived from a higher entity
                continue
            try:
                response = self.get_downward_hierarchy(res_type, id_)
            except requests.exceptions.HTTPError as exc:
                if exc.response.status_code == 404:
                    # resource is deleted
                    continue
                raise
            self.render(action_resources, aset, response)
        result = dict(map(lambda k: (k, list()), action_list))
        for i in aset:
            res_id, res_type, action = i
            result[action].append((res_type, res_id))
        return result

    def get_action_resources(self, token=None, action_list=None,
                             user_id=None):
        """
        Returns List of actions with corresponding resources
        :return:
         {ACTION_NAME: [(type, uuid), (type, uuid)]}
        """
        if action_list is None:
            action_list = list()
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
        _, res_info = self.restapi_client.resources_get(payload)
        return res_info

    @handle503
    def get_context(self, res_type, uuid):
        if not uuid:
            return {}
        _, context = self.restapi_client.context_get(res_type, uuid)
        return context

    @handle503
    def get_downward_hierarchy(self, res_type, uuid):
        _, hierarchy = self.restapi_client.auth_hierarchy_get(
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

    def use_verification_code(self, email, code):
        if not email or not code:
            return
        now = opttime.utcnow()
        return self.session.query(VerificationCode).filter(
            and_(
                VerificationCode.email == email,
                VerificationCode.deleted.is_(False),
                VerificationCode.code == get_digest(str(code)),
                VerificationCode.valid_until > now
            )
        ).update({
            VerificationCode.deleted_at: int(now.timestamp())
        })

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
