import numbers
import pystache
import collections.abc
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from herald.modules.template_generator.template_generator import get_default_template


LOG = logging.getLogger(__name__)


def _generate_context(template_params, config_client):
    def update_template(template, params):
        for key, value in params.items():
            if isinstance(value, collections.abc.Mapping):
                template[k] = update_template(template.get(key, {}), value)
            else:
                template[k] = value
        return template

    def get_numbered_params(params_dict):
        numbered_dict = {}
        for key, value in params_dict.items():
            if isinstance(value, numbers.Number):
                numbered_dict[k] = value
        return numbered_dict

    def update_template_style(numbered_dict):
        style = {}
        display_visibility_name = 'element_visibility_%s'
        for key, value in numbered_dict.items():
            style[display_visibility_name % k] = 'table-row' if value else 'none'
        return style

    def generate_control_panel_parameters(organization_map):
        control_panel_keys_map = {'id': 'organizationId'}
        list_params = []
        for input_key, output_key in control_panel_keys_map.items():
            if organization_map.get(input_key):
                list_params.append('%s=%s' % (output_key, organization_map[input_key]))
        return "?" + '&'.join(list_params) if list_params else None
    default_template = get_default_template()
    texts = template_params.get('texts', {})
    numbered_dict = get_numbered_params(texts)
    organization_info = texts.get('organization', {})
    texts['control_panel_parameters'] = generate_control_panel_parameters(organization_info)
    texts['etcd'] = {}
    texts['etcd']['control_panel_link'] = config_client.get('/public_ip').value
    template = update_template(default_template, template_params)
    template['style'] = update_template_style(numbered_dict)
    for k, etcd_k in template.get('etcd', {}).items():
        etcd_v = ''
        try:
            etcd_v = config_client.get(etcd_k).value
        except Exception:
            pass
        template['etcd'].update({k: etcd_v})
    return template


def generate_email(config_client, to, subject, template_params,
                   template_type=None, reply_to_email=None,
                   frm='noreply@hystax.com'):
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = frm
    msg['To'] = to
    if reply_to_email:
        msg['reply-to'] = reply_to_email
    context = _generate_context(template_params, config_client)
    msg.attach(_generate_body(context, template_type))
    return msg


def get_templates_path():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(dir_path, 'templates')
    return template_path


def _generate_body(context, template_type='default'):
    template_path = os.path.join(
        get_templates_path(), '%s.html' % template_type)
    with open(template_path, 'r', encoding="utf-8") as tmp:
        base_email_template = tmp.read()
    body = MIMEText(pystache.render(base_email_template, context), 'html')
    return body
