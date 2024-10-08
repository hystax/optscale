from slacker.slacker_server.message_templates.common import get_resource_type_location
from currency_symbols.currency_symbols import CURRENCY_SYMBOLS_MAP as CURRENCY_MAP

__all__ = ['get_resource_blocks', 'get_resources_message']


def get_resource_blocks(resource_data, public_ip, org_id, currency='USD'):
    c_sign = CURRENCY_MAP.get(currency, '')
    r_id = resource_data['resource_id']
    r_cid = resource_data['cloud_resource_id']
    short_id = r_id[:4]
    r_name = resource_data.get('resource_name', '')
    r_ttl_constr = resource_data.get('ttl')
    r_total_exp_constr = resource_data.get('total_expense_limit')
    r_daily_exp_constr = resource_data.get('daily_expense_limit')

    ttl_msg = ''
    if r_ttl_constr is not None:
        if r_ttl_constr <= -1:
            ttl_msg = ":exclamation: *TTL expired {} hours ago*".format(
                abs(int(r_ttl_constr)))
        elif -1 < r_ttl_constr <= 0:
            ttl_msg = ":exclamation:*TTL expired < 1 hour ago*"
        elif 0 < r_ttl_constr <= 1:
            ttl_msg = ":warning: TTL expires in the next hour"
        elif r_ttl_constr > 1:
            ttl_msg = ":warning: TTL expires in {} hours".format(
                int(r_ttl_constr))

    total_exp_msg = ''
    if r_total_exp_constr is not None:
        if r_total_exp_constr < resource_data['cost']:
            total_exp_msg = (":exclamation: *Total expense limit is {0}{1}*"
                             .format(r_total_exp_constr, c_sign))
        elif r_total_exp_constr >= resource_data['cost']:
            total_exp_msg = (":warning: Total expense limit is {0}{1}"
                             .format(r_total_exp_constr, c_sign))

    daily_exp_msg = ''
    if r_daily_exp_constr is not None:
        if r_daily_exp_constr < resource_data['cost']:
            daily_exp_msg = (":exclamation: *Daily expense limit is {0}{1}*"
                             .format(r_daily_exp_constr, c_sign))
        elif r_daily_exp_constr >= resource_data['cost']:
            daily_exp_msg = (":warning: Daily expense limit is {0}{1}"
                             .format(r_daily_exp_constr, c_sign))

    header_block = [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*<https://{public_ip}/resources/{r_id}"
                            f"?organizationId={org_id}|{r_cid}>*\n{r_name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"_*{get_resource_type_location(resource_data)}*_\n"
                            f":moneybag: {c_sign}{resource_data['cost']:.2f}"
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
        }
    ]

    footer_block = [
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

    if ttl_msg:
        constr_block = [{
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"{ttl_msg}\t\t{total_exp_msg}\t\t{daily_exp_msg}"
                }
            ]
        }]
    elif total_exp_msg:
        constr_block = [{
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"{total_exp_msg}\t\t{daily_exp_msg}"
                }
            ]
        }]
    elif daily_exp_msg:
        constr_block = [{
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"{daily_exp_msg}"
                }
            ]
        }]
    else:
        constr_block = []

    shareable_block = []
    if resource_data.get('shareable'):
        shareable_block = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "This resource is an Environment"
            }
        }]
    return header_block + constr_block + shareable_block + footer_block


def get_resources_message(org_id, org_name, shown_data, total_count,
                          total_sum, public_ip, currency='USD'):
    c_sign = CURRENCY_MAP.get(currency, '')
    bold_org_name = f'*{org_name}*'
    shown_count = len(shown_data)
    shown_sum = round(sum([e['cost'] for e in shown_data]), 2)

    total_text_template = f"{shown_count} out of {total_count} resources shown\n"\
                          f"{c_sign}{shown_sum} out of {c_sign}{total_sum} " \
                          f"total expenses shown"
    if not total_count:
        total_text_template = f"You don’t own any active resources in {bold_org_name}"

    header_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Here is the list of your active resources "
                        f"in {bold_org_name}",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": total_text_template
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
                            f"available in <https://{public_ip}/resources"
                            f"?organizationId={org_id}|OptScale web console>"
                }
            ]
        }
    ]
    resource_blocks = []
    for e in shown_data:
        resource_blocks.extend(get_resource_blocks(e, public_ip, org_id,
                                                   currency))
    return {
        "text": f"Here is the list of your active resources in {org_name}",
        "blocks": header_blocks + resource_blocks + footer_blocks,
        "unfurl_links": False
    }
