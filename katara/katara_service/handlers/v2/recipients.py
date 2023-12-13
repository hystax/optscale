import json


from katara.katara_service.controllers.recipient import (
    RecipientAsyncController
)
from katara.katara_service.exceptions import Err
from katara.katara_service.handlers.v2.base import (
    BaseAsyncItemHandler,
    BaseAsyncCollectionHandler
)
from katara.katara_service.utils import ModelEncoder

from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError


PAYLOAD_MAP_PARAMS = {
    'user_ids': ('user_ids', str, True),
    'recipient_ids': ('recipient_ids', str, True),
    'scope_ids': ('scope_ids', str, True)
}


class RecipientAsyncItemHandler(BaseAsyncItemHandler):
    def _get_controller_class(self):
        return RecipientAsyncController

    async def get(self, recipient_id):
        """
        ---
        description: >
            Gets recipient with specified ID \n\n
            Required permission: CLUSTER_SECRET
        tags: [recipients]
        summary: Get recipient
        parameters:
        -   name: id
            in: path
            description: Recipient ID
            required: true
            type: string
        responses:
            200:
                description: Recipient data
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique recipient id"}
                        created_at: {type: integer,
                            description: "Created timestamp (service field)"}
                        role_purpose: {type: string,
                            description: "Role purpose of recipient"}
                        scope_id: {type: string,
                            description: "Recipient scope id"}
                        user_id: {type: string,
                            description: "Recipient user id"}
                        meta: {type: string,
                            description: "Recipient metadata"}
            401:
                description: |
                    Unauthorized:
                    - OKA0011: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OKA0010: Bad secret
            404:
                description: |
                    Not found:
                    - OKA0013: Recipient not found
        security:
        - secret: []
        """
        await super().get(recipient_id)

    async def patch(self, recipient_id, **kwargs):
        """
        ---
        tags: [recipients]
        summary: Edit recipient
        description: >
            Modifies a recipient with specified id \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: id
            in: path
            description: Recipient ID
            required: true
            type: string
        -   in: body
            name: body
            description: Recipient changes
            required: true
            schema:
                type: object
                properties:
                    meta: {type: string,
                        description: "Recipient metadata"}
        responses:
            200:
                description: Recipient data
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique recipient id"}
                        created_at: {type: integer,
                            description: "Created timestamp (service field)"}
                        role_purpose: {type: string,
                            description: "Role purpose of recipient"}
                        scope_id: {type: string,
                            description: "Recipient scope id"}
                        user_id: {type: string,
                            description: "Recipient user id"}
                        meta: {type: string,
                            description: "Recipient metadata"}
            400:
                description: |
                    Wrong arguments:
                    - OKA0009: Incorrect request body received
                    - OKA0012: Unexpected parameters
                    - OKA0016: Incorrect meta format
                    - OKA0019: Parameter is immutable
            401:
                description: |
                    Unauthorized:
                    - OKA0011: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OKA0010: Bad secret
            404:
                description: |
                    Not found:
                    - OKA0013: Recipient not found
            409:
                description: |
                    Conflict:
                    - OKA0002: Recipient in scope already exists
        security:
        - secret: []
        """
        await super().patch(recipient_id, **kwargs)

    async def delete(self, _recipient_id, **kwargs):
        self.raise405()


class RecipientAsyncCollectionHandler(BaseAsyncCollectionHandler):
    def _get_controller_class(self):
        return RecipientAsyncController

    def get_request_data(self):
        return self.parse_url_params_into_payload(PAYLOAD_MAP_PARAMS)

    async def get(self, **kwargs):
        """
        ---
        tags: [recipients]
        summary: List recipients
        description: >
            Gets a list of recipients \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: scope_id
            in: path
            description: Recipient scope id (organization id)
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        recipients:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Unique recipient id"}
                                    created_at: {type: integer,
                                        description:
                                          "Created timestamp (service field)"}
                                    role_purpose: {type: string,
                                        description:
                                          "Role purpose of recipient"}
                                    scope_id: {type: string,
                                        description: "Recipient scope id"}
                                    user_id: {type: string,
                                        description: "Recipient user id"}
                                    meta: {type: string,
                                        description: "Recipient metadata"}
            400:
                description: |
                    Wrong arguments:
                    - OKA0021: Argument is not provided
            401:
                description: |
                    Unauthorized:
                    - OKA0011: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OKA0010: Bad secret
        security:
        - secret: []
        """
        scope_id = self.get_arg('scope_id', str)
        if not scope_id:
            raise OptHTTPError(400, Err.OKA0021, ['scope_id'])
        res = await self.controller.list(scope_id=scope_id)
        report_dict = {'recipients': [
            report.to_dict() for report in res]}
        self.write(json.dumps(report_dict, cls=ModelEncoder))

    async def post(self, **url_params):
        """
        ---
        tags: [recipients]
        summary: Create recipient
        description: >
            Adds a new recipient \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   in: body
            name: body
            description: Recipient to add
            required: true
            schema:
                type: object
                properties:
                    role_purpose: {type: string,
                        description: "Role purpose of recipient.
                          User id field must not be filled."}
                    scope_id: {type: string,
                        description: "Recipient scope id"}
                    user_id: {type: string,
                        description: "Recipient user id. Role Purpose field
                          must not be filled."}
                    meta: {type: string,
                        description: "Recipient metadata"}
        responses:
            201:
                description: Recipient data
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique recipient id"}
                        created_at: {type: integer,
                            description: "Created timestamp (service field)"}
                        role_purpose: {type: string,
                            description: "Role purpose of recipient"}
                        scope_id: {type: string,
                            description: "Recipient scope id"}
                        user_id: {type: string,
                            description: "Recipient user id"}
                        meta: {type: string,
                            description: "Recipient metadata"}
            400:
                description: |
                    Wrong arguments:
                    - OKA0009: Incorrect request body received
                    - OKA0012: Unexpected parameters
                    - OKA0016: Incorrect meta format
                    - OKA0021: scope_id not provided
                    - OKA0023: role_purpose or user_id not provided
                    - OKA0024: role_purpose or user_id required
                    - OKA0025: Invalid role_purpose
            401:
                description: |
                    Unauthorized:
                    - OKA0011: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OKA0010: Bad secret
            409:
                description: |
                    Conflict:
                    - OKA0002: Recipient in scope already exists
        security:
        - secret: []
        """
        await super().post(**url_params)

    async def delete(self, **kwargs):
        """
        ---
        tags: [recipients]
        summary: Delete recipients
        description: >
            Deletes recipients for specific lists \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: user_ids
            in: query
            description: list of user ids
            required: false
            type: array
            items:
                type: string
            collectionFormat: multi
        -   name: recipient_ids
            in: query
            description: list of recipient ids
            required: false
            type: array
            items:
                type: string
            collectionFormat: multi
        -   name: scope_ids
            in: query
            description: list of scope ids
            required: false
            type: array
            items:
                type: string
            collectionFormat: multi
        responses:
            204: {description: Success}
            401:
                description: |
                    Unauthorized:
                    - OKA0011: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OKA0010: Bad secret
        security:
        - secret: []
        """
        data = self.get_request_data()
        try:
            await self.controller.delete(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        self.set_status(204)
