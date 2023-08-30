import logging
from datetime import datetime
from sqlalchemy import false, and_

from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.calendar_synchronization import (
    CalendarSynchronizationController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import (
    Organization, ShareableBooking, CalendarSynchronization)

from rest_api.google_calendar_client.client import CalendarException
from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  FailedDependency)

LOG = logging.getLogger(__name__)
# when deleting events from the trash,
# Google sets this date as the beginning of the event
DELETED_EVENT_START = datetime(2000, 1, 1, 0, 0)


class CalendarObserverController(BaseController):
    def _get_model_type(self):
        return CalendarSynchronization

    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._calendar_sync_ctl = None
        self._check_list = [
            lambda evt, prop, val: evt.get(prop) is not None,
            lambda evt, prop, val: isinstance(evt[prop], type(val)),
            lambda evt, prop, val: evt[prop] == val,
        ]

    @property
    def calendar_sync_ctl(self):
        if not self._calendar_sync_ctl:
            self._calendar_sync_ctl = CalendarSynchronizationController(
                self.session, self._config)
        return self._calendar_sync_ctl

    def _get_organization(self, organization_id):
        return self.session.query(Organization).filter(
            and_(
                Organization.deleted.is_(False),
                Organization.id == organization_id,
                Organization.is_demo.is_(false())
            )).one_or_none()

    def _get_calendar_synchronization(self, organization_id):
        return self.calendar_sync_ctl.get_by_organization_id(
            organization_id)

    def _get_calendar_events(self, calendar_sync):
        return self.calendar_sync_ctl.list_calendar_events(
            calendar_sync.calendar_id,
            updated_min=datetime.fromtimestamp(calendar_sync.last_completed)
        )

    def _get_shareable_bookings(self, organization_id, event_ids):
        return self.session.query(ShareableBooking).filter(
            and_(
                ShareableBooking.deleted.is_(False),
                ShareableBooking.organization_id == organization_id,
                ShareableBooking.event_id.in_(event_ids)
            )).all()

    def _get_booked_resources_map(self, bookings):
        resource_ids = {b.resource_id for b in bookings}
        resources = self.calendar_sync_ctl.get_resources(list(resource_ids))
        return {r['_id']: r for r in resources}

    def observe(self, organization_id):
        organization = self._get_organization(organization_id)
        if not organization:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        calendar_sync = self._get_calendar_synchronization(organization_id)
        if not calendar_sync:
            raise NotFoundException(Err.OE0486, [organization_id])
        try:
            self._observe(calendar_sync)
        except Exception as ex:
            msg = self.calendar_sync_ctl.format_http_error(ex)
            meta = {
                'calendar_id': calendar_sync.calendar_id,
                'reason': msg,
                'is_observer': True,
                'level': 'WARNING'
            }
            self.publish_activities_task(
                calendar_sync.organization_id, calendar_sync.id,
                'calendar_synchronization', 'calendar_warning',
                meta, 'calendar_synchronization.calendar_warning',
                add_token=True)

    def is_deleted_event(self, event):
        return event.get('status') == 'cancelled' and event.get(
            'start') == DELETED_EVENT_START

    def _observe(self, calendar_sync):
        events_map = {
            x['id']: x for x in self._get_calendar_events(calendar_sync)}
        bookings = self._get_shareable_bookings(
            calendar_sync.organization_id, list(events_map.keys()))
        resources_map = self._get_booked_resources_map(bookings)
        updates_map = {}
        creates_list = []
        for booking in bookings:
            event = events_map.get(booking.event_id)
            if not event:
                continue
            resource = resources_map.get(booking.resource_id)
            if not resource:
                continue
            if self.is_deleted_event(event):
                creates_list.append(booking)
            else:
                changes = self.calendar_sync_ctl.get_event_template(
                    calendar_sync.calendar_id, booking, resource, event)
                changes.pop('calendar_id', None)
                for prop, val in changes.copy().items():
                    is_changed = False
                    for check in self._check_list:
                        if not check(event, prop, val):
                            is_changed = True
                            break
                    if not is_changed:
                        changes.pop(prop)
                if changes:
                    updates_map[event['id']] = changes
        for event_id, changes in updates_map.items():
            try:
                self.calendar_sync_ctl.google_calendar_cl.update_event(
                    calendar_sync.calendar_id, event_id, **changes)
            except CalendarException as ex:
                raise FailedDependency(Err.OE0491, [str(ex)])
        try:
            self.calendar_sync_ctl.create_calendar_events(
                creates_list, calendar_sync.calendar_id)
        except CalendarException as ex:
            raise FailedDependency(Err.OE0489, [str(ex)])
        calendar_sync.last_completed = int(datetime.utcnow().timestamp())
        self.session.commit()


class CalendarObserverAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CalendarObserverController
