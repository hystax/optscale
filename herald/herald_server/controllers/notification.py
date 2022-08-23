from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_


from herald_server.controllers.base import BaseController
from herald_server.controllers.reaction import ReactionController
from herald_server.controllers.base_async import BaseAsyncControllerWrapper
from herald_server.models.models import (
    Notification, Reaction, FilterCriteria, Field)
from herald_server.exceptions import Err

from optscale_types.utils import check_string_attribute
from optscale_exceptions.common_exc import WrongArgumentsException


class NotificationController(BaseController):
    def _get_model_type(self):
        return Notification

    @property
    def create_restrictions(self):
        return super().create_restrictions + ['filter', 'reactions']

    @property
    def update_restrictions(self):
        return super().update_restrictions + ['filter', 'reactions']

    def _validate_creation(self, **kwargs):
        # TODO: check that user has POLL_EVENT
        #  for event_object_type:event_object_id
        self.check_create_restrictions(**kwargs)
        filter_str = kwargs.get('filter')
        check_string_attribute('filter', filter_str)
        self._validate_reactions(kwargs.get('reactions'))

    def _validate_edit(self, **kwargs):
        # TODO: check that user has POLL_EVENT
        # for event_object_type:event_object_id
        self.check_update_restrictions(**kwargs)
        filter_str = kwargs.get('filter')
        if filter_str is not None:
            check_string_attribute('filter', filter_str)
        self._validate_reactions(kwargs.get('reactions'))

    @staticmethod
    def _validate_reactions(reactions):
        if reactions is not None and (not isinstance(reactions, list) or any(
                filter(lambda x: not isinstance(x, dict), reactions))):
            raise WrongArgumentsException(Err.G0012, [])

    def _list_fields(self):
        query = self.session.query(Field).filter(Field.deleted.is_(False))
        return query.all()

    @property
    def fields_map(self):
        fields = self._list_fields()
        return dict(((field.name, field.id) for field in fields))

    def _parse_filter(self, filter_str):
        criterias = []

        fields_map = self.fields_map
        for criteria_str in filter_str.split(' '):

            try:
                field_name, value = criteria_str.split(':')
            except ValueError:
                raise WrongArgumentsException(
                    Err.G0013,
                    [criteria_str])

            field_id = fields_map.get(field_name)
            if field_id is None:
                raise WrongArgumentsException(Err.G0014, [field_name])

            criterias.append(FilterCriteria(field_id=field_id, value=value))

        return criterias

    def create(self, **kwargs):
        self._validate_creation(**kwargs)
        reactions = []
        if 'reactions' in kwargs:
            reactions = kwargs.pop('reactions') or []
        filter_str = kwargs.pop('filter')

        notification = Notification(**kwargs)
        for reaction in reactions:
            notification.reactions.append(ReactionController(
                self.session, self._config).create(**reaction))

        notification.criterias = self._parse_filter(filter_str)

        self.session.add(notification)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.G0027, [str(ex)])
        return notification

    def get(self, item_id, **kwargs):
        return super().get(item_id)

    def delete(self, item_id):
        super().delete(item_id)

    def edit(self, item_id, **kwargs):
        self._validate_edit(**kwargs)

        notification = self.get(item_id)
        reactions = kwargs.pop('reactions', None)
        if reactions is not None:
            notification.reactions = [
                ReactionController(self.session, self._config).create(
                    **reaction) for reaction in reactions
            ]

        filter_str = kwargs.pop('filter', None)
        if filter_str is not None:
            notification.criterias = self._parse_filter(filter_str)
        notification = super().edit(item_id, **kwargs)
        return notification

    def list(self, user_id):
        return super().list(user_id=user_id)

    def _event_user_reactions(self, event):
        filtering_fields = self._list_fields()

        event_based_filters = []

        for field in filtering_fields:
            event_field_value = event.get(field.name)
            if event_field_value is None:
                continue
            if isinstance(event_field_value, bool):
                event_field_value = str(event_field_value).lower()
            event_based_filters.append(and_(
                FilterCriteria.field_id == field.id,
                FilterCriteria.value == event_field_value
            ))

        query = self.session.query(
            Notification.user_id,
            Reaction
        ).filter(
            Notification.deleted.is_(False),
        ).join(
            Notification.criterias
        ).filter(
            or_(*event_based_filters)
        ).join(
            Notification.reactions
        )

        return query.all()

    def _authorized_users(self, user_ids, event):
        authorized_users = set()

        authorized_user_actions = self.authorize_users(
            user_ids, ['POLL_EVENT'], event.get('object_type'), event.get('object_id'))
        for user_id, authorized_actions in authorized_user_actions.items():
            if 'POLL_EVENT' in authorized_actions:
                authorized_users.add(user_id)

        return authorized_users

    def _filter_user_access(self, event, user_reactions):
        user_ids = [user_id for user_id, _ in user_reactions]
        authorized_user_ids = self._authorized_users(user_ids, event)
        return [reaction for user_id, reaction in user_reactions
                if user_id in authorized_user_ids]

    def event_user_reactions(self, event):
        user_reactions = self._event_user_reactions(event)
        return self._filter_user_access(event, user_reactions)


class NotificationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return NotificationController
