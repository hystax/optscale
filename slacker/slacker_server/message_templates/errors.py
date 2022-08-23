__all__ = ['get_ca_not_connected_message',
           'get_not_have_slack_permissions_message']


def get_ca_not_connected_message(org_name, public_ip):
    bold_org_name = f'*{org_name}*'

    header_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":warning: Cloud Account error!",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"No cloud accounts are connected for organization {bold_org_name}"
            }
        }
    ]
    footer_blocks = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":pushpin: Setting up cloud accounts are "
                            f"available in <https://{public_ip}/"
                            f"cloud-accounts|OptScale web console>"
                }
            ]
        }
    ]
    return {
        "text": f":warning: Cloud Account error!",
        "blocks": header_blocks + footer_blocks,
        "unfurl_links": False
    }


def get_not_have_slack_permissions_message():

    header_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":warning: Slack permissions error!",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Application doesn’t have enough permissions. Please "
                        f"reinstall it or connect support@hystax.com for "
                        f"assistance."
            }
        }
    ]
    return {
        "text": f":warning: Cloud Account error!",
        "blocks": header_blocks,
    }
