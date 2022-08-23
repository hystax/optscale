import http
import logging
from typing import List, Union

from zcrmsdk.src.com.zoho.api.authenticator import OAuthToken, TokenType
from zcrmsdk.src.com.zoho.api.authenticator.store import FileStore
from zcrmsdk.src.com.zoho.crm.api import (
    Initializer,
    UserSignature,
    SDKConfig,
    ParameterMap,
    HeaderMap,
)
from zcrmsdk.src.com.zoho.crm.api.record import (
    RecordOperations,
    SearchRecordsParam,
    GetRecordsParam,
    ResponseWrapper,
    Record,
    BodyWrapper,
    ActionWrapper,
)
from zcrmsdk.src.com.zoho.crm.api.tags import TagsOperations, AddTagsToRecordParam
from zcrmsdk.src.com.zoho.crm.api.util import APIResponse

from zoho_integrator.registered_app import RegisteredApp

LOG = logging.getLogger(__file__)

ZOHO_SDK_TOKENS_FILE = "zoho_tokens.csv"
ZOHO_SDK_RESOURCES_DIR = "zoho_resources"


class RecordNotFoundException(Exception):
    pass


class APIFailedException(Exception):
    pass


class ZohoClient:
    def __init__(self, app: RegisteredApp):
        self._initialized = False
        self.app = app
        self._initialize()

    def _initialize(self) -> None:
        try:
            token = self._get_token()
            Initializer.initialize(
                user=UserSignature(email=self.app.email),
                environment=self.app.env,
                token=token,
                store=FileStore(file_path=ZOHO_SDK_TOKENS_FILE),
                sdk_config=SDKConfig(
                    auto_refresh_fields=False, pick_list_validation=False
                ),
                resource_path=ZOHO_SDK_RESOURCES_DIR,
            )
            self._initialized = True
        except Exception as e:
            LOG.error(f"Wasn't able to initialize zoho client. Err: {str(e)}")
            raise

    def _get_token(self) -> OAuthToken:
        return OAuthToken(
            client_id=self.app.client_id,
            client_secret=self.app.client_secret,
            token=self.app.ref_token,
            token_type=TokenType.REFRESH,
            redirect_url=self.app.redirect_uri,
        )

    def find_record(self, email: str, module: str) -> Record:
        record_operations_instance = RecordOperations()
        param_instance = ParameterMap()
        param_instance.add(SearchRecordsParam.email, email)
        param_instance.add(GetRecordsParam.per_page, 1)
        param_instance.add(GetRecordsParam.page, 1)
        header_instance = HeaderMap()
        response = record_operations_instance.search_records(
            module, param_instance, header_instance
        )
        list_of_objects = self.handle_api_response(response)
        if list_of_objects:
            return list_of_objects[0]
        raise RecordNotFoundException

    def handle_api_response(self, response: APIResponse) -> Union[List, object]:
        if response is not None:
            status_code = response.get_status_code()
            if not (http.HTTPStatus.BAD_REQUEST > status_code >= http.HTTPStatus.OK):
                LOG.error(f"API request has failed. Status code: {status_code}")
                raise APIFailedException()
            data = response.get_object()
            if isinstance(data, ResponseWrapper) or isinstance(data, ActionWrapper):
                data = data.get_data()
                return data
            else:
                return data

    def upsert_record(self, record: Record, module: str) -> Union[List, object]:
        record_operations = RecordOperations()
        request = BodyWrapper()
        records_list = [record]
        request.set_data(records_list)
        header_instance = HeaderMap()
        response = record_operations.upsert_records(module, request, header_instance)
        data = self.handle_api_response(response)
        return data

    def add_tags(
        self, module: str, id_: int, tag_names: List[str]
    ) -> Union[List, object]:
        LOG.info(f"Add tags {tag_names} to record with id {id_}")
        tags_operations = TagsOperations()
        param_instance = ParameterMap()
        for tag_name in tag_names:
            param_instance.add(AddTagsToRecordParam.tag_names, tag_name)
        param_instance.add(AddTagsToRecordParam.over_write, "false")
        response = tags_operations.add_tags_to_record(id_, module, param_instance)
        data = self.handle_api_response(response)
        return data
