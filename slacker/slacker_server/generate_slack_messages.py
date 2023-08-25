import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from inspect import getmembers, getmodule, isfunction
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store.sqlalchemy import (
    SQLAlchemyInstallationStore)
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore
from optscale_client.config_client.client import Client as ConfigClient
from slacker.slacker_server.constants import urls
from slacker.slacker_server.slack_client import SlackClient
from slacker.slacker_server.message_templates.alerts import *
from slacker.slacker_server.message_templates.bookings import *
from slacker.slacker_server.message_templates.connect import *
from slacker.slacker_server.message_templates.constraints import *
from slacker.slacker_server.message_templates.constraint_violations import *
from slacker.slacker_server.message_templates.disconnect import *
from slacker.slacker_server.message_templates.envs import *
from slacker.slacker_server.message_templates.env_alerts import *
from slacker.slacker_server.message_templates.errors import *
from slacker.slacker_server.message_templates.org import *
from slacker.slacker_server.message_templates.resources import *
from slacker.slacker_server.message_templates.resource_details import *
from slacker.slacker_server.message_templates.warnings import *
from slacker.slacker_server.models.db_factory import DBType, DBFactory

NOW_TS = int(datetime.utcnow().timestamp())
ACQUIRED_SINCE = datetime.strftime(datetime.utcfromtimestamp(
    NOW_TS - 60), "%m/%d/%Y %H:%M UTC")
RELEASED_AT = datetime.strftime(datetime.utcfromtimestamp(NOW_TS + 3600),
                                "%m/%d/%Y %H:%M UTC")
FUTURE_ACQUIRED_SINCE = datetime.strftime(datetime.utcfromtimestamp(
    NOW_TS + 3660), "%m/%d/%Y %H:%M UTC")
FUTURE_RELEASED_AT = datetime.strftime(datetime.utcfromtimestamp(
    NOW_TS + 7200), "%m/%d/%Y %H:%M UTC")
POOL = {"name": "My pool", "limit": 500, "id": str(uuid.uuid4())}
CLOUD_ACCOUNT = {"name": "My super cloud", "id": str(uuid.uuid4())}
ORGS = [{"name": "My super org", "id": str(uuid.uuid4())}]
PUBLIC_IP = '5.5.5.5'
USER = {"name": "superuser", "email": "superuser@hystax.com",
        "id": str(uuid.uuid4())}
EMPLOYEE = {"id": str(uuid.uuid4()), "auth_user_id": USER['id']}
ALERT_COMMON_PARAMS = {"pool_name": POOL['name'], "pool_id": POOL['id'],
                       "limit": POOL['limit'], "initiator_name": USER['name'],
                       "public_ip": PUBLIC_IP, "initiator_email": USER['email']}
ALERT_1_PARAMS = {**ALERT_COMMON_PARAMS, "threshold": 50,
                  "threshold_type": "percentage", "based": "cost",
                  "include_children": True}
ALERT_2_PARAMS = {**ALERT_COMMON_PARAMS, "threshold": 100,
                  "threshold_type": "percentage", "based": "forecast",
                  "include_children": False}
CONTACTS = {"contacts": [{'slack_channel_id': "FAKE"}]}
ALERT = {**ALERT_1_PARAMS, "id": str(uuid.uuid4()), **CONTACTS}
ALERT_2 = {**ALERT_2_PARAMS, "id": str(uuid.uuid4()), **CONTACTS}
CHANNEL_MAP = {"FAKE": "My secret channel"}
EXPENSES = [{"cloud_resource_id": "i-00000000", "resource_type": "Instance",
             "resource_id": str(uuid.uuid4()), "cost": 118.23,
             "cloud_account_name": CLOUD_ACCOUNT['name'],
             'total_expense_limit': 100},
            {"cloud_resource_id": "i-00000001", "resource_type": "Volume",
             "resource_id": str(uuid.uuid4()), "cost": 0.25,
             "cloud_account_name": CLOUD_ACCOUNT['name'], 'ttl': 2},
            {"cloud_resource_id": "i-00000002", "resource_type": "Snapshot",
             "resource_id": str(uuid.uuid4()), "cost": 84.62,
             "cloud_account_name": CLOUD_ACCOUNT['name'],
             'daily_expense_limit': 60}]
