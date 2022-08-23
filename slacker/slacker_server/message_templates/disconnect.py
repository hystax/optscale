__all__ = ['get_disconnected_message', 'get_disconnect_confirmation_message']


def get_disconnected_message(user_email, public_ip):
    italic_user_email = '_{}_'.format(user_email)
    return {
        "text": "You have disconnected your OptScale account "
                f"{user_email} from this Slack user.",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You have disconnected your OptScale account "
                            f"{italic_user_email} from this Slack user."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You are still able to use OptScale using Web UI "
                            f"at <https://{public_ip}/>",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Say me anything if you want to connect back. "
                            "I'll be waiting right here. :wave:"
                }
            }
        ],
        "unfurl_links": False
    }


def get_disconnect_confirmation_message(user_email, public_ip):
    italic_user_email = '_{}_'.format(user_email)
    return {
        "text": "You are about to disconnect your OptScale "
                f"account {user_email} from this Slack user.",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You are about to disconnect your OptScale "
                            f"account {italic_user_email} from this Slack user."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You will still able to use OptScale using Web UI "
                            f"at <https://{public_ip}/>"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please confirm disconnection:"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Disconnect"
                        },
                        "style": "danger",
                        "action_id": "account_disconnect",
                    }
                ]
            }
        ],
        "unfurl_links": False
    }
