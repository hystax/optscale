from slacker_server.message_templates.common import get_resource_type_location

__all__ = ['get_constraint_violation_alert']


def get_constraint_violation_alert(org_id, org_name, violations, public_ip):
    constraint_str = 'several constraints' if len(
        violations) > 1 else 'constraint'
    header_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":bell:*Alert*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Resources you own in *{org_name}* have just "
                        f"violated {constraint_str}:"
            }
        }
    ]
    violation_blocks = []
    for violation in violations:
        r_id = violation.get('resource_id')
        r_cid = violation.get('cloud_resource_id')
        r_name = violation.get('resource_name')
        expired_map = {
            'ttl': 'TTL expired',
            'total_expense_limit': 'Total expense limit exceeded',
            'daily_expense_limit': 'Daily expense limit exceeded'
        }
        expired = expired_map.get(violation.get('type'))
        violation_blocks.extend([
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*<https://{public_ip}/resources/{r_id}"
                                f"?tab=constraints&organizationId={org_id}"
                                f"|{r_cid}>*\n{r_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"_*{get_resource_type_location(violation)}*_\n"
                                f":bangbang: {expired}"
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
                    "action_id": "resource_details",
                }
            },
            {
                "type": "divider"
            },
        ])
    footer_blocks = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f":pushpin: You can see all current constraints "
                            f"violations at <https://{public_ip}/resources"
                            f"?constraintViolated=true&organizationId={org_id}"
                            f"|OptScale web console>"
                }
            ]
        }
    ]
    return {
        "text": f"Resources you own in {org_name} have just violated "
                f"{constraint_str}",
        "blocks": header_blocks + violation_blocks + footer_blocks,
        "unfurl_links": False
    }
