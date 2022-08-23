import json
from tornado import gen
from optscale_exceptions.http_exc import OptHTTPError

from report_server.exceptions import Err
from report_server.handlers.v2.base import BaseReceiveHandler
from report_server.controllers.feedback import FeedbackAsyncController
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            UnauthorizedException)
from report_server.utils import ModelEncoder


class FeedbacksAsyncHandler(BaseReceiveHandler):

    def _get_controller_class(self):
        return FeedbackAsyncController

    def _validate_get_params(self, data):
        valid_keys = ['time_start', 'time_end', 'user_id', 'email', 'url',
                      'limit']
        self._validate(valid_keys, data)

    def _validate_post_params(self, data):
        valid_keys = ['email', 'url', 'text', 'metadata']
        self._validate(valid_keys, data)

    @staticmethod
    def _validate(valid_keys, data):
        if valid_keys is not None:
            request_keys = data.keys()
            for check_key in request_keys:
                if check_key not in valid_keys:
                    raise OptHTTPError(400, Err.OK0040, [check_key])

    @gen.coroutine
    def get(self):
        """
        ---
        description: |
          List feedbacks
          Required permission: CLUSTER_SECRET or POLL_EVENT
        tags: [feedbacks]
        summary: List feedbacks
        parameters:
        - name: time_start
          in: query
          description: start time in microseconds
          required: false
          type: integer
        - name: time_end
          in: query
          description: end time in microseconds
          required: false
          type: integer
        - name: user_id
          in: query
          description: return feedbacks with specified user_id
          required: false
          type: string
        - name: email
          in: query
          description: return feedbacks with specified email
          required: false
          type: string
        - name: url
          in: query
          description: return feedbacks with specified url
          required: false
          type: string
        - name: limit
          in: query
          description: max amount of feedbacks returned
          required: false
          type: integer
        responses:
          200:
            description: Success
            schema:
              type: array
              items:
                type: object
                example:
                  email: sd@hystax.com
                  url: dashboard
                  text: my first feedback
                  time: 1576046177
                  id: 5df08e6175a42f0001167799
                  user_id: 25c54588-86ef-45da-ab2b-593fe9b55e89
          400:
            description: |
              Wrong arguments:
              - OK0045: Invalid query parameter
              - OK0015: Wrong integer value
              - OK0040: Unexpected parameter
          401:
            description: |
              Unauthorized:
              - OK0003: Unauthorized
              - OK0005: This resource requires authorization
          403:
            description: |
              Forbidden:
              - OK0002: Forbidden
              - OK0006: Bad secret
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            yield self.check_permissions('POLL_EVENT', 'root', None)
        data = {
            'time_start': self.get_arg('time_start', int),
            'time_end': self.get_arg('time_end', int),
            'user_id': self.get_arg('user_id', str),
            'email': self.get_arg('email', str),
            'url': self.get_arg('url', str),
            'limit': self.get_arg('limit', int)
        }
        data = {k: v for k, v in data.items() if v is not None}
        self._validate_get_params(data)
        data.update({'token': self.token})
        try:
            res = yield gen.Task(self.controller.list, **data)
        except UnauthorizedException as exc:
            raise OptHTTPError.from_opt_exception(401, exc)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        self.write(json.dumps(res.result(), cls=ModelEncoder))

    @gen.coroutine
    def post(self, **kwargs):
        """
        ---
        description: |
          Submit feedback
          Required permission: TOKEN
        tags: [feedbacks]
        summary: Submit feedback
        parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              email:
                type: string
                required: true
                description: contact email
              text:
                type: string
                required: true
                description: feedback text
              url:
                type: string
                required: false
                description: url from which feedback sent
              metadata:
                type: string
                required: false
                description: json string with feedback metadata
        responses:
          201:
            description: Success (returns created object)
            schema:
              type: object
              example:
                email: sd@hystax.com
                url: dashboard
                text: my first feedback
                time: 1576046177
                id: 5df08e6175a42f0001167799
                user_id: 25c54588-86ef-45da-ab2b-593fe9b55e89
          400:
            description: |
              Wrong arguments:
              - OK0040: Unexpected parameter
          401:
            description: |
              Unauthorized:
              - OK0003: Unauthorized
              - OK0005: This resource requires authorization
        security:
        - token: []
        """
        yield self.check_token()
        data = self._request_body()
        self._validate_post_params(data)
        data.update({'token': self.token})
        yield super().post(**data)
