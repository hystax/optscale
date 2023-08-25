from datetime import datetime
from slacker.slacker_server.constants import CURRENCY_MAP

__all__ = ['get_alert_message', 'get_alert_added_message',
           'get_alert_removed_message', 'get_join_channel_message',
           'get_alert_section', 'get_alert_list_block', 'get_alert_list',
           'get_pool_selector', 'get_channel_selector',
           'get_add_expense_alert_modal', 'get_add_alert_modal_empty_template',
           'get_add_constraint_envs_alert_modal', 'get_select_alert_type_modal',
           ]


def get_alert_message(pool_name, organization_name, organization_id,
                      public_ip, pool_id, limit, cost, based, threshold,
                      threshold_type, currency='USD'):
    c_sign = CURRENCY_MAP.get(currency, '')
    threshold_type_str = 'Expenses' if based == 'cost' else 'Forecast'
    if threshold_type == 'absolute':
        exceed_str = f'*{c_sign}{threshold}* threshold'
    else:
        exceed_str = f'*{threshold}%*'
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59)
    start_ts = int(month_start.timestamp())
    end_ts = int(today_end.timestamp())
    return {
        "text": f"Alarm! Expenses in pool {pool_name} of "
                f"{organization_name} organization require attention.",
        "blocks": [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":bell: *Alarm!*\nExpenses in pool "
                        f"*{pool_name}* of *{organization_name}* organization"
                        f" require attention."
            }
        }, {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"Pool: *<https://{public_ip}/pools/"
                            f"{pool_id}?organizationId={organization_id}"
                            f"|{pool_name}>*\n :dollar: {c_sign}{limit}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*{threshold_type_str}* exceed {exceed_str} "
                            f"of pool limit\n:moneybag:{c_sign}{cost:.2f}"
                }
            ]
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Please check the resources in *{pool_name}* pool"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "See resources",
                    "emoji": True
                },
                "url": f"https://{public_ip}/resources?poolIdIncl={pool_id}"
                       f"&endDate={end_ts}&startDate={start_ts}"
                       f"&organizationId={organization_id}",
                "action_id": "link_button_click",
            }
        }],
        "unfurl_links": False
    }


def get_alert_added_message(pool_name, pool_id, limit, initiator_name,
                            initiator_email, public_ip, organization_id,
                            threshold, threshold_type, based, include_children,
                            currency='USD'):
    return {
        "text": "New alert created for this channel",
        "blocks": [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Hello :wave:"
            }
        }, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Thanks to {initiator_name} ({initiator_email}), we "
                        f"have a new alert created for this channel:"
            }
        }, get_alert_section(
            public_ip, pool_id, organization_id, pool_name, limit, based,
            threshold, threshold_type, include_children, currency
        ), {
            "type": "divider"
        }, {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":pushpin: You can check alerts list saying "
                            "`alerts` in DM with OptScale App"
                }
            ]
        }],
        "unfurl_links": False
    }


def get_alert_removed_message(pool_name, pool_id, limit, initiator_name,
                              initiator_email, public_ip, organization_id,
                              threshold, threshold_type, based,
                              include_children, currency='USD'):
    return {
        "text": f"{initiator_name} ({initiator_email}) has just deleted an "
                f"alert pointing to this channel",
        "blocks": [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Hello :wave:"
            }
        }, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{initiator_name} ({initiator_email}) has just deleted"
                        f" the following alert pointing to this channel:"
            }
        }, get_alert_section(
            public_ip, pool_id, organization_id, pool_name, limit, based,
            threshold, threshold_type, include_children, currency
        ), {
            "type": "divider"
        }, {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":pushpin: You can check alerts list saying "
                            "`alerts` in DM with OptScale App"
                }
            ]
        }],
        "unfurl_links": False
    }


def get_join_channel_message():
    return {
        "text": "Hi everyone",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hi everyone :wave:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "I'm OptScale bot.\nI can notify you here about "
                            "your environments usage and let you know if cloud "
                            "usage expenses will break the comfortable amount."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please DM `alerts` to me to see and adjust "
                            "notifications."
                }
            }
        ]
    }


