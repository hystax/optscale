import json

from datetime import datetime
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from slack_bolt.app import App
from slack_bolt.request import BoltRequest

from slacker.slacker_server.utils import ModelEncoder, tp_executor


class SlackBaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def initialize(self, app: App):
        self.app = app

    @property
    def bolt_request(self):
        return BoltRequest(
            body=self.request.body.decode("utf-8") if self.request.body else "",
            query=self.request.query,
            headers=self.request.headers,
        )

    def write_json(self, response):
        self.write(json.dumps(response, cls=ModelEncoder))

    def set_response(self, bolt_resp):
        self.set_status(bolt_resp.status)
        self.write(bolt_resp.body)
        for name, value in bolt_resp.first_headers_without_set_cookie().items():
            self.set_header(name, value)
        for cookie in bolt_resp.cookies():
            for name, c in cookie.items():
                expire_value = c.get("expires")
                expire = (
                    datetime.strptime(expire_value, "%a, %d %b %Y %H:%M:%S %Z")
                    if expire_value
                    else None
                )
                self.set_cookie(
                    name=name,
                    value=c.value,
                    max_age=c.get("max-age"),
                    expires=expire,
                    path=c.get("path"),
                    domain=c.get("domain"),
                    secure=True,
                    httponly=True,
                )


class SlackEventsHandler(SlackBaseHandler):
    async def post(self):
        bolt_resp = await IOLoop.current().run_in_executor(
            tp_executor, self.app.dispatch, self.bolt_request
        )
        self.set_response(bolt_resp)


class SlackOAuthHandler(SlackBaseHandler):
    async def get(self):
        if self.app.oauth_flow is not None:
            oauth_flow = self.app.oauth_flow
            if self.request.path == oauth_flow.install_path:
                bolt_resp = await IOLoop.current().run_in_executor(
                    tp_executor, oauth_flow.handle_installation, self.bolt_request
                )
                self.set_response(bolt_resp)
            elif self.request.path == oauth_flow.redirect_uri_path:
                bolt_resp = await IOLoop.current().run_in_executor(
                    tp_executor, oauth_flow.handle_callback, self.bolt_request
                )
                self.set_response(bolt_resp)
        else:
            self.set_status(404)


class SlackInstallPathHandler(SlackBaseHandler):
    def get(self):
        """
        ---
        description: |
            Get the installation path for the Slack app
            Required permission: none
        tags: [install_path]
        summary: Get the installation path for the Slack app
        responses:
            200:
                description: The installation path received successfully
                schema:
                    type: object
                    properties:
                        url:
                            type: string
                            description: the installation path
                            example: >
                                https://slack.com/oauth/v2/authorize?state=
                                de1070fe-02aa-4fc8-8565-c80968aa7c73&client_id=
                                111111111111.111111111111&scope=chat:write,im:history
                                ,chat:write.public,groups:write,channels:read,
                                groups:read&user_scope=
            404:
                description: |
                    Not Found
        """
        if self.app.oauth_flow is not None:
            oauth_flow = self.app.oauth_flow
            state = oauth_flow.issue_new_state(self.bolt_request)
            url = oauth_flow.build_authorize_url(state, self.bolt_request)
            set_cookie_value = (
                oauth_flow.settings.state_utils.build_set_cookie_for_new_state(state)
            )
            url_dict = {"url": url}
            self.set_header("set-cookie", set_cookie_value)
            self.write_json(url_dict)
        else:
            self.set_status(404)
