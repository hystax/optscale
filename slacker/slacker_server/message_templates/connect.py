from slacker_server.message_templates.org import get_org_switch_blocks

__all__ = ['get_welcome_message', 'get_connection_done_message']


def get_welcome_message(public_ip, secret):
    return {
        "text": "Hi there",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hi there :wave:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Great to see you! OptScale App helps you monitor "
                            "and control your cloud resources and expenses "
                            "right here in Slack. These are just a few "
                            "things that you will be able to do:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• Monitor your resources and their expenses\n• "
                            "Control resources TTL settings\n• Get notified "
                            "of important events regarding your resources"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "But before you can do all these amazing things, "
                            "we need you to connect your OptScale user account "
                            "to this Slack App."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Follow this link to authorize yourself in OptScale"
                            f" - \n<https://{public_ip}/slack/connect/{secret}>"
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
                        "text": "Not sure if your team already uses OptScale? "
                                "Check with your manager and if not - show "
                                f"them our *<https://{public_ip}/live-demo|"
                                "live demo>*."
                    }
                ]
            }
        ],
        "unfurl_links": False
    }


def get_connection_done_message(orgs, user_email, active_org_id):
    congratulations_base = "Congratulations, you're now connected with " \
                           "your OptScale account"
    help_msg = {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": ":pushpin: You can always check the list of your "
                        "organizations by sending `org` message"
            }
        ]
    }
    connection_done_tmp = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{congratulations_base} _{user_email}_!"
        }
    }
    return {
        'blocks': [
            b for b in [connection_done_tmp] + [
                org for org in get_org_switch_blocks(orgs, active_org_id)
            ] + [help_msg]
        ],
        'text': congratulations_base,
        'unfurl_links': False
    }
