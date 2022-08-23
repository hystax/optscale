__all__ = ['get_org_message', 'get_org_switch_blocks', 'get_org_switch_message',
           'get_org_switch_completed_message']


def get_org_message(org, active=False):
    if active:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{org['name']}*   `Active`",
            }
        }
    else:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{org['name']}*",
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Choose"
                },
                "value": org['id'],
                "action_id": "choose_organization",
            }
        }


def get_org_switch_blocks(orgs, active_org_id):
    divider = {"type": "divider"}
    singular_plural_org = 'organization' if len(orgs) == 1 else 'organizations'

    org_switch_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"You are member of {len(orgs)} {singular_plural_org} in "
                        f"OptScale."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Please choose which one should be set active "
                        "(I'll remember it for your futher actions):"
            }
        },
        divider
    ]
    for org in orgs:
        org_message = get_org_message(org, org['id'] == active_org_id)
        org_switch_blocks.append(org_message)
    org_switch_blocks.append(divider)
    return org_switch_blocks


def get_org_switch_message(orgs, active_org_id):
    return {
        'blocks': get_org_switch_blocks(orgs, active_org_id),
        'text': 'Switch organization'
    }


def get_org_switch_completed_message(org_name):
    bold_org_name = f'*{org_name}*'
    return {
        "text": f"You have set {org_name} as your current active organization.",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"You have set {bold_org_name} as your current "
                            f"active organization.",
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": ":pushpin: You can always check the list of "
                                "your organizations by sending `org` message"
                    },
                    {
                        "type": "mrkdwn",
                        "text": ":calendar: Check the list of your environments"
                                " in the organization by sending `envs` message"
                    },
                    {
                        "type": "mrkdwn",
                        "text": ":cloud: Check the list of your resources in "
                                "the organization by sending `resources` "
                                "message"
                    },
                    {
                        "type": "mrkdwn",
                        "text": ":bell: Get a list of alerts and manage them "
                                "(requires a manager role) by sending "
                                "`alerts` message"
                    },
                    {
                        "type": "mrkdwn",
                        "text": ":runner: Log out current Slack user from "
                                "OptScale by sending `logout` message"
                    }
                ]
            }
        ]
    }
