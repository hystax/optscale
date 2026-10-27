import json

from rest_api.rest_api_server.controllers.policy_gen import (
    PolicyGeneratorControllerAsyncController)
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err


class PolicyGeneratorAsyncCollectionHandler(BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return PolicyGeneratorControllerAsyncController

    async def get(self, organization_id, **kwargs):
        """
        ---
        description: |
            Get clou policy for assumed accounts for organization
            Required permission: INFO_ORGANIZATION
        tags: [cloud_policy]
        summary: Policies for assumed cloud account
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: cloud_type
            in: query
            type: string
            description: Cloud type
            required: true
        -   name: linked
            in: query
            type: boolean
            description: is linked account
            required: false
        -   name: bucket_name
            in: query
            type: string
            description: Bucket name
            required: false
        -   name: external_id
            in: query
            type: string
            description: >
                ExternalId for the sts:AssumeRole trust policy condition
            required: false
        responses:
            200:
                description: Cloud accounts list
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0436: Provided unsupported cloud type
                    - OE0548: Argument is required

            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            424:
                description: |
                    Failed dependency:
                    - OE0570: Failed to get account id

        security:
        - token: []
        - secret: []
        """
        await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        args = self._request_arguments()
        allowed_args = ('bucket_name', 'cloud_type', 'linked', 'external_id')

        cloud_type = self.get_arg('cloud_type', str)
        linked = self.get_arg('linked', bool, False)
        bucket_name = self.get_arg('bucket_name', str, None)
        external_id = self.get_arg('external_id', str, None)

        if not cloud_type:
            raise OptHTTPError(400, Err.OE0548, ['cloud_type'])
        # bucket name is required for the non-linked account
        if not linked:
            if not bucket_name:
                raise OptHTTPError(400, Err.OE0548, ['bucket_name'])
        else:
            if bucket_name:
                # bucket name is unexpected for linked accounts
                raise OptHTTPError(400, Err.OE0212, ['bucket_name'])

        unexpected_args = list(filter(lambda x: x not in allowed_args,
                                      args.keys()))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])

        res = await run_task(self.controller.generate_policies,
                             cloud_type, bucket_name, linked, external_id)
        self.write(json.dumps(res, cls=ModelEncoder))