def get_alert_section(public_ip, pool_id, organization_id, pool_name,
                      limit, based, threshold, threshold_type,
                      include_children, currency='USD'):
    c_sign = CURRENCY_MAP.get(currency, '')
    threshold_type_str = 'Expenses' if based == 'cost' else 'Forecast'
    if threshold_type == 'absolute':
        exceed_str = f'*{c_sign}{threshold}*'
    else:
        exceed_str = f'*{threshold}%*'
    with_subs = ' (with subs)' if include_children else ''
    if based == 'constraint':
        condition_text = "When resource *constraint is violated*"
    elif based == 'env_change':
        condition_text = "When *Environment is updated*"
    else:
        condition_text = "When *{0}* exceed {1} of {2}".format(
            threshold_type_str, exceed_str, based)
    return {
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"Pool: *<https://{public_ip}/pools/"
                        f"{pool_id}?organizationId={organization_id}"
                        f"|{pool_name}>*{with_subs}\n :dollar: {c_sign}{limit}"
            },
            {
                "type": "mrkdwn",
                "text": condition_text
            }
        ]
    }


def get_alert_list_block(alert, pool, channel_names, public_ip,
                         organization_id, currency='USD'):
    main_section = get_alert_section(
        public_ip, alert['pool_id'], organization_id, pool['name'],
        pool['limit'], alert['based'], alert['threshold'],
        alert['threshold_type'], alert['include_children'], currency
    )
    main_section['accessory'] = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "emoji": True,
            "text": "Delete"
        },
        "style": "danger",
        "value": alert['id'],
        "action_id": "alert_delete",
    }
    divider = {"type": "divider"}
    if len(channel_names) == 1:
        channels_str = f"Target channel: *{channel_names[0]}*"
    elif len(channel_names) > 1:
        names_str = ', '.join([f'*{ch}*' for ch in channel_names])
        channels_str = f"Target channels: {names_str}"
    else:
        return [main_section, divider]

    return [
        main_section,
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": channels_str
                }
            ]
        },
        divider
    ]


def get_alert_list(alerts, pool_map, public_ip, organization_id,
                   organization_name, channel_map, currency='USD'):
    pool_blocks = []
    for alert in alerts:
        pool_info = pool_map.get(alert['pool_id'])
        channel_contacts = [contact['slack_channel_id']
                            for contact in alert['contacts']
                            if contact['slack_channel_id'] is not None]
        channel_names = [channel_map.get(ch_id) for ch_id in channel_contacts]
        pool_blocks.extend(get_alert_list_block(
            alert, pool_info, channel_names, public_ip, organization_id,
            currency))
    header_blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Here is the list of alerts set "
                    f"in *{organization_name}*"
        }
    }]
    footer_blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":question:Want to set up new alert?"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Add alert",
                "emoji": True
            },
            "action_id": "alert_create"
        }
    }]
    return {
        "text": f"Here is the list of alerts set in {organization_name}",
        "blocks": header_blocks + pool_blocks + footer_blocks,
        "unfurl_links": False
    }


def get_pool_selector(pools_map, currency_sign=''):
    blocks = []
    max_text_length = 75
    for pool_id, pool_info in pools_map.items():
        pool_info_text = "{0} ({1}{2})".format(pool_info['name'], currency_sign,
                                               pool_info['limit'])
        if len(pool_info_text) > max_text_length:
            pool_name_len = max_text_length - (
                    len(pool_info_text) - len(pool_info['name']))
            pool_info_text = "{0}... ({1}{2})".format(
                pool_info['name'][:pool_name_len - 3], currency_sign,
                pool_info['limit'])
        blocks.append({
            "text": {
                "type": "plain_text",
                "text": pool_info_text,
                "emoji": True
            },
            "value": pool_id,
        })
    return blocks


def get_channel_selector(channels_map):
    blocks = []
    for channel_id, channel_name in channels_map.items():
        blocks.append({
            "text": {
                "type": "plain_text",
                "text": channel_name,
                "emoji": True
            },
            "value": channel_id,
        })
    return blocks


def get_add_alert_modal_empty_template(text):
    return {
        "callback_id": "add_alert_view",
        "title": {
            "type": "plain_text",
            "text": "Add alert"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": text
                }
            }
        ],
        "type": "modal"
    }


