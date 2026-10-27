import logging
from typing import List

from zcrmsdk.src.com.zoho.crm.api.record import Record, Field
from zcrmsdk.src.com.zoho.crm.api.record.success_response import SuccessResponse
from zcrmsdk.src.com.zoho.crm.api.util import Choice

from tools.zoho_integrator.zoho_client import ZohoClient, RecordNotFoundException


FULL_NAME_SEP = " "
LAST_NAME_PLACE_HOLDER = "NOT_SET_IN_FORM"
LEADS_MODULE_NAME = "Leads"
CONTACTS_MODULE_NAME = "Contacts"
MODULES_FOR_SYNC = [CONTACTS_MODULE_NAME, LEADS_MODULE_NAME]

UTM_FIELDS = [
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'
]

LOG = logging.getLogger(__name__)


class ZohoIntegrator:
    def __init__(self, zoho_client: ZohoClient):
        self.client = zoho_client

    def find_existing_record(self, email: str):
        target_module = None
        user = None
        for module in MODULES_FOR_SYNC:
            try:
                record = self.client.find_record(email, module)
                if record:
                    target_module = module
                    user = record
                    break
            except RecordNotFoundException:
                LOG.debug(
                    "Zoho: No record found for email %s in module %s",
                    email, module
                )
                continue
        return user, target_module

    @staticmethod
    def _get_first_last_names(full_name: str) -> List[str]:
        if not full_name:
            return [LAST_NAME_PLACE_HOLDER, LAST_NAME_PLACE_HOLDER]
        if FULL_NAME_SEP in full_name:
            return full_name.split(FULL_NAME_SEP)[:2]
        else:
            return [full_name, LAST_NAME_PLACE_HOLDER]

    def _build_new_record(self, email: str, full_name: str,
                          lead_source: str, lead_source_description: str,
                          email_opt_out: bool = True,
                          utm_fields: dict = None) -> Record:
        first_name, last_name = self._get_first_last_names(full_name)
        record = Record()
        record.add_field_value(Field.Leads.last_name(), last_name)
        record.add_field_value(Field.Leads.first_name(), first_name)
        record.add_field_value(Field.Leads.full_name(), full_name)
        record.add_field_value(Field.Leads.email(), email)
        record.add_field_value(Field.Leads.lead_source(),
                               Choice(lead_source))
        # Lead_Source_Description is not in the standard Leads fields,
        # setting it manually via generic Field.
        record.add_field_value(
            Field("Lead_Source_Description"), lead_source_description
        )
        record.add_field_value(Field.Leads.email_opt_out(), email_opt_out)
        if utm_fields:
            for key in UTM_FIELDS:
                value = utm_fields.get(key)
                if value:
                    record.add_field_value(Field(key), value)
        return record

    def _apply_utm_fields(self, record: Record, utm_fields: dict) -> bool:
        modified = False
        for key in UTM_FIELDS:
            incoming = utm_fields.get(key)
            if not incoming:
                continue
            current = record.get_key_value(key)
            if current:
                current_values = [v.strip() for v in current.split(',')]
                if incoming in current_values:
                    continue
                new_value = f"{current},{incoming}"
            else:
                new_value = incoming
            record.add_field_value(Field(key), new_value)
            modified = True
        return modified

    def create_or_update(self, email: str, full_name: str,
                         lead_source: str, lead_source_description: str,
                         tags: List[str], email_opt_out: bool = None,
                         utm_fields: dict = None) -> None:
        LOG.info(
            "Zoho: Starting sync for email %s, lead_source=%s, tags=%s",
            email, lead_source, tags
        )
        modified = False
        user, target_module = self.find_existing_record(email)
        if user:
            LOG.info(
                "Zoho: Found existing record for email %s in module %s "
                "(id=%s)", email, target_module, user.get_id()
            )
            api_name = Field.Leads.last_name().get_api_name()
            if user.get_key_value(api_name) == LAST_NAME_PLACE_HOLDER:
                LOG.debug(
                    "Zoho: Last name is placeholder for email %s, "
                    "checking update", email
                )
                _, new_last_name = self._get_first_last_names(full_name)
                if new_last_name and new_last_name != LAST_NAME_PLACE_HOLDER:
                    LOG.info(
                        "Zoho: Updating last name placeholder for email %s",
                        email
                    )
                    user.add_field_value(Field.Leads.last_name(), new_last_name)
                    modified = True
            if email_opt_out is not None:
                current_opt_out = user.get_key_value(
                    Field.Leads.email_opt_out().get_api_name())
                if current_opt_out != email_opt_out:
                    user.add_field_value(
                        Field.Leads.email_opt_out(), email_opt_out)
                    modified = True
            if utm_fields:
                utm_modified = self._apply_utm_fields(user, utm_fields)
                if utm_modified:
                    modified = True
        else:
            LOG.info(
                "Zoho: No existing record for email %s, creating new Lead",
                email
            )
            if email_opt_out is None:
                email_opt_out = True
            target_module = LEADS_MODULE_NAME
            user = self._build_new_record(
                email, full_name, lead_source, lead_source_description,
                email_opt_out, utm_fields
            )
            modified = True

        if modified:
            # Email must be included in upsert request,
            # otherwise Zoho creates a new lead instead of updating.
            user.add_field_value(Field.Leads.email(), email)
            LOG.info("Zoho: Upserting record for email %s in module %s",
                     email, target_module)
            data = self.client.upsert_record(user, target_module)
            LOG.info("Zoho: Upsert result for email %s: %s",
                     email, data)
            result = data[0]
            if not isinstance(result, SuccessResponse):
                LOG.error("Zoho upsert failed: %s", result)
                return
            record_id = result.get_details().get("id")
        else:
            record_id = user.get_id()
            LOG.info(
                "Zoho: No modifications needed for email %s, record id=%s",
                email, record_id
            )
        LOG.info("Zoho: Adding tags %s to record with id %s",
                 tags, record_id)
        self.client.add_tags(target_module, record_id, tags)
        LOG.info(
            "Zoho: sync completed for email %s, record id=%s, tags=%s",
            email, record_id, tags
        )
