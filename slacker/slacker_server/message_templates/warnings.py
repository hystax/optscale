from slacker.slacker_server.message_templates.alerts import get_alert_section

__all__ = ['get_archived_message_block']


def get_archived_message_block(public_ip, pool_id, organization_id, pool_name,
                               limit, based, threshold, threshold_type,
                               include_children, channel_id, currency='USD'):
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Slack channel *{channel_id}*, contains configured "
                    f"OptScale alerts, is archived. Please recreate "
                    f"alert to pick new slack channel:"
        }},
        get_alert_section(public_ip, pool_id, organization_id, pool_name,
                          limit, based, threshold, threshold_type,
                          include_children, currency),
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"You will get alerts message to DM while it is not "
                        f"reconfigured to active slack channel:"
            }
        }]