def get_add_expense_alert_modal(pools_map, channels_map, organization_name,
                                currency='USD', alert_type='expense'):
    c_sign = CURRENCY_MAP.get(currency, '')
    return {
        "callback_id": "add_alert_view",
        "private_metadata": alert_type,
        "title": {
            "type": "plain_text",
            "text": "Add alert"
        },
        "submit": {
            "type": "plain_text",
            "text": "Add"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please specify desired alert parameters to create "
                            f"it in *{organization_name}*"
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a pool",
                        "emoji": True
                    },
                    "options": get_pool_selector(pools_map, c_sign),
                    "action_id": "pool_id"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Pick a pool to track"
                },
                "block_id": "pool_id"
            },
            {
                "type": "input",
                "element": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "mrkdwn",
                                "text": "Track sub-pools as well"
                            },
                            "value": "include_children",
                        }
                    ],
                    "action_id": "include_children"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Do you want to set up the same alert for each of "
                            "descendant pool?"
                },
                "block_id": "include_children",
                "optional": True
            },
            {
                "type": "input",
                "element": {
                    "type": "radio_buttons",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Expenses this month",
                                "emoji": True
                            },
                            "value": "cost"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Forecast for this month",
                                "emoji": True
                            },
                            "value": "forecast"
                        }
                    ],
                    "action_id": "based"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Value to track"
                },
                "block_id": "based"
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "50%",
                                "emoji": True
                            },
                            "value": "50"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "70%",
                                "emoji": True
                            },
                            "value": "70"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "90%",
                                "emoji": True
                            },
                            "value": "90"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "95%",
                                "emoji": True
                            },
                            "value": "95"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "100%",
                                "emoji": True
                            },
                            "value": "100"
                        }
                    ],
                    "action_id": "threshold"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Threshold"
                },
                "block_id": "threshold"
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a channel",
                        "emoji": True
                    },
                    "options": get_channel_selector(channels_map),
                    "action_id": "channel_id",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Pick a target channel for this alert"
                },
                "block_id": "channel_id"
            }
        ],
        "type": "modal"
    }


def get_add_constraint_envs_alert_modal(
        pools_map, channels_map, organization_name, currency='USD', alert_type='constraint'):
    c_sign = CURRENCY_MAP.get(currency, '')
    return {
        "callback_id": "add_alert_view",
        "private_metadata": alert_type,
        "title": {
            "type": "plain_text",
            "text": "Add alert"
        },
        "submit": {
            "type": "plain_text",
            "text": "Add"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please specify desired alert parameters to create "
                            f"it in *{organization_name}*"
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a pool",
                        "emoji": True
                    },
                    "options": get_pool_selector(pools_map, c_sign),
                    "action_id": "pool_id"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Pick a pool to track"
                },
                "block_id": "pool_id"
            },
            {
                "type": "input",
                "element": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "mrkdwn",
                                "text": "Track sub-pools as well"
                            },
                            "value": "include_children",
                        }
                    ],
                    "action_id": "include_children"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Do you want to set up the same alert for each of "
                            "descendant pool?"
                },
                "block_id": "include_children",
                "optional": True
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a channel",
                        "emoji": True
                    },
                    "options": get_channel_selector(channels_map),
                    "action_id": "channel_id",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Pick a target channel for this alert"
                },
                "block_id": "channel_id"
            }
        ],
        "type": "modal"
    }


def get_select_alert_type_modal(organization_name, private_metadata=''):
    return {
        "private_metadata": private_metadata,
        "callback_id": "add_alert_view",
        "title": {
            "type": "plain_text",
            "text": "Select an alert type"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please choose an alert type to create it "
                            f"in *{organization_name}*"
                }
            },
            {
                "type": "actions",
                "block_id": "alert_types",
                "elements": [
                    {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Pick an alert type"
                        },
                        "action_id": "alert_view_next",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "constraint alert"
                                },
                                "value": "constraint"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "environment changes alert"
                                },
                                "value": "env_change"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "expenses/forecast alert"
                                },
                                "value": "expense"
                            },
                        ]
                    }
                ]
            }
        ],
        "type": "modal"
    }
