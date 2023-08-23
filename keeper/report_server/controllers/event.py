import logging
import hashlib
from datetime import datetime
from mongoengine.errors import ValidationError, DoesNotExist
from mongoengine.queryset.visitor import Q

from keeper.report_server.exceptions import Err
from keeper.report_server.model import Event, ReadEvent
from keeper.report_server.controllers.event_base import EventBaseController
from keeper.report_server.controllers.base_async import BaseAsyncControllerWrapper
from keeper.report_server.utils import _check_filter_list


from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException,
    NotFoundException,
    ForbiddenException
)


LOG = logging.getLogger(__name__)


class EventCountController(EventBaseController):

    def get_count(self, **kwargs):
        token = kwargs.get('token')
        ack_only = kwargs.get('ack_only', False)
        levels = kwargs.get('levels', [])
        result = {"count": 0, "levels": []}
        _check_filter_list(levels, 'levels')
        org_id = kwargs.get('organization_id')
        if org_id is None:
            return result
        user_id = self.get_user_id_by_token(token)
        reads = self.get_reads(user_id)
        events = Event.objects(
            Q(organization_id=org_id) & Q(id__nin=list(reads.keys())))
        if levels:
            events = events(Q(level__in=levels))
        if ack_only:
            events = events(Q(ack=True))
        levels = list(frozenset(map(lambda x: x.level, events)))
        result['levels'] = levels
        result['count'] = events.count()
        return result


class EventCountAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return EventCountController


class EventController(EventBaseController):

    @staticmethod
    def _get_event(id):
        try:
            event = Event.objects.get(id=id)
        except (ValidationError, DoesNotExist):
            raise NotFoundException(Err.OK0004, [Event.__name__, id])
        return event

    @staticmethod
    def _check_limit(limit):
        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                raise WrongArgumentsException(
                    Err.OK0015, [])

    def get(self, id, token):
        event = self._get_event(id)
        poll_orgs = self.get_poll_resources(token)
        if event.organization_id not in poll_orgs:
            raise ForbiddenException(Err.OK0002, [])
        return event.to_dict()

    def list(self, **kwargs):
        token = kwargs.get('token')
        limit = kwargs.get('limit')
        ack_only = kwargs.get('ack_only', False)
        read_on_get = kwargs.get('read_on_get', False)
        time_start = kwargs.get('time_start')
        time_end = kwargs.get('time_end')
        evt_classes = kwargs.get('evt_classes')
        levels = kwargs.get('levels', [])
        object_types = kwargs.get('object_types', [])
        _check_filter_list(levels, 'levels')
        _check_filter_list(object_types, 'object_types')
        last_polled_time = 0
        events = self.get_events(time_start, time_end, evt_classes, levels,
                                 object_types, ack_only, limit)
        events_result = []
        last_id = kwargs.get('last_id')
        include_read = kwargs.get('include_read', False)
        org_id = kwargs.get('organization_id')
        if org_id is None:
            return {"events": [], "unread": 0, "alert": False}
        self._check_limit(limit)
        if last_id:
            # get last id
            last_polled = Event.objects.get(id=last_id)
            if not last_polled:
                raise NotFoundException(Err.OK0004, [Event.__name__, last_id])
            last_polled_time = last_polled.time
            events = events(Q(time__lt=last_polled_time))
        user_id = self.get_user_id_by_token(token)
        reads = self.get_reads(user_id)
        events = events(Q(organization_id=org_id))
        if not include_read:
            events = events(Q(id__nin=list(reads.keys())))
        if read_on_get:
            to_read = []
            for event in events:
                evt_dict = event.to_dict()
                evt_dict.update({'read': reads.get(event.id, False)})
                events_result.append(evt_dict)
                if str(event.id) not in reads.keys() and (
                        not event.ack or(event.ack and event.acknowledged_by)):
                    to_read.append(str(event.id))
            # marking events as read, we cant crash here
            if to_read:
                try:
                    reads = list(map(lambda x: ReadEvent(
                        user_id=user_id,
                        event=Event.objects.get(id=x)), to_read))
                    ReadEvent.objects.insert(reads)
                except Exception as exc:
                    LOG.error(
                        'Failed to mark events as read for user %s with %s',
                        user_id, str(exc))
        else:
            events_result = list(map(lambda x: x.to_dict(), events))
        result = {
            "events": events_result,
        }
        return result

    def ack(self, id, **kwargs):
        token = kwargs.get('token')
        resolution = kwargs.get('resolution', '')
        event = self._get_event(id=id)
        if not event.ack or event.acknowledged_by:
            raise WrongArgumentsException(Err.OK0018, [id])
        poll_orgs = self.get_ack_resources(token)
        if event.organization_id not in poll_orgs:
            raise ForbiddenException(Err.OK0002, [])
        digest = hashlib.md5(token.encode('utf-8')).hexdigest()
        user_meta = self.get_meta_by_token(token)
        event.acknowledged_by = digest
        event.acknowledged_user = '%s (%s)' % (
            user_meta.get('user_display_name'), user_meta.get('user_name'))
        if resolution:
            event.resolution = resolution
        user_id = self.get_user_id_by_token(token)
        ReadEvent.objects.insert(ReadEvent(event=event, user_id=user_id))
        event.save()
        return {'id': id}

    def ack_all(self, **kwargs):
        token = kwargs.pop('token')
        resolution = kwargs.get('resolution')
        timestamp = kwargs.get('timestamp')
        org_id = kwargs.pop('organization_id', None)
        if timestamp is None:
            return {'id': []}

        if ((timestamp is not None and not isinstance(timestamp, int)) or
                timestamp < 0):
            raise WrongArgumentsException(
                Err.OK0028, [])
        unexpected = list(filter(
            lambda x: x not in['resolution', 'timestamp'], kwargs))
        if unexpected:
            args = ','.join(unexpected)
            raise WrongArgumentsException(Err.OK0030, [args])
        events = Event.objects(
            (Q(organization_id=org_id)) & Q(
                time__lte=timestamp) & Q(
                ack=True) & Q(acknowledged_by=None))
        event_ids = list(map(lambda x: str(x.id), events))
        if events:
            digest = hashlib.md5(token.encode('utf-8')).hexdigest()
            user_meta = self.get_meta_by_token(token)
            events.update(acknowledged_by=digest,
                          acknowledged_user='%s (%s)' % (
                              user_meta.get('user_display_name'),
                              user_meta.get('user_name')),
                          resolution=resolution)
            user_id = self.get_user_id_by_token(token)
            read_event = list(map(lambda x: ReadEvent(
                user_id=user_id, event=Event.objects.get(id=x)), event_ids))
            ReadEvent.objects.insert(read_event)
        return {'id': event_ids}

    def _publish_event(self, **kwargs):
        self.rabbit_client.publish_message(kwargs)

    def submit(self, **kwargs):
        # TODO: possible filter kwargs/filter unexpected
        kwargs['time'] = int(datetime.utcnow().timestamp())
        event = Event(**kwargs)
        try:
            event.save()
        except ValidationError as exc:
            self.raise_from_validation_error(exc)

        self._publish_event(**kwargs)

        return event.to_dict()


class EventAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return EventController
