from collections import OrderedDict
from datetime import datetime
from slacker.slacker_server.constants import CURRENCY_MAP

__all__ = ['get_resource_details_block', 'get_resource_details_message']

EXPENSE_LIMIT_TO_SHOW = 0.9
TTL_LIMIT_TO_SHOW = 72
SEC_IN_HRS = 3600


def get_resource_details_block(resource, org_id, public_ip):
    cloud_resource_id = resource['cloud_resource_id']
    r_name = resource.get('name') or cloud_resource_id
    r_id = resource['id']
    details = resource['details']
    service_name = details['service_name']
    r_type = resource['resource_type']
    cloud_name = details['cloud_name']
    region = resource['region']
    ordered_resource_details = OrderedDict({
        'Type': r_type,
        'Service': service_name,
        'Data Source': cloud_name,
        'Region': region
    })
    result_details = ""
    for r_key, r_value in ordered_resource_details.items():
        if not result_details:
            result_details = f"_{r_key}: *{r_value}*_\n_"
        elif r_value:
            result_details += f"{r_key}: *{r_value}*_\n_"
    fields = [{
        "type": "mrkdwn",
        "text": f"*<https://{public_ip}/resources/{r_id}"
                f"?tab=details&organizationId={org_id}"
                f"|{cloud_resource_id}>*\n{r_name}"
    }]
    if result_details:
        # clear last trailing
        result_details = result_details[:-2]
        fields.append({
            "type": "mrkdwn",
            "text": result_details
        })
    return [
        {
            "type": "section",
            "fields": fields
        }
    ]


def _get_expense_limit_msg(c_sign, total_cost, expense):
    expense_msg = "Not set"
    if expense:
        if expense['limit'] < total_cost:
            expense_msg = ":exclamation:*{0}{1}*".format(
                c_sign, expense['limit'])
        elif total_cost / expense['limit'] >= EXPENSE_LIMIT_TO_SHOW:
            expense_msg = ":warning:{0}{1}".format(
                c_sign, expense['limit'])
        elif total_cost / expense['limit'] < EXPENSE_LIMIT_TO_SHOW:
            expense_msg = "{0}{1}".format(c_sign, expense['limit'])
        elif expense['limit'] == 0:
            expense_msg = ":warning:No limit"
    return expense_msg


def get_resource_details_message(
        resource, org_id, public_ip, booking=None,
        currency='USD', total_expense_limit_enabled=False):
    c_sign = CURRENCY_MAP.get(currency, '')
    r_id = resource['id']
    details = resource['details']
    pool_id = resource.get('pool_id')
    pool_name = details.get('pool_name')
    owner_name = details.get('owner_name')
    total_cost = details.get('total_cost', 0)
    month_cost = details.get('cost', 0)
    tags = resource.get('tags', {})

    constraint_types = ['ttl', 'daily_expense_limit']
    if total_expense_limit_enabled:
        constraint_types.append('total_expense_limit')
    constraints = {}
    for constraint in constraint_types:
        if details['constraints'].get(constraint):
            constraints[constraint] = details['constraints'][constraint]
            constraints[constraint]['constraint_type'] = '_(resource specific)_'
        elif details['policies'].get(constraint, {}).get('active'):
            constraints[constraint] = details['policies'][constraint]
            constraints[constraint]['constraint_type'] = '_(pool policy)_'
        else:
            constraints[constraint] = {}

    ttl = constraints.get('ttl')
    if ttl:
        hrs = (ttl['limit'] - datetime.utcnow().timestamp()) / SEC_IN_HRS
        if ttl['limit'] == 0:
            ttl_msg = ":warning:No limit"
        elif hrs <= -1:
            ttl_msg = ":exclamation:*TTL expired {} hours ago*".format(
                abs(int(hrs)))
        elif -1 < hrs <= 0:
            ttl_msg = ":exclamation:*TTL expired < 1 hour ago*"
        elif 0 < hrs <= 1:
            ttl_msg = ":warning:< 1 hour left"
        elif 1 < hrs < TTL_LIMIT_TO_SHOW + 1:
            ttl_msg = ":warning:{} hours left".format(int(hrs))
        else:
            ttl_msg = "{} hours left".format(int(hrs))
    else:
        ttl_msg = 'Not set'

    daily_expense = constraints.get('daily_expense_limit')
    daily_expense_msg = _get_expense_limit_msg(c_sign, total_cost,
                                               daily_expense)
    daily_constaint_type = constraints['daily_expense_limit'].get(
        'constraint_type', '')

    header_blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Here are the details of the resource you asked"
        }
    }] + get_resource_details_block(resource, org_id, public_ip)

    tags_blocks = []
    if tags:
        text = "*Tags*"
        for k, v in tags.items():
            text += f"\n{k} : *{v}*"
        tags_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                    "verbatim": True
                },
            }
        ]

    resource_blocks = [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"Pool\n*<https://{public_ip}/pools/"
                            f"{pool_id}?organizationId={org_id}"
                            f"|{pool_name}>*"
                },
                {
                    "type": "mrkdwn",
                    "text": f"Owner\n*{owner_name}*"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":moneybag:*Expenses*"
            },
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"Total\t\t{c_sign}{total_cost:.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"This month\t{c_sign}{month_cost:.2f}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Constraints*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"TTL\t\t\t\t\t\t\t{ttl_msg} "
                        f"{constraints['ttl'].get('constraint_type', '')}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Update TTL",
                    "emoji": True
                },
                "action_id": "update_ttl",
                "value": f"{resource['id']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Daily expense limit\t\t\t{daily_expense_msg} "
                        f"{daily_constaint_type}"
            }
        }
    ]

    if total_expense_limit_enabled:
        total_expense = constraints.get('total_expense_limit')
        total_expense_msg = _get_expense_limit_msg(c_sign, total_cost,
                                                   total_expense)
        total_constaint_type = constraints['total_expense_limit'].get(
            'constraint_type', '')
        resource_blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Total expense limit\t\t\t{total_expense_msg} "
                            f"{total_constaint_type}"
                }
            }
        )

    booking_blocks = []
    if resource.get('shareable'):
        if booking:
            employee = booking['acquired_by']['name']
            since = booking['acquired_since']
            until = booking['released_at']
        else:
            since = until = employee = 'Not set'
        booking_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Bookings*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Employee:\t\t\t{employee}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Details",
                        "emoji": True
                    },
                    "action_id": "booking_details",
                    "value": f"{resource['id']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Since:\t\t\t\t\t{since}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Until: \t\t\t\t\t{until}"
                }
            }
        ]

    footer_blocks = [{
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f":pushpin: You can also check this resource "
                            f"details in <https://{public_ip}/resources/{r_id}"
                            f"?tab=details&organizationId={org_id}"
                            f"|OptScale web console>"
                }
            ]
        }
    ]
    return {
        "text": "Here are the details of the resource you asked",
        "blocks": (header_blocks + tags_blocks + resource_blocks +
                   booking_blocks + footer_blocks),
        "unfurl_links": False
    }
