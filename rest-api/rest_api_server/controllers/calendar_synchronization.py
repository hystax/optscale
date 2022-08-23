import logging

from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from sqlalchemy import and_, exists

from rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from rest_api_server.models.models import (
    Organization, CalendarSynchronization, ShareableBooking)

from google_calendar_client.client import GoogleCalendarClient, CalendarException
from googleapiclient.errors import HttpError
from optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException, FailedDependency, ConflictException)

LOG = logging.getLogger(__name__)
# Google API limitation
UPDATED_MIN_DAYS = 28


class CalendarSynchronizationController(BaseController, MongoMixin):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._google_calendar_cl = None
        self._public_ip = None

    @property
    def google_calendar_cl(self):
        if self._google_calendar_cl is None:
            service_key = self._config.google_calendar_service_key()
            self._google_calendar_cl = GoogleCalendarClient(service_key)
        return self._google_calendar_cl

    @property
    def public_ip(self):
        if not self._public_ip:
            self._public_ip = self._config.public_ip()
        return self._public_ip

    def _get_model_type(self):
        return CalendarSynchronization

    def _is_organization_exists(self, organization_id):
        return self.session.query(
            exists().where(and_(
                Organization.id == organization_id,
                Organization.deleted.is_(False)
            ))
        ).scalar()

    def _validate(self, item, is_new=True, **kwargs):
        if not self._is_organization_exists(item.organization_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, item.organization_id])
        query = self.session.query(exists().where(
            and_(*(item.get_uniqueness_filter(is_new)))))
        cloud_acc_exist = query.scalar()
        if cloud_acc_exist:
            raise ConflictException(
                Err.OE0487, [item.calendar_id, item.organization_id])

    def _is_synchronization_supported(self):
        try:
            return bool(self._config.google_calendar_service_enabled())
        except:
            return False

    def get_resources(self, resource_ids):
        if not resource_ids:
            return []
        return self.resources_collection.find(
            {'_id': {'$in': resource_ids}, 'deleted_at': 0})

    def _get_shareable_bookings(self, organization_id, with_none_events=True):
        query = self.session.query(ShareableBooking).filter(
            and_(
                ShareableBooking.organization_id == organization_id,
                ShareableBooking.deleted.is_(False)
            ))
        if not with_none_events:
            query = query.filter(ShareableBooking.event_id.isnot(None))
        return query.all()

    def create(self, calendar_id, organization_id, **kwargs):
        if not self._is_synchronization_supported():
            raise FailedDependency(Err.OE0485, [])
        self._check_calendar_availability(organization_id, calendar_id)
        shareable_bookings = self._get_shareable_bookings(organization_id)
        self.create_calendar_events(shareable_bookings, calendar_id)
        calendar_synchronization = super().create(
            calendar_id=calendar_id, organization_id=organization_id, **kwargs)
        meta = {
            'calendar_id': calendar_synchronization.calendar_id
        }
        self.publish_activities_task(
            calendar_synchronization.organization_id,
            calendar_synchronization.id, 'calendar_synchronization',
            'calendar_connected', meta,
            'calendar_synchronization.calendar_connected', add_token=True)
        return calendar_synchronization

    def delete(self, item_id):
        item = self.get(item_id)
        if not self._is_organization_exists(item.organization_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, item.organization_id])
        self.delete_calendar_events(item)
        self.clear_shareable_bookings(item.organization_id)
        super().delete(item_id)
        meta = {
            'calendar_id': item.calendar_id
        }
        self.publish_activities_task(
            item.organization_id, item.id,
            'calendar_synchronization', 'calendar_disconnected',
            meta, 'calendar_synchronization.calendar_disconnected',
            add_token=True)

    def clear_shareable_bookings(self, org_id):
        self.session.query(ShareableBooking).filter(
            and_(
                ShareableBooking.organization_id == org_id,
                ShareableBooking.deleted.is_(False)
            )).update({'event_id': None}, synchronize_session=False)

    def delete_calendar_event_by_id(self, calendar_sync, event_id):
        if event_id:
            try:
                self.google_calendar_cl.delete_event(
                    calendar_sync.calendar_id, event_id)
            except CalendarException as ex:
                self.publish_gcalendar_warning(calendar_sync, str(ex))

    def format_http_error(self, ex):
        if isinstance(ex, HttpError):
            if ex.resp.status == 403:
                return 'Not enough permissions to manage calendar'
            elif ex.resp.status == 404:
                return 'Calendar not found'
        return str(ex)

    def delete_calendar_events(self, calendar_sync):
        bookings = self._get_shareable_bookings(
            calendar_sync.organization_id, False)
        event_ids = [x.event_id for x in bookings]

        for event_id in event_ids:
            try:
                self.google_calendar_cl.delete_event(
                    calendar_sync.calendar_id, event_id)
            except CalendarException as ex:
                self.publish_gcalendar_warning(calendar_sync, str(ex))
                break

    def update_calendar_event(self, event_id, calendar_id, updates):
        try:
            self.google_calendar_cl.update_event(
                calendar_id, event_id, **updates)
        except CalendarException as ex:
            raise FailedDependency(Err.OE0491, [str(ex)])

    def get_by_organization_id(self, organization_id):
        if not self._is_organization_exists(organization_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        res = self.list(organization_id=organization_id)
        if len(res) > 1:
            raise WrongArgumentsException(Err.OE0177, [])
        if len(res) == 1:
            return res[0]

    def get_service_account(self):
        service_key = self._config.google_calendar_service_key()
        return service_key.get('client_email') or None

    def list_calendar_events(self, calendar_id, time_min=None, time_max=None,
                             updated_min=None, reraise=False):
        if updated_min:
            updated_min_limit = datetime.utcnow() - timedelta(days=UPDATED_MIN_DAYS)
            updated_min = max(updated_min, updated_min_limit)
        try:
            events = self.google_calendar_cl.list_events(
                calendar_id, time_min, time_max, updated_min)
            return events
        except CalendarException as ex:
            if not reraise:
                raise FailedDependency(Err.OE0490, [str(ex)])
            raise

    def get_event_template(
            self, calendar_id, shareable_booking, resource, event=None):
        owner_name = shareable_booking.acquired_by.name
        r_link = f"https://{self.public_ip}/resources/{shareable_booking.resource_id}"
        if not shareable_booking.released_at:
            end_boost = timedelta(days=365)
            end_booking = datetime.fromtimestamp(
                shareable_booking.acquired_since).replace(
                hour=23, minute=59, second=0, microsecond=0) + end_boost
            if event:
                today = datetime.utcnow().replace(
                    hour=23, minute=59, second=0, microsecond=0)
                end_border = today + timedelta(days=180)
                if event['end'] < end_border:
                    end_booking = today + end_boost
                else:
                    end_booking = event['end']
        else:
            end_booking = datetime.fromtimestamp(
                shareable_booking.released_at).replace(second=0)
        return {
            'calendar_id': calendar_id,
            'start': datetime.fromtimestamp(
                shareable_booking.acquired_since).replace(second=0),
            'end': end_booking,
            'summary': f"{resource.get('name')} is acquired by {owner_name}",
            'description': r_link,
            'status': 'confirmed'
        }

    def _check_calendar_availability(self, organization_id, calendar_id):
        now = datetime.utcnow()
        test_template = {
            'calendar_id': calendar_id,
            'start': now,
            'end': now + timedelta(hours=1),
            'summary': "Hystax OptScale test"
        }
        try:
            event = self.google_calendar_cl.create_event(**test_template)
            self.google_calendar_cl.delete_event(calendar_id, event['id'])
        except CalendarException as ex:
            raise FailedDependency(Err.OE0493, [str(ex)])

    def create_calendar_events(self, shareable_bookings, calendar_id):
        resources = self.get_resources(
            [sh_book.resource_id for sh_book in shareable_bookings])
        resources_map = {r['_id']: r for r in resources}

        res = []
        mappings = []
        for shareable_booking in shareable_bookings:
            resource = resources_map.get(shareable_booking.resource_id)
            if not resource:
                continue
            event = self.get_event_template(
                calendar_id, shareable_booking, resource)
            event.pop('status', None)
            try:
                google_event = self.google_calendar_cl.create_event(**event)
                res.append(google_event)
            except CalendarException as ex:
                raise FailedDependency(Err.OE0489, [str(ex)])
            mappings.append({'id': shareable_booking.id,
                             'event_id': google_event['id']})
        self.session.bulk_update_mappings(ShareableBooking, mappings)
        try:
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        return res

    def publish_gcalendar_warning(self, calendar_sync, reason=None):
        meta = {
            'calendar_id': calendar_sync.calendar_id,
            'reason': reason,
            'level': 'WARNING'
        }
        self.publish_activities_task(
            calendar_sync.organization_id, calendar_sync.id,
            'calendar_synchronization', 'calendar_warning',
            meta, 'calendar_synchronization.calendar_warning', add_token=True)


class CalendarSynchronizationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CalendarSynchronizationController
