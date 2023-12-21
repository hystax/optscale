from datetime import datetime
from functools import wraps

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

CALENDAR_SCOPE = 'https://www.googleapis.com/auth/calendar'
UTC_TZ_TAIL = '+00:00'


class CalendarException(Exception):
    pass


def wrap_http_error(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as ex:
            if ex.resp.status == 403:
                msg = 'Not enough permissions to manage calendar'
            elif ex.resp.status == 404:
                msg = 'Calendar not found'
            else:
                msg = str(ex)
            raise CalendarException(msg)
    return func_wrapper


class GoogleCalendarClient(object):
    def __init__(self, account_info):
        self.account_info = account_info
        self._service = None

    @property
    def service(self):
        if self._service is None:
            credentials = Credentials.from_service_account_info(
                self.account_info, scopes=[CALENDAR_SCOPE])
            self._service = discovery.build(
                'calendar', 'v3', credentials=credentials,
                cache_discovery=False)
        return self._service

    @property
    def events(self):
        # pylint: disable=no-member
        return self.service.events()

    @wrap_http_error
    def delete_event(self, calendar_id, event_id):
        return self.events.delete(
            calendarId=calendar_id, eventId=event_id, sendUpdates='none'
        ).execute()

    @staticmethod
    def format_datetime_tz(dt):
        return '%s%s' % (dt.isoformat(), UTC_TZ_TAIL)

    @wrap_http_error
    def update_event(self, calendar_id, event_id, start=None, end=None,
                     private_properties=None, **changes):
        for prop, val in {'start': start, 'end': end}.items():
            if val:
                if not changes.get(prop):
                    changes[prop] = {
                        'dateTime': self.format_datetime_tz(val)}
        if private_properties is not None and isinstance(
                private_properties, dict):
            changes['extendedProperties'] = {'private': private_properties}
        return self.events.patch(
            calendarId=calendar_id, eventId=event_id, body=changes
        ).execute()

    @wrap_http_error
    def create_event(self, calendar_id, start, end, summary=None,
                     description=None, private_properties=None):
        event = {
            'start': {
                'dateTime': self.format_datetime_tz(start),
            },
            'end': {
                'dateTime': self.format_datetime_tz(end),
            },
            'extendedProperties': {
            },
            'guestsCanModify': False,
            'guestsCanInviteOthers': False,
            'transparency': 'transparent',
        }
        if summary is not None:
            event['summary'] = summary
        if description is not None:
            event['description'] = description
        if private_properties is not None and isinstance(
                private_properties, dict):
            event['extendedProperties']['private'] = private_properties
        return self.events.insert(
            calendarId=calendar_id, body=event).execute()

    @staticmethod
    def _format_event(event):
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        for prop in ['start', 'end']:
            val = event.pop(prop, {}).get('dateTime')
            if val:
                event[prop] = datetime.strptime(val, date_format)
        extended_properties = event.pop('extendedProperties', None)
        if extended_properties:
            for src_prop, dst_prop in [
                ('private', 'private_properties'),
                ('shared', 'shared_properties')
            ]:
                val = extended_properties.pop(src_prop, None)
                if val:
                    event[dst_prop] = val
        return event

    @wrap_http_error
    def list_events(self, calendar_id, time_min=None, time_max=None,
                    updated_min=None, private_property=None, limit=100,
                    sort_key=None):
        def format_datetime(dt):
            return '%sZ' % dt.isoformat()

        params = {
            'calendarId': calendar_id,
            'singleEvents': True,
            'timeZone': UTC_TZ_TAIL,
            'showDeleted': True
        }
        if sort_key is not None:
            params['orderBy'] = sort_key
        if limit:
            params['maxResults'] = limit
        if private_property:
            params['privateExtendedProperty'] = private_property
        if time_min is not None:
            params['timeMin'] = format_datetime(time_min)
        if time_max is not None:
            params['timeMax'] = format_datetime(time_max)
        if updated_min is not None:
            params['updatedMin'] = format_datetime(updated_min)

        raw_result = self.events.list(**params).execute()
        for e in raw_result.pop('items', []):
            yield self._format_event(e)
        while raw_result.get('nextPageToken'):
            params['pageToken'] = raw_result.get('nextPageToken')
            raw_result = self.events.list(**params).execute()
            for e in raw_result.pop('items', []):
                yield self._format_event(e)