RESOURCE = {"name": "my_resource", "cloud_resource_id": "i-00000000",
            "id": str(uuid.uuid4()), "resource_type": "Instance",
            "region": "eu-north-1", "pool_id": POOL['id'],
            "cloud_account_id": CLOUD_ACCOUNT['id'], "details": {
                "cost": 118.23, "total_cost": 251.87, "service_name": "AWS EC2",
                "cloud_name": CLOUD_ACCOUNT['name'],
                "pool_name": POOL['name'], "owner_name": USER['name'],
                "constraints": {'ttl': {'limit': 0}}, "policies": {}},
            "tags": {"super": "tag"},
            "cloud_account_name": CLOUD_ACCOUNT["name"]}
RESOURCE_1 = {**RESOURCE, "name": "my_booked_resource", "id": str(uuid.uuid4()),
              "shareable": True}
RESOURCE_2 = {**RESOURCE, "name": "my_available_resource",
              "id": str(uuid.uuid4())}
CONSTRAINT_VIOLATIONS = [{"resource_id": RESOURCE['id'],
                          "resource_type": RESOURCE['resource_type'],
                          "cloud_account_name": CLOUD_ACCOUNT['name'],
                          "cloud_resource_id": RESOURCE['cloud_resource_id'],
                          "resource_name": RESOURCE['name'], "type": "ttl"}]
BOOKING_COMMON = {"organization_id": ORGS[0]['id'], "id": str(uuid.uuid4()),
                  "resource_id": RESOURCE['id'],
                  "acquired_by": {"id": EMPLOYEE['id'], "name": USER['name']}}
BOOKING_FUTURE = {**BOOKING_COMMON, "acquired_since": FUTURE_ACQUIRED_SINCE,
                  "released_at": FUTURE_RELEASED_AT,
                  "resource_id": RESOURCE['id'], "allow_delete": True}
BOOKING_NOW = {**BOOKING_COMMON, "acquired_since": ACQUIRED_SINCE,
               "released_at": RELEASED_AT, "resource_id": RESOURCE['id'],
               "allow_delete": True, "allow_release": True}
BOOKING_NO_RELEASE = {**BOOKING_COMMON, "acquired_since": ACQUIRED_SINCE,
                      "released_at": "Not set",
                      "resource_id": RESOURCE_1['id']}
BOOKING_STATUS = "occupied until {0} by {1}".format(RELEASED_AT, USER['name'])
BOOKING_STATUS_AVAILABLE = "available"
BOOKING_STATUS_NO_RELEASE = "occupied by {0}".format(USER['name'])
CURRENCY = 'USD'
ACTIVE_STATES = ['Active', 'Not Active']
ENV_PROPERTIES = [
    {"name": "JIRA tickets", "previous_value": "NGUI-123",
     "new_value": "NGUI-321"},
    {"name": "software", "previous_value": "SunWare-1.1",
     "new_value": "SunWare-2.1"},
    {"name": "owner", "previous_value": "user", "new_value": "superuser"},
    {"name": "job number", "previous_value": "1", "new_value": "2"},
    {"name": "job status", "previous_value": "failed", "new_value": "passed"},
    {"name": "status", "previous_value": "down", "new_value": "up"}]
CURRENT_PROPERTIES = {"status": "up", "job status": "passed",
                      "job number": "2", "owner": "superuser",
                      "software": "SunWare-2.1", "JIRA tickets": "NGUI-123"}


