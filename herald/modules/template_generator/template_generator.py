from datetime import datetime

# optscale images are also added to cdn, but not used in emails yet
# 'background': 'https://cdn.hystax.com/OptScale/email-header-background.png'
# 'logo_new': 'https://cdn.hystax.com/OptScale/email-images/logo-new.png'
# 'logo_optscale_beta_white': 'https://cdn.hystax.com/OptScale/email-images/logo-optscale-beta-white.png'


def generate_event_template_params(event, config_client):
    subject = 'Hystax OptScale Notification (%s) - %s' % (
        event.get('level'), event.get('evt_class'))
    template_params = {
        'images': {
            'level': _relevant_image_name(event.get('level')),
            'object_type': _relevant_image_name(event.get('object_type')),
        },
        'texts': {
            'object_name': event.get('object_name'),
            'title': 'Hystax notifications service',
            'top_text': 'You have received the following notification for the customer ',
            'bottom_text1': 'You have received this email because you have event notification turned on. Please use ',
            'bottom_text2': 'if you want to alter your notification settings.'
        }
    }
    additional_info = _get_additional_info(config_client, event)
    template_params['texts'].update(additional_info)
    return subject, template_params


def _get_additional_info(config_client, event):
    customer_name = ''
    return {
        "customer_name": customer_name
    }


def _get_control_panel_link(config_client):
    control_panel_link = ''
    try:
        control_panel_link = 'https://%s' % config_client.public_ip()
    except Exception:
        pass
    return control_panel_link


def _relevant_image_name(event_type):
    circle_grey_url = 'https://cdn.hystax.com/OptScale/email-images/circle-grey.png'
    return {
        'INFO': circle_grey_url,
        'SUCCESS': 'https://cdn.hystax.com/OptScale/email-images/circle-green.png',
        'WARNING': 'https://cdn.hystax.com/OptScale/email-images/circle-yellow.png',
        'ERROR': 'https://cdn.hystax.com/OptScale/email-images/triangle-red.png',
        'customer': 'https://cdn.hystax.com/OptScale/email-images/users.png',
        'cloudsite': 'https://cdn.hystax.com/OptScale/email-images/cloud.png',
        'device': 'https://cdn.hystax.com/OptScale/email-images/desktop.png',
        'agent': 'https://cdn.hystax.com/OptScale/email-images/shield.png',
    }.get(event_type, circle_grey_url)


def get_default_template():
    return {
        'images': {
            'logo': 'https://cdn.hystax.com/OptScale/email-images/logo-optscale-white.png',
            'optscale_banner': 'https://cdn.hystax.com/OptScale/email-images/optscale-welcome-banner.png',
            'telegram': 'https://cdn.hystax.com/OptScale/email-images/telegram.png',
            'optscale_ml_banner': 'https://cdn.hystax.com/OptScale/email-images/optscale-ml-welcome-banner.png',
            'optscale_mlops': 'https://cdn.hystax.com/OptScale/email-images/optscale-mlops-capabilities.png',
            'optscale_finops': 'https://cdn.hystax.com/OptScale/email-images/optscale-finops-capabilities.png',
        },
        'texts': {
            'product': 'Hystax OptScale',
            'dont_reply': 'Please do not reply to this email',
            'copyright': 'Copyright © 2016-%s' % datetime.utcnow().year,
            'address': '1250 Borregas Ave, Sunnyvale, CA 94089, USA',
            'phone': '+1 628 251-1280'
        },
        'etcd': {
            'control_panel_link': "/public_ip"
        },
        'links': {
            'linkedin': 'https://linkedin.com/company/hystax',
            'twitter': 'https://twitter.com/hystaxcom',
            'facebook': 'https://facebook.com/hystax',
            'telegram': 'https://t.me/hystax',
            'terms_of_use': 'https://hystax.com/terms-of-use/',
            'privacy_policy': 'https://hystax.com/privacy-policy/',
            'background_image':
                'https://cdn.hystax.com/OptScale/email-header-background.png'
        }
    }
