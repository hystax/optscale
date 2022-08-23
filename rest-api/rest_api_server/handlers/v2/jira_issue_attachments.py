from rest_api_server.exceptions import Err
from rest_api_server.utils import run_task, ModelEncoder
from rest_api_server.controllers.jira_issue_attachment import (
    JiraIssueAttachmentAsyncController)
from rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.base import BaseHandler
from optscale_exceptions.http_exc import OptHTTPError


class JiraIssueAttachmentCollectionHandler(BaseAsyncCollectionHandler,
                                           BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return JiraIssueAttachmentAsyncController

    def _validate_params(self, **kwargs):
        required = ['shareable_booking_id', 'client_key', 'project_key',
                    'issue_number', 'issue_link', 'status']
        optional = ['auto_detach_status']
        not_provided = list(filter(lambda x: x not in kwargs.keys(), required))
        if not_provided:
            raise OptHTTPError(400, Err.OE0216, [not_provided[0]])
        allowed_params = required + optional
        unexpected = list(filter(
            lambda x: x not in allowed_params, kwargs.keys()))
        if unexpected:
            raise OptHTTPError(400, Err.OE0212, [', '.join(unexpected)])

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of attachments for jira issue.
            Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [jira_issue_attachments]
        summary: "List of attachment for specified jira issue"
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   name: client_key
            in: query
            description: Jira issue tenant id
            required: true
            type: string
        -   name: project_key
            in: query
            description: Jira issue project id
            required: true
            type: string
        -   name: issue_number
            in: query
            description: Jira issue number
            required: true
            type: integer
        responses:
            200:
                description: attachment list
                schema:
                    type: object
                    properties:
                        jira_issue_attachments:
                            type: array
                            items:
                                type: object
                            example:
                                - id: e1a3bb04-d513-42d2-b9b7-019d24097dec
                                  project_key: OSB
                                  client_key: 99843c5d-462e-4f1b-8774-661cd108c8a7
                                  issue_number: 1234
                                  issue_link: https://example.atlassian.net/browse/OSB-1234
                                  auto_detach_status: Done
                                  status: Review
                                  created_at: 1632829593
                                  deleted_at: 0
                                  shareable_booking_id: aea929ab-3103-4932-a77c-ca0a758a992b
                                - id: 21285b43-c154-4d0a-b2cc-43ce26f1fb16
                                  project_key: OSB
                                  client_key: 99843c5d-462e-4f1b-8774-661cd108c8a7
                                  issue_number: 2345
                                  issue_link: https://example.atlassian.net/browse/OSB-2345
                                  auto_detach_status: Done
                                  status: Review
                                  created_at: 1632829593
                                  deleted_at: 0
                                  shareable_booking_id: 122bbeabf-4ad0-4467-bfcb-d1f6ada39f8e
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0378: User is not a member of organization
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        params = dict(
            organization_id=organization_id,
            client_key=self.get_arg('client_key', str, None),
            project_key=self.get_arg('project_key', str, None),
            issue_number=self.get_arg('issue_number', int, None),
        )
        res = await run_task(self.controller.list, **params)
        issue_attachments = {
            'jira_issue_attachments': [
                attachment.to_dict() for attachment in res
            ]
        }
        self.write(issue_attachments)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Attach jira issue to environment resource
            Required permission: TOKEN
        tags: [jira_issue_attachments]
        summary: Create shareable book schedule for resource
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: Shareable book schedule info
            required: true
            schema:
                type: object
                properties:
                    client_key:
                        type: string
                        description: "Jira tenant id"
                        required: True
                        example: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                    project_key:
                        type: string
                        description: "Jira project id"
                        required: True
                        example: OSB
                    issue_number:
                        type: integer
                        description: "Jira issue id"
                        required: True
                        example: 1234
                    issue_link:
                        type: string
                        description: "Resource id"
                        required: True
                        example: https://ex.atlassian.net/browse/OSB-1234
                    status:
                        type: string
                        description: "Issue status"
                        required: True
                        example: Review
                    shareable_booking_id:
                        type: string
                        description: "Shareable booking id"
                        required: True
                        example: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                    auto_detach_status:
                        type: string
                        description: "Auto detach on status"
                        required: False
                        example: Done
        responses:
            201:
                description: Created (returns created attachment object)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        client_key: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        project_key: OSB
                        issue_number: 1234
                        issue_link: https://example.atlassian.net/browse/OSB-2345
                        auto_detach_status: Done
                        status: Review
                        created_at: 1632829593
                        deleted_at: 0
                        shareable_booking_id: aea929ab-3103-4932-a77c-ca0a758a992b
                        created_at: 1587029026
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0233: Incorrect body received
                    - OE0384: Invalid resource type
                    - OE0416: Argument should not contain only whitespaces
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
                    - OE0501: Shareable booking belongs to another user
            404:
                description: |
                    Not found:
                    - OE0002: Argument not found
            409:
                description: |
                    Conflict:
                    - OE0502: Jira issue already attached to shareable booking
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        user_id = await self.check_self_auth()
        res = await run_task(self.controller.create,
                             organization_id=organization_id, user_id=user_id,
                             **data)
        self.set_status(201)
        self.write(res.to_json())


class JiraIssueAttachmentItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return JiraIssueAttachmentAsyncController

    async def get(self, id):
        """
        ---
        description: |
            Get jira issue attachment by ID
            Required permission: CLUSTER_SECRET or TOKEN
        tags: [jira_issue_attachments]
        summary: Get jira issue attachment
        parameters:
        -   name: id
            in: path
            description: Jira issue attachment ID
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        client_key: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        project_key: OSB
                        issue_number: 1234
                        issue_link: https://example.atlassian.net/browse/OS-2345
                        auto_detach_status: Done
                        status: Review
                        created_at: 1632829593
                        deleted_at: 0
                        shareable_booking_id: aea929ab-3103-4932-a77c-ca0a758a992b
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_self_auth()
        await super().get(id)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Update existing jira issue attachment
            Required permission: CLUSTER_SECRET or TOKEN
        tags: [jira_issue_attachments]
        summary: Update jira issue attachment
        parameters:
        -   name: id
            in: path
            description: Jira issue attachment id
            required: true
            type: string
        -   in: body
            name: body
            description: Jira issue attachment to modify
            required: true
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: Current issue status
                    auto_detach_status:
                        type: string
                        description: Current issue status
        responses:
            200:
                description: Success (returns modified value)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        client_key: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        project_key: OSB
                        issue_number: 1234
                        issue_link: https://example.atlassian.net/browse/OSB-2345
                        auto_detach_status: Done
                        status: Review
                        created_at: 1632829593
                        deleted_at: 0
                        shareable_booking_id: aea929ab-3103-4932-a77c-ca0a758a992b
            400:
                description: |
                    Wrong arguments:
                    - OE0003: Database error
                    - OE0177: Non unique parameters in get request
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0216: Argument is not provided
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0501: Shareable booking belongs to another user
            404:
                description: |
                    Not found:
                    - OE0002: Attachment not found
        security:
        - token: []
        - secret: []
        """
        user_id = None
        if not self.check_cluster_secret(raises=False):
            user_id = await self.check_self_auth()
        data = self._request_body()
        res = await run_task(
            self.controller.edit, item_id=id, user_id=user_id, **data)
        self.write(res.to_json())

    async def delete(self, id, **kwargs):
        """
        ---
        description: >
            Detach jira issue from environment
            Required permission: CLUSTER_SECRET or TOKEN
        tags: [jira_issue_attachments]
        summary: Detach jira issue
        parameters:
        -   name: id
            in: path
            description: Jira issue attachment ID
            required: true
            type: string
        responses:
            204: {description: Success}
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0234: Forbidden\n\n
                - OE0484: Deleting of shareable booking is not allowed\n\n
                - OE0501: Shareable booking belongs to another user."}
            404: {description: "Not found: \n\n
                - OE0002: ShareableBooking not found"}
        security:
        - token: []
        - secret: []
        """
        user_id = None
        if not self.check_cluster_secret(raises=False):
            user_id = await self.check_self_auth()
        await super().delete(id, user_id=user_id)