LOG = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', dest='mode',
                        help='where message data should be saved: [json, dm],'
                             '"dm" mode requires environmental variables:'
                             'HX_ETCD_HOST, HX_ETCD_PORT, SLACK_SIGNING_SECRET,'
                             'SLACK_CLIENT_ID, SLACK_CLIENT_SECRET',
                        choices=['json', 'dm'], required=True)
    parser.add_argument('-e', '--employee', dest='employee', type=str,
                        help='employee to send slack messages')
    args = parser.parse_args()

    templates = {"get_welcome_message": [PUBLIC_IP, 'secret'],
                 "get_connection_done_message": [ORGS, USER['email'],
                                                 ORGS[0]['id']],
                 "get_disconnected_message": [USER['email'], PUBLIC_IP],
                 "get_disconnect_confirmation_message": [USER['email'],
                                                         PUBLIC_IP],
                 "get_org_switch_message": [ORGS, ORGS[0]['id']],
                 "get_org_switch_completed_message": [ORGS[0]['name']],
                 "get_resources_message": [
                     ORGS[0]['id'], ORGS[0]['name'], EXPENSES, len(EXPENSES),
                     sum(x['cost'] for x in EXPENSES), PUBLIC_IP, CURRENCY],
                 "get_resource_details_message": [
                     RESOURCE_1, ORGS[0]['id'], PUBLIC_IP, BOOKING_NOW,
                     CURRENCY],
                 "get_alert_added_message": [
                     POOL['name'], POOL['id'], POOL['limit'],
                     ALERT_COMMON_PARAMS['initiator_name'],
                     ALERT_COMMON_PARAMS['initiator_email'],
                     PUBLIC_IP, ORGS[0]['id'], ALERT_1_PARAMS['threshold'],
                     ALERT_1_PARAMS['threshold_type'],
                     ALERT_1_PARAMS['based'],
                     ALERT_1_PARAMS['include_children'], CURRENCY],
                 "get_alert_removed_message": [
                     POOL['name'], POOL['id'], POOL['limit'],
                     ALERT_1_PARAMS['initiator_name'],
                     ALERT_1_PARAMS['initiator_email'],
                     PUBLIC_IP, ORGS[0]['id'], ALERT_1_PARAMS['threshold'],
                     ALERT_1_PARAMS['threshold_type'], ALERT_1_PARAMS['based'],
                     ALERT_1_PARAMS['include_children'], CURRENCY],
                 "get_alert_list": [[ALERT, ALERT_2], {POOL['id']: POOL},
                                    PUBLIC_IP, ORGS[0]['id'],
                                    ORGS[0]['name'], CHANNEL_MAP, CURRENCY],
                 "get_alert_message": [
                     POOL['name'], ORGS[0]['name'], ORGS[0]['id'], PUBLIC_IP,
                     POOL['id'], POOL['limit'], RESOURCE['details']['cost'],
                     ALERT_1_PARAMS['based'], ALERT_1_PARAMS['threshold'],
                     ALERT_1_PARAMS['threshold_type'], CURRENCY],
                 "get_join_channel_message": [],
                 "get_constraint_violation_alert": [
                     ORGS[0]['id'], ORGS[0]['name'], CONSTRAINT_VIOLATIONS,
                     PUBLIC_IP],
                 "get_constraint_updated": [RESOURCE, ORGS[0]['id'], PUBLIC_IP],
                 "get_ca_not_connected_message": [ORGS[0]['name'], PUBLIC_IP],
                 "get_not_have_slack_permissions_message": [],
                 "get_envs_message": [
                     ORGS[0]['id'], ORGS[0]['name'],
                     [RESOURCE_2, RESOURCE_1, RESOURCE],
                     {RESOURCE_2['id']: 'available',
                      RESOURCE_1['id']: BOOKING_STATUS,
                      RESOURCE['id']: BOOKING_STATUS_NO_RELEASE}, PUBLIC_IP],
                 "get_booking_details_message": [
                     PUBLIC_IP, RESOURCE['id'], RESOURCE['name'],
                     ORGS[0]['id'], ORGS[0]['name'],
                     [BOOKING_NOW, BOOKING_FUTURE]],
                 "get_message_changed_active_state": [
                     RESOURCE['id'], RESOURCE['name'], PUBLIC_IP,
                     ORGS[0]['id'], ORGS[0]['name'], ACTIVE_STATES[0],
                     ACTIVE_STATES[1]],
                 "get_property_updated_message": [
                     RESOURCE['id'], RESOURCE['name'], PUBLIC_IP, ORGS[0]['id'],
                     ORGS[0]['name'], ENV_PROPERTIES, CURRENT_PROPERTIES,
                     BOOKING_STATUS_AVAILABLE],
                 "get_message_released": [
                     RESOURCE['id'], RESOURCE['name'], PUBLIC_IP, ORGS[0]['id'],
                     ORGS[0]['name'], BOOKING_FUTURE, BOOKING_NO_RELEASE]
                 }
    excluded_functions = [
        'get_add_expense_alert_modal', 'get_alert_list_block',
        'get_alert_section', 'get_pool_selector', 'get_channel_selector',
        'get_constraint_block', 'get_ttl_constraint_message',
        'get_update_ttl_form', 'get_org_message', 'get_org_switch_blocks',
        'get_resource_blocks', 'get_resource_details_block',
        'get_add_alert_modal_empty_template', 'get_env_resource_block',
        'get_add_constraint_envs_alert_modal', 'get_select_alert_type_modal',
        'get_time_options', 'get_add_bookings_form',
        'get_booking_block', 'get_env_property_updated_block',
        'get_current_env_property_block', 'get_released_or_acquired_message',
        'get_message_acquired', 'get_archived_message_block'
    ]

    check_templates(templates, excluded_functions)
    if args.mode == 'json':
        save_to_json(templates)
    else:
        assert args.employee, "Employee is not defined"
        send_messages_to_slack_channel(templates, args.employee)


