import logging
import datetime
from sqlalchemy import and_, or_
from auth.auth_server.auth_token.macaroon import MacaroonToken
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import (Token, User, Assignment, Role,
                                            Action, RoleAction, Type)
from auth.auth_server.utils import get_context_values, get_digest
from tools.optscale_exceptions.common_exc import (UnauthorizedException,
                                                  ForbiddenException)

LOG = logging.getLogger(__name__)


class TokenStore(object):
    """
    Auth logic here
    """
    def __init__(self, session):
        self._session = session

    @property
    def session(self):
        return self._session

    def check_token_valid(self, token_str):
        token = self.session.query(Token).filter(
            Token.valid_until >= datetime.datetime.utcnow(),
            Token.digest == get_digest(token_str),
        ).all()
        if not token:
            raise UnauthorizedException(Err.OA0010, [])
        macaroon_token = MacaroonToken(token[0].user.salt, token[0].user.id)
        # additional check
        if not macaroon_token.verify(token_str):
            raise UnauthorizedException(Err.OA0011, [])

    def check_permissions(self, user, action_name, context, ass_type,
                          scope_id=None):
        actions = {action_name}
        if user is None:
            raise ForbiddenException(Err.OA0012, [])
        context_values = get_context_values(context)
        if scope_id and scope_id not in context_values:
            raise ForbiddenException(Err.OA0012, [])
        # requested level
        ass_type_ids = (
                [ass_type.id] + list(map(lambda x: x.id, ass_type.parent_tree))
        )
        assignments_query = self.session.query(Assignment).join(
            User, and_(
                User.id == user.id,
                Assignment.user_id == User.id,
                User.deleted.is_(False),
                User.is_active.is_(True)
            )
        ).join(
            Role, and_(
                Assignment.role_id == Role.id,
                Role.deleted.is_(False),
                Role.is_active.is_(True)
            )
        ).join(
            RoleAction, and_(
                RoleAction.role_id == Role.id,
            )
        ).join(Action).filter(
            and_(
                Assignment.type_id.in_(ass_type_ids),
                Assignment.deleted.is_(False),
                Action.name.in_(actions)
            )
        )
        if context:
            assignments_query = assignments_query.filter(
                or_(
                    Assignment.resource_id.is_(None),
                    Assignment.resource_id.in_(context_values)
                )
            )
        else:
            assignments_query = assignments_query.filter(
                Assignment.resource_id.is_(None)
            )

        assignments = assignments_query.all()
        if not assignments:
            LOG.warning('Access denied for user: %s, user type: %s action: %s'
                        ' context: %s', user.email, user.type, action_name,
                        str(context))
            raise ForbiddenException(Err.OA0012, [])
        return assignments

    def action_resources(self, user, action_list=None):
        """
        Returns list of sorted tuples action-resource
        [(resource-id, type, ACTION_NAME)]
        example:
        [('a8897a68-46d9-4a8d-bcc9-71df31049fd5', 'organization', 'ACTION1'),
        [('13ea5490-1eba-4884-99cd-10e0e8e47f98', 'pool', 'ACTION2')]]
        :param user: User instance
        :param action_list: list of actions names or None
        :return:
        """
        action_resources_query = self.session.query(
            Assignment.resource_id, Type.name, Action.name).join(
            Type, and_(
                Assignment.type_id == Type.id)).join(
            User, and_(
                User.id == user.id,
                Assignment.user_id == User.id,

                and_(
                    User.deleted.is_(False),
                    User.is_active.is_(True)))).join(
            Role, and_(
                Assignment.role_id == Role.id,
                Role.deleted.is_(False),
                Role.is_active.is_(True))).join(
            RoleAction, and_(
                RoleAction.role_id == Role.id)).join(
            Action, and_(
                Action.id == RoleAction.action_id)).filter(
            and_(
                Action.deleted.is_(False),
                Assignment.deleted.is_(False)
            )
        )
        if action_list:
            action_resources_query = action_resources_query.filter(
                Action.name.in_(action_list))

        action_resources = action_resources_query.order_by(
            Type.name, Action.name, Assignment.resource_id).all()
        return action_resources

    def bulk_action_resources(self, user_ids, action_list=None):
        """
        Returns map where key is user id and value is a list of sorted tuples
        (resource_id, type, action_name)
        """
        action_resources_query = self.session.query(
            Assignment.resource_id, Type.name, Action.name, User.id).join(
            Type, and_(
                Assignment.type_id == Type.id)).join(
            User, and_(
                User.id.in_(user_ids),
                Assignment.user_id == User.id,
                and_(
                    User.deleted.is_(False),
                    User.is_active.is_(True)))).join(
            Role, and_(
                Assignment.role_id == Role.id,
                Role.deleted.is_(False),
                Role.is_active.is_(True))).join(
            RoleAction, and_(
                RoleAction.role_id == Role.id)).join(
            Action, and_(
                Action.id == RoleAction.action_id)).filter(
            and_(
                Action.deleted.is_(False),
                Assignment.deleted.is_(False)
            )
        )
        if action_list:
            action_resources_query = action_resources_query.filter(
                Action.name.in_(action_list))

        action_resources = action_resources_query.order_by(
            Type.name, Action.name, Assignment.resource_id).all()
        result = {}
        for ar in action_resources:
            resource_id, type_name, action_name, user_id = ar
            if user_id not in result:
                result[user_id] = []
            result[user_id].append((resource_id, type_name, action_name))
        return result

    def auth_user_list(self, user_id_list, action_list, allowed_lvls,
                       context=None):
        """
        Returns list of sorted tuples user_id-action
        [(user_id, ACTION_NAME)]
        example:
        [('a8897a68-46d9-4a8d-bcc9-71df31049fd5', 'ACTION1'),
        [('13ea5490-1eba-4884-99cd-10e0e8e47f98', 'ACTION2')
        :param user_id_list: list of user ids
        :param action_list: list of action names
        :param allowed_lvls: list allowed (by type access lvl) lvl ids
        :param context: list of resource ids (str) or None
        :return:
        """
        auth_list_query = self.session.query(
            Assignment.user_id, Action.name
        ).join(
            User, and_(

                Assignment.user_id == User.id,
                and_(
                    User.deleted.is_(False),
                    User.is_active.is_(True))
            )
        ).join(
            Role, and_(
                Assignment.role_id == Role.id,
                Role.deleted.is_(False),
                Role.is_active.is_(True))
        ).join(

            RoleAction, and_(
                RoleAction.role_id == Role.id)
        ).join(
            Action, and_(
                Action.name.in_(action_list),
                Action.id == RoleAction.action_id,
                Action.deleted.is_(False))
        ).filter(
            and_(

                Assignment.deleted.is_(False),
                Assignment.type_id.in_(allowed_lvls),
                Assignment.user_id.in_(user_id_list),
                or_(
                    Assignment.resource_id.in_(context or []),
                    Assignment.resource_id.is_(None)
                )
            )
        )
        auth_list = auth_list_query.order_by(User.id, Action.name).all()
        return auth_list
