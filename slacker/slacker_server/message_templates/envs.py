from slacker.slacker_server.message_templates.common import get_resource_type_location

__all__ = ['get_envs_message', 'get_env_resource_block']


def get_envs_message(org_id, org_name, resources, resource_status_map,
                     public_ip):
    bold_org_name = f'*{org_name}*'
    header_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Here is the list of your Environments "
                        f"in {bold_org_name}",
            }
        }
    ]

    footer_blocks = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":pushpin: More resources and details are "
                            f"available in <https://{public_ip}/environments"
                            f"?organizationId={org_id}|OptScale web console>"
                }
            ]
        }
    ]

    if not resources:
        resource_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You don’t have any Environments "
                            f"in {bold_org_name}"
                }
            }
        ]
    else:
        resource_blocks = []
        for r in resources:
            resource_blocks.extend(get_env_resource_block(
                r, resource_status_map, public_ip, org_id))
    return {
        "text": f"Here is the list of your environments in {org_name}",
        "blocks": header_blocks + resource_blocks + footer_blocks,
        "unfurl_links": False
    }


def get_env_resource_block(resource, resource_status_map, public_ip, org_id):
    r_id = resource['id']
    r_name = resource.get('name')
    booking_status = resource_status_map[r_id]
    short_id = r_id[:4]
    return [{
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*<https://{public_ip}/resources/{r_id}"
                        f"?organizationId={org_id}|{r_name}>*\n"
            },
            {
                "type": "mrkdwn",
                "text": f"_*{get_resource_type_location(resource)}*_"
            }
        ],
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "emoji": True,
                "text": "Details"
            },
            "value": r_id,
            "action_id": "resource_details"
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
                "value": r_id,
                "action_id": "add_booking"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f":id: {short_id}"
                }
            ]
        },
        {
            "type": "divider"
        }
    ]
