from rest_api.rest_api_server.controllers.disconnect_survey import DisconnectSurveyAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task


class DisconnectSurveyAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return DisconnectSurveyAsyncController

    async def post(self, organization_id, **url_params):
        """
         ---
        description: |
         Disconnect Survey
         Required permission: INFO_ORGANIZATION
        tags: [disconnect_survey]
        summary: Sends service email with Disconnect Survey results
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Survey data
            required: true
            schema:
                type: object
                properties:
                    survey_type:
                        type: string
                        description: Type of Survey
                        required: True
                        example: Disconnect Survey
                    payload:
                        type: object
                        description: "specific data for Survey"
        responses:
            204:
                description: No content
            400:
             description: |
                 Wrong arguments:
                 - OE0212: Unexpected parameters
                 - OE0547: Payload should be less than %d bytes
            404:
             description: |
                 Not found:
                 - OE0005: Organization doesn't exist
            403:
             description: |
                 Forbidden:
                 - OE0234: Forbidden
            401:
             description: |
                 Unauthorized:
                 - OE0235: Unauthorized
                 - OE0237: This resource requires authorization
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        data = self._request_body()
        await run_task(self.controller.submit, organization_id, **data)
        self.set_status(204)
