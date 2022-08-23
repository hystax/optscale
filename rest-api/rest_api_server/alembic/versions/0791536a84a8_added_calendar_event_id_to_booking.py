"""Added calendar event id to booking

Revision ID: 0791536a84a8
Revises: aaa0e98cbc49
Create Date: 2021-10-13 09:26:46.520343

"""
import logging
import os

from alembic import op
from sqlalchemy import Column, String, Integer, select, update, and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from config_client.client import Client as EtcdClient
from google_calendar_client.client import (
    GoogleCalendarClient, CalendarException)

# revision identifiers, used by Alembic.

revision = '0791536a84a8'
down_revision = 'aaa0e98cbc49'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
LOG = logging.getLogger(__name__)


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_calendar_client():
    config_client = _get_etcd_config_client()
    service_key = config_client.google_calendar_service_key()
    return GoogleCalendarClient(service_key)


def upgrade():
    op.add_column('shareable_booking', Column(
        'event_id', String(40), nullable=True))
    op.create_unique_constraint('uc_calendar_id_event_id',
                                'shareable_booking',
                                ['organization_id', 'event_id'])
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        calendar_table = table('calendar_synchronization',
                               column('organization_id', String(36)),
                               column('calendar_id', String(256)),
                               column('deleted_at', Integer()))
        active_calendar_stmt = select(
            [calendar_table.c.organization_id, calendar_table.c.calendar_id]
        ).where(calendar_table.c.deleted_at == 0)
        active_calendars = [
            (x['calendar_id'], x['organization_id']) for x in session.execute(
                active_calendar_stmt)]
        gc_client = _get_calendar_client()
        booking_table = table('shareable_booking',
                              column('id', String(36)),
                              column('organization_id', String(36)),
                              column('event_id', String(40)),
                              column('deleted_at', Integer()))
        for calendar_id, org_id in active_calendars:
            org_cond = f"organization_id={org_id}"
            try:
                event_list = gc_client.list_events(
                    calendar_id, limit=2500, private_property=org_cond)
            except CalendarException as exc:
                LOG.warning("Failed to get the list of events, calendar_id %s, "
                            "org_id %s: %s", calendar_id, org_id, str(exc))
                continue
            for event in event_list:
                booking_id = event.get(
                    'private_properties', {}).get('shareable_booking_id')
                event_id = event.get('id')
                if booking_id and event_id:
                    if len(event_id) > 40:
                        LOG.warning(
                            "Event_id is too big, event_id %s, booking_id %s",
                            event_id, booking_id)
                        continue
                    stmt = update(booking_table).values(
                        event_id=event_id).where(
                        and_(booking_table.c.id == booking_id,
                             booking_table.c.organization_id == org_id,
                             booking_table.c.deleted_at == 0))
                    session.execute(stmt)
            session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_constraint('shareable_booking_ibfk_2',
                       'shareable_booking', type_='foreignkey')
    op.drop_constraint('uc_calendar_id_event_id',
                       'shareable_booking', type_='unique')
    op.drop_column('shareable_booking', 'event_id')
    op.create_foreign_key('shareable_booking_ibfk_2', 'shareable_booking',
                          'organization', ['organization_id'], ['id'])