def check_templates(templates, excluded_functions):
    funcs = getmembers(sys.modules[__name__], isfunction)
    for func in funcs:
        func_module = getmodule(func[1])
        if ('message_templates' in func_module.__name__ and
                func[0] not in excluded_functions and
                func[0] not in list(templates.keys())):
            LOG.warning('%s is missing in messages templates to send',  func[0])


def get_messages_texts(templates):
    messages = {}
    for func_name, params in templates.items():
        func = getattr(sys.modules[__name__], func_name)
        result = func(*params)
        file_name = func_name[4:]
        messages[file_name] = result
    specific_messages = get_specific_messages_texts()
    return {**messages, **specific_messages}


def get_specific_messages_texts():
    def resources_with_no_resources():
        return get_resources_message(
            org_id=ORGS[0]['id'], org_name=ORGS[0]['name'], shown_data=[],
            total_count=0, total_sum=0, public_ip=PUBLIC_IP)

    def envs_with_no_resources():
        return get_envs_message(
            org_id=ORGS[0]['id'], org_name=ORGS[0]['name'], resources=[],
            resource_status_map={}, public_ip=PUBLIC_IP)

    def alert_with_archived_warning():
        msg = get_alert_message(
                     POOL['name'], ORGS[0]['name'], ORGS[0]['id'], PUBLIC_IP,
                     POOL['id'], POOL['limit'], RESOURCE['details']['cost'],
                     ALERT_1_PARAMS['based'], ALERT_1_PARAMS['threshold'],
                     ALERT_1_PARAMS['threshold_type'], CURRENCY)
        msg['blocks'] = get_archived_message_block(
            PUBLIC_IP, POOL['id'], ORGS[0]['id'], POOL['name'],
            ALERT_1_PARAMS['limit'], ALERT_1_PARAMS['based'],
            ALERT_1_PARAMS['threshold'], ALERT_1_PARAMS['threshold_type'],
            ALERT_1_PARAMS['include_children'], list(CHANNEL_MAP.keys())[0],
            CURRENCY) + msg['blocks']
        return msg

    return {"resources_message_with_no_resources": resources_with_no_resources(),
            "envs_message_with_no_resources": envs_with_no_resources(),
            "alert_with_archived_warning": alert_with_archived_warning()}


def save_to_json(templates):
    messages = get_messages_texts(templates)
    for name, message in messages.items():
        with open(name, 'w') as f:
            f.write(json.dumps({'blocks': message['blocks']}))
        LOG.info('Message was saved to %s file', name)


def prepare_slack_app(employee):
    etcd_host = os.environ.get('HX_ETCD_HOST', '127.0.0.1')
    etcd_port = int(os.environ.get('HX_ETCD_PORT', '2379'))
    config_cl = ConfigClient(host=etcd_host, port=etcd_port)

    db_type = DBType.MySQL
    db = DBFactory(db_type, config_cl).db

    slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET",
                                          'signing_secret')
    slack_client_id = os.environ.get("SLACK_CLIENT_ID", 'client_id')
    slack_client_secret = os.environ.get("SLACK_CLIENT_SECRET", 'client_secret')

    installation_store = SQLAlchemyInstallationStore(
        client_id=slack_client_id,
        engine=db.engine,
        logger=LOG,
    )
    oauth_state_store = SQLAlchemyOAuthStateStore(
        expiration_seconds=120,
        engine=db.engine,
        logger=LOG,
    )

    app = App(
        logger=LOG,
        signing_secret=slack_signing_secret,
        installation_store=installation_store,
        oauth_settings=OAuthSettings(
            client_id=slack_client_id,
            client_secret=slack_client_secret,
            scopes=["chat:write", 'im:history'],
            state_store=oauth_state_store,
            redirect_uri_path=urls.oauth_redirect,
            install_path=urls.install,
        ),
        client=SlackClient(installation_store=installation_store)
    )

    sql_cmd = """select slack_channel_id, slack_team_id from user
              where employee_id='{}' and deleted_at=0""".format(employee)
    with db.engine.connect() as connection:
        result = connection.execute(sql_cmd)
        assert result.rowcount == 1, ('Can\'t get channel for '
                                      'employee %s', employee)
        for row in result:
            channel_id = row[0]
            team_id = row[1]
    return app, channel_id, team_id


def send_messages_to_slack_channel(templates, employee):
    app, channel_id, team_id = prepare_slack_app(employee)
    messages = get_messages_texts(templates)
    for name, message in messages.items():
        app.client.chat_post(
            channel_id=channel_id, team_id=team_id,
            blocks=message['blocks'], text=message['text'])
        LOG.info('Message %s was sent to %s channel', name, channel_id)


if __name__ == '__main__':
    main()
