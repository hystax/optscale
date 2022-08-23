__all__ = ['get_message_changed_active_state', 'get_message_acquired',
           'get_message_released', 'get_env_property_updated_block',
           'get_current_env_property_block', 'get_property_updated_message',
           'get_released_or_acquired_message']


def get_message_changed_active_state(resource_id, resource_name, public_ip,
                                     org_id, org_name, previous_state,
                                     new_state):
    return {
        "text": "Active state of the Environment resource has been changed",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Active state of the Environment resource "
                            f"*<https://{public_ip}/resources/{resource_id}?"
                            f"organizationId={org_id}|{resource_name}>* from "
                            f"organization *{org_name}* has been changed from "
                            f"*{previous_state}* to *{new_state}*."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "See Environment details"
                        },
                        "action_id": "resource_details",
                        "value": resource_id
                    }
                ]
            }
        ],
        "unfurl_links": False
    }


def get_released_or_acquired_message(
        resource_id, resource_name, public_ip, org_id, org_name,
        upcoming_booking, booking_status, acquired=True):
    acquired_or_released = 'acquired' if acquired else 'released'
    common_blocks = [
        {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"The Environment resource *<https://{public_ip}/"
                            f"resources/{resource_id}?organizationId={org_id}|"
                            f"{resource_name}>* from organization *{org_name}*"
                            f" has been {acquired_or_released}."
                }
        },
        {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Booking status: {booking_status}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Book"
                    },
                    "value": resource_id,
                    "action_id": "add_booking"
                }
        }]

    upcoming_block = []
    if upcoming_booking:
        upcoming_block = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Upcoming booking*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Employee:\t\t\t{upcoming_booking['acquired_by']['name']}\n"
                            f"Since:\t\t\t\t\t{upcoming_booking['acquired_since']}\n"
                            f"Until: \t\t\t\t\t{upcoming_booking['released_at']}"
                }
            },
        ]

    env_details_btn = [
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "See Environment details"
                    },
                    "action_id": "resource_details",
                    "value": resource_id
                }
            ]
        }
    ]
    return {
        "text": f"The Environment resource has been {acquired_or_released}",
        "blocks": common_blocks + upcoming_block + env_details_btn,
        "unfurl_links": False
    }


def get_message_released(resource_id, resource_name, public_ip, org_id,
                         org_name, upcoming_booking, booking_status):
    return get_released_or_acquired_message(
        resource_id, resource_name, public_ip, org_id, org_name,
        upcoming_booking, booking_status, acquired=False)


def get_message_acquired(resource_id, resource_name, public_ip, org_id,
                         org_name, upcoming_booking, booking_status):
    return get_released_or_acquired_message(
        resource_id, resource_name, public_ip, org_id, org_name,
        upcoming_booking, booking_status, acquired=True)


def get_env_property_updated_block(env_properties, public_ip, resource_id):
    env_properties_blocks = []
    for prop in env_properties[:5]:
        env_properties_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Name:*\n{prop['name']}\n"
                        f"*Previous value:* \n{prop['previous_value']}\n"
                        f"*New value:*\n{prop['new_value']}"
            }
        })
    if len(env_properties) > 5:
        env_properties_blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Only first 5 changed properties are shown. "
                                f"See more details in <https://{public_ip}/"
                                f"resources/{resource_id}?tab=details"
                                f"|OptScale web console>"
                    }
                ]
            },
        )
    return env_properties_blocks


def get_current_env_property_block(curr_env_properties):
    blocks = [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Current Environment properties:*"
                }
            }]

    text = ''
    for prop_name, value in curr_env_properties.items():
        text = text + f"*{prop_name}:*\n{value}\n"

    if not text:
        text = '-'

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    })
    return blocks


def get_property_updated_message(resource_id, resource_name, public_ip, org_id,
                                 org_name, env_properties, current_properties,
                                 booking_status):
    start_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Property of the environment resource "
                            f"*<https://{public_ip}/resources/{resource_id}?"
                            f"organizationId={org_id}|{resource_name}>* from "
                            f"organization *{org_name}* has been changed:"
                }
            }
    ]
    env_prop_upd_blocks = get_env_property_updated_block(
        env_properties, public_ip, resource_id)
    env_prop_blocks = get_current_env_property_block(current_properties)
    end_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Booking status: {booking_status}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Book"
                    },
                    "value": resource_id,
                    "action_id": "add_booking"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "See Environment details"
                        },
                        "action_id": "resource_details",
                        "value": resource_id
                    }
                ]
            }
        ]
    blocks = start_blocks + env_prop_upd_blocks + env_prop_blocks + end_blocks
    return {
        "text": f"The Environment resource property has been updated",
        "blocks": blocks,
        "unfurl_links": False
    }
