from datetime import datetime, timedelta

__all__ = ['get_time_options', 'get_add_bookings_form', 'get_booking_block',
           'get_booking_details_message']


def get_time_options():
    options = []
    initial_option = None
    now = datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    minutes = 0
    while start != end:
        time = start.strftime('%I:%M%p').lower() + ' (UTC)'
        option = {
               "text": {
                   "type": "plain_text",
                   "text": time
               },
               "value": str(minutes)
           }
        if start - now < timedelta(minutes=30):
            initial_option = option
        options.append(option)
        minutes += 30
        start += timedelta(minutes=30)
    return options, initial_option


def get_add_bookings_form(resource, public_ip):
    now_date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")
    r_id = resource['id']
    r_name = resource.get('name')
    options, initial_option = get_time_options()
    return {
        "callback_id": "add_booking_view",
        "private_metadata": f"{r_id}/{r_name}",
        "title": {
            "type": "plain_text",
            "text": "Add booking",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "type": "modal",
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Fill the form to book Resource *{r_name}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Book since:*"
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "datepicker",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True
                    },
                    "action_id": "datepicker",
                    "initial_date": now_date,
                },
                "label": {
                    "type": "plain_text",
                    "text": "Select a date"
                },
                "block_id": "datepicker",
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
                    "initial_option": initial_option,
                    "options": options,
                    "action_id": "time_selector"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Select booking start time"
                },
                "block_id": "time_selector",
            },
            {
                "type": "section",
                "block_id": "book_period",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Select booking period:*"
                },
                "accessory": {
                    "type": "radio_buttons",
                    "action_id": "book_period",
                    "initial_option": {
                        "value": "0",
                        "text": {
                            "type": "plain_text",
                            "text": "unlimited"
                        }
                    },
                    "options": [
                        {
                            "value": "0",
                            "text": {
                                "type": "plain_text",
                                "text": "unlimited"
                            }
                        },
                        {
                            "value": "3",
                            "text": {
                                "type": "plain_text",
                                "text": "3 hours"
                            }
                        },
                        {
                            "value": "12",
                            "text": {
                                "type": "plain_text",
                                "text": "12 hours"
                            }
                        },
                        {
                            "value": "24",
                            "text": {
                                "type": "plain_text",
                                "text": "1 day"
                            }
                        },
                        {
                            "value": "168",
                            "text": {
                                "type": "plain_text",
                                "text": "1 week"
                            }
                        }
                    ]
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":pushpin: If you want to book "
                            f"Resource *{r_name}* for another time period, you"
                            f" can do it in <https://{public_ip}/environments|"
                            f"OptScale web console>"
                }
            }
        ]
    }


def get_booking_block(booking_id, employee_name, since, until,
                      allow_delete=False, allow_release=False):

    release_btn = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Release"
        },
        "action_id": "release_booking",
        "value": booking_id
    }

    delete_btn = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Delete"
        },
        "style": "danger",
        "action_id": "delete_booking",
        "value": booking_id
    }

    divider = {
        "type": "divider"
    }

    booking_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Employee:\t\t\t{employee_name}\n"
                        f"Since:\t\t\t\t\t{since}\n"
                        f"Until: \t\t\t\t\t{until}"
            }
        }]

    if allow_release and allow_delete:
        booking_blocks.append({
            "type": "actions",
            "elements": [release_btn, delete_btn]
        })
    elif allow_release:
        booking_blocks.append({
            "type": "actions",
            "elements": [release_btn]
        })
    elif allow_delete:
        booking_blocks.append({
            "type": "actions",
            "elements": [delete_btn]
        })
    booking_blocks.append(divider)
    return booking_blocks


def get_booking_details_message(public_ip, resource_id, resource_name, org_id,
                                org_name, bookings):
    header_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Here are the details of the Resource bookings you "
                        "asked"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*<https://{public_ip}/resources/{resource_id}"
                            f"?tab=details&organizationId={org_id}"
                            f"|{resource_name}>*"
                },
                {
                    "type": "mrkdwn",
                    "text": f"_*{org_name}*_"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Bookings*"
            }
        }
    ]

    booking_add_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":question:Want to setup a new booking?"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Book this Resource",
                    "emoji": True
                },
                "action_id": "add_booking",
                "value": f"{resource_id}"
            }
        },
        {
            "type": "divider"
        }]

    warning = {
        "type": "mrkdwn",
        "text": ":pushpin: Ony first 10 bookings are shown. See all Resource "
                f"bookings in <https://{public_ip}/environments"
                f"&organizationId={org_id}|OptScale web console>"
    }
    advice = {
        "type": "mrkdwn",
        "text": ":pushpin: You can also check this Resource details in "
                f"<https://{public_ip}/resources/{resource_id}?tab=details"
                f"&organizationId={org_id}|OptScale web console>"
    }
    footer_blocks = [{
        "type": "context",
        "elements": [advice]
    }]

    booking_blocks = []
    if not bookings:
        booking_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You don’t have any bookings for Resource"
                            f" {resource_name}"
                }
            }
        ]
    else:
        if len(bookings) == 10:
            footer_blocks = [{
                "type": "context",
                "elements": [warning, advice]
            }]

        for booking in bookings:
            booking_blocks.extend(get_booking_block(
                booking['id'], booking['acquired_by']['name'],
                booking['acquired_since'], booking['released_at'],
                booking.get('allow_delete'), booking.get('allow_release')))

    return {
        "text": "Here are the details of the Resource booking you asked",
        "blocks": (header_blocks + booking_blocks + booking_add_blocks +
                   footer_blocks),
        "unfurl_links": False
    }
