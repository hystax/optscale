from datetime import datetime
from slacker.slacker_server.message_templates.resource_details import get_resource_details_block

__all__ = ['get_ttl_constraint_message', 'get_constraint_block',
           'get_update_ttl_form', 'get_constraint_updated']

SEC_IN_HRS = 3600
TTL_LIMIT_TO_SHOW = 72


def get_ttl_constraint_message(ttl_constr):
    ttl_msg = None
    if ttl_constr:
        hrs = (ttl_constr['limit'] - datetime.utcnow().timestamp()) / SEC_IN_HRS
        if ttl_constr['limit'] == 0:
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
    return ttl_msg


def get_constraint_block(resource):
    ttl_constr = resource['details']['constraints'].get('ttl')
    ttl_constr_msg = get_ttl_constraint_message(ttl_constr)
    if not ttl_constr_msg:
        ttl_constr_msg = 'Not set'
    return [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "Current limit"
                },
                {
                    "type": "mrkdwn",
                    "text": f"{ttl_constr_msg} _(resource specific)_"
                }
            ]
        }
    ]


def get_update_ttl_form(resource, org_id, public_ip):
    resource_block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Resource*"
                    },
        }
    ] + get_resource_details_block(resource, org_id, public_ip)
    created = (datetime.utcnow().timestamp() - resource['created_at']) / SEC_IN_HRS
    if created < 1:
        created_msg = '< 1 hour ago'
    elif created == 1:
        created_msg = '1 hour ago'
    else:
        created_msg = '{} hours ago'.format(int(created))

    created_block = [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "Created"
                },
                {
                    "type": "mrkdwn",
                    "text": f"{created_msg}"
                }
            ]
        }
    ]

    ttl_constr = resource['details']['constraints'].get('ttl')
    ttl_policy = resource['details']['policies'].get('ttl')
    ttl_constr_msg = "Not set"
    if ttl_constr:
        if get_ttl_constraint_message(ttl_constr):
            ttl_constr_msg = "{} _(resource specific)_".format(
                get_ttl_constraint_message(ttl_constr))
    elif ttl_policy and ttl_policy['active']:
        ttl_constr_msg = get_ttl_constraint_message(ttl_policy)
        if get_ttl_constraint_message(ttl_policy):
            ttl_constr_msg = "{} _(pool policy)_".format(
                get_ttl_constraint_message(ttl_policy))

    constraint_block = [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "Current limit"
                },
                {
                    "type": "mrkdwn",
                    "text": f"{ttl_constr_msg}"
                }
            ]
        }

    ]

    actions_block = [
        {
            "type": "input",
            "block_id": "ttl_actions",
            "label": {
                "type": "plain_text",
                "text": "Select action"
            },
            "element": {
                "type": "radio_buttons",
                "initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": "Set to now+3h",
                        "emoji": True
                    },
                    "value": "3"
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Set to now+3h",
                            "emoji": True
                        },
                        "value": "3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Set to now+1d",
                            "emoji": True
                        },
                        "value": "24"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Set to now+3d",
                            "emoji": True
                        },
                        "value": "72"
                    },
                ],
                "action_id": "based"
            }
        }
    ]

    reset_to_policy = {
        "text": {
            "type": "plain_text",
            "text": "Reset to pool policy",
            "emoji": True
        },
        "value": "-1"}

    policy_block = []
    if ttl_constr and ttl_policy and ttl_policy['active']:
        ttl_policy_msg = get_ttl_constraint_message(ttl_policy)
        policy_block = [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "Pool policy"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{ttl_policy_msg}"
                    }
                ]
            }
        ]
        actions_block[0]["element"]["options"].insert(0, reset_to_policy)
        actions_block[0]["element"]["initial_option"] = reset_to_policy

    footer_block = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":pushpin: You can also manage this constraint"
                            f"on the <https://{public_ip}/resources/{resource['id']}"
                            f"?tab=constraints&organizationId={org_id}|resource page>"
                }
            ]
        }
    ]

    return {
        "type": "modal",
        "callback_id": "update_ttl_view",
        "private_metadata": f"{resource['id']}",
        "title": {
            "type": "plain_text",
            "text": "Update TTL",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": (resource_block + created_block + constraint_block +
                   policy_block + actions_block + footer_block)
    }


def get_constraint_updated(resource, org_id, public_ip):
    header_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Resource TTL constraint has been updated."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Resource*"
            }
        }
    ]

    resource_block = get_resource_details_block(resource, org_id, public_ip)
    constraint_block = get_constraint_block(resource)

    policy_block = []
    if resource['details']['policies'].get('ttl', {}).get('active'):
        ttl_policy_msg = get_ttl_constraint_message(
            resource['details']['policies']['ttl'])
        policy_block = [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "Pool policy"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{ttl_policy_msg}"
                    }
                ]
            }
        ]
    return {
        "text": "Here are the details of the resource you asked",
        "blocks": header_blocks + resource_block + constraint_block + policy_block,
        "unfurl_links": False
    }
