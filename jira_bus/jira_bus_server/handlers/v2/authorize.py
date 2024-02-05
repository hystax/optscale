from jira_bus.jira_bus_server.controllers.base import BaseAsyncController
from jira_bus.jira_bus_server.exceptions import Err
from jira_bus.jira_bus_server.handlers.v2.base import BaseHandler
from tools.optscale_exceptions.http_exc import OptHTTPError


class AuthorizeHandler(BaseHandler):
    def _get_controller_class(self):
        return BaseAsyncController

    async def post(self):
        """
        ---
        description: >
            Authorize JWT for Jira app\n\n
            Required permission: none
        tags: [authorize]
        summary: Authorize JWT for Jira plugin
        parameters:
        -   name: jwt
            in: body
            description: >
                Atlassian JWT to validate
            required: string
            type: string
        -   name: url
            in: body
            description: >
                URL to validate JWT
            required: true
            type: string
        -   name: method
            in: body
            description: >
                API method to validate JWT
            required: true
            type: string
            example: GET
        responses:
            200:
                description: OK
            403:
                description:
                -  OJ0018: Forbidden
        """
        try:
            params = self._request_body()
            jwt = params.get('jwt')
            url = params.get('url')
            method = params.get('method')
            await self.check_atlassian_auth(token=jwt, url=url, method=method)
        except OptHTTPError as exc:
            if exc.error_code == 'OJ0012':
                raise OptHTTPError(403, Err.OJ0018, [])
            raise exc
