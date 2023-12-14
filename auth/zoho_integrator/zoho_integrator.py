import logging
from typing import List
from zcrmsdk.src.com.zoho.crm.api.record import Record, Field
from zcrmsdk.src.com.zoho.crm.api.util import Choice

from auth.zoho_integrator.zoho_client import (ZohoClient,
                                              RecordNotFoundException)


FULL_NAME_SEP = " "
LAST_NAME_PLACE_HOLDER = "NOT_SET_IN_FORM"
OPTSCALE_TAG = "OptScale"
OPTSCALE_REGISTRANT_TAG = "OptScale Registrant"
LEADS_MODULE_NAME = "Leads"
CONTACTS_MODULE_NAME = "Contacts"
MODULES_FOR_SYNC = [CONTACTS_MODULE_NAME, LEADS_MODULE_NAME]
TAGS_FOR_SYNC = [OPTSCALE_TAG, OPTSCALE_REGISTRANT_TAG]

DEFAULT_LEAD_SOURCE = "Website Optscale sign up"
DEFAULT_LEAD_SOURCE_DESCRIPTION = "Registration"
LOG = logging.getLogger(__file__)


class ZohoIntegrator:
    def __init__(self, zoho_client: ZohoClient):
        self.client = zoho_client

    def find_existing_record(self, email: str) -> (Record, str):
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
                    "Wasn't able to find record with email %s in module %s",
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

    def new_record(self, email: str, full_name: str) -> Record:
        first_name, last_name = self._get_first_last_names(full_name)
        record = Record()
        record.add_field_value(Field.Leads.last_name(), last_name)
        record.add_field_value(Field.Leads.first_name(), first_name)
        record.add_field_value(Field.Leads.full_name(), full_name)
        record.add_field_value(Field.Leads.email(), email)
        record.add_field_value(Field.Leads.lead_source(),
                               Choice(DEFAULT_LEAD_SOURCE))
        # For some reasons Lead_Source_Description doesn't exist in lead
        # fields. Set manually.
        record.add_field_value(
            Field("Lead_Source_Description"), DEFAULT_LEAD_SOURCE_DESCRIPTION
        )
        return record

    def create_or_update(self, email: str, full_name: str) -> None:
        modified = False
        user, target_module = self.find_existing_record(email)
        if user:
            LOG.info(
                "Found user with email %s in module %s. Updating...",
                email, target_module
            )
            api_name = Field.Leads.last_name().get_api_name()
            if user.get_key_value(api_name) == LAST_NAME_PLACE_HOLDER:
                LOG.debug("Found place holder in last name for existing user.")
                _, new_last_name = self._get_first_last_names(full_name)
                if new_last_name and new_last_name != LAST_NAME_PLACE_HOLDER:
                    LOG.debug(
                        "Updating last name from place holder to specified")
                    user.add_field_value(Field.Leads.last_name(),
                                         new_last_name)
                    # without adding this email field in request
                    # zoho server will create new lead instead of update
                    # existing
                    user.add_field_value(Field.Leads.email(), email)
                    modified = True
        else:
            LOG.info(
                "Wasn't able to find records with email %s in modules. "
                "Creating a new one", email
            )
            target_module = LEADS_MODULE_NAME
            user = self.new_record(email, full_name)
            modified = True
        if modified:
            LOG.info("User doesn't exist or was modified. Upsert record")
            data = self.client.upsert_record(user, target_module)
            LOG.info("Data %s", data)
            record_id = data[0].get_details().get("id")
        else:
            record_id = user.get_id()
        self.client.add_tags(target_module, record_id, TAGS_FOR_SYNC)
