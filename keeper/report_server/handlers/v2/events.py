from keeper.report_server.controllers.event import (
    EventAsyncController,
    EventCountAsyncController,
)
from keeper.report_server.handlers.v2.auth import (
    AuthHandler,
)
from keeper.report_server.handlers.v2.report import (
    ReportHandler,
)
from keeper.report_server.handlers.v2.receive import (
    ReceiveHandler,
)

from tools.optscale_exceptions.common_exc import (
    UnauthorizedException,
    NotFoundException,
    WrongArgumentsException,
    ForbiddenException,
)
from tools.optscale_exceptions.http_exc import OptHTTPError


class EventAsyncHandler(ReceiveHandler):
    def _get_controller_class(self):
        return EventAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
          List events
          Required permission: POLL_EVENT
        tags: [events]
        summary: List events
        parameters:
        - in: path
          name: organization_id
          description: id of the related organization
          type: string
          required: true
        - name: limit
          type: integer
          in: query
          required: false
          description: max amount of events returned
        - name: time_start
          type: integer
          in: query
          required: false
          description: start date in microseconds
        - name: time_end
          type: integer
          in: query
          required: false
          description: end date in microseconds
        - name: ack_only
          type: boolean
          in: query
          required: false
          description: >
            if True - return only events which require acknowledgement
        - name: level
          type: array
          in: query
          items:
            type: string
          collectionFormat: multi
          required: false
          description: return only events of the specified levels
        - name: object_type
          type: array
          in: query
          items:
            type: string
          collectionFormat: multi
          required: false
          description: return only events with specified object type
        - name: evt_class
          type: array
          in: query
          items:
            type: string
          collectionFormat: multi
          required: false
          description: return only events with specified event type
        - name: last_id
          type: string
          in: query
          required: false
          description: return events starting from time of the last_id event
        - name: include_read
          type: boolean
          in: query
          required: false
          description: if True - include events that are read
        - name: read_on_get
          type: boolean
          in: query
          required: false
          description: if True - mark all requested events as read
        responses:
          200:
            description: Success
            schema:
              type: array
              items:
                type: object
                example:
                  id: 59bb70044926aa000174131f
                  time: 1502975432
                  level: INFO
                  evt_class: ORGANIZATION_CREATED
                  object_id: 340e6f8b-6f9b-4af5-83c4-317938d6da6e
                  object_type: organization
                  object_name: My Test organization
                  organization_id: d3af8fba-9ef4-46c3-bab0-50835d54daad
                  description: Organization My Test organization
                    (d3af8fba-9ef4-46c3-bab0-50835d54daad) created
                  ack: true
                  acknowledged: 1502975555
                  acknowledged_by: 2af23d9fd3fb34693c3a95bbc21afb9f
                  acknowledged_user: John Doe (jdoe@email.com)
                  resolution": That will do
                  read: false
          400:
            description: |
              Wrong arguments:
              - OK0045: Invalid query parameter
              - OK0046: Wrong boolean value
              - OK0015: Wrong integer value
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
          404:
            description: |
              Not found:
              - K0004: Organization not found
        security:
        - token: []
        """
        try:
            await self.check_permissions("POLL_EVENT", "organization", organization_id)
            data = {
                "limit": self.get_arg("limit", int),
                "time_start": self.get_arg("time_start", int),
                "time_end": self.get_arg("time_end", int),
                "ack_only": self.get_arg("ack_only", bool),
                "last_id": self.get_arg("last_id", str),
                "include_read": self.get_arg("include_read", bool),
                "levels": self.get_arg("level", str, repeated=True),
                "object_types": self.get_arg("object_type", str, repeated=True),
                "evt_classes": self.get_arg("evt_class", str, repeated=True),
                "read_on_get": self.get_arg("read_on_get", bool),
                "organization_id": organization_id,
                "token": self.token,
            }
            data = {k: v for k, v in data.items() if v is not None}
            res = await self.controller.list(**data)
        except UnauthorizedException as exc:
            raise OptHTTPError.from_opt_exception(401, exc)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        self.write_json(res)

    async def post(self, organization_id, **kwargs):
        """
        ---
        description: |
          Submit event
          Required permission: CLUSTER_SECRET
        tags: [events]
        summary: Submit event
        parameters:
        - in: path
          name: organization_id
          description: id of the related organization
          type: string
          required: true
        - in: body
          name: body
          description: event properties
          required: true
          schema:
            type: object
            properties:
              level:
                type: string
                required: true
                description: event level
              evt_class:
                type: string
                required: true
                description: event class
              object_id:
                type: string
                required: false
                description: id of the related object
              object_type:
                type: string
                required: false
                description: type of the related object
              object_name:
                type: string
                required: false
                description: name of the related object
              description:
                type: string
                required: false
                description: event description
              localized:
                type: string
                required: false
                description: localized description
              ack:
                type: boolean
                required: true
                description: True if user acknowledgement required
              initiator_id:
                type: string
                required: false
                description: id of the user who initiated event
              initiator_name:
                type: string
                required: false
                description: name of the user who initiated event
        responses:
          201: {description: Success (returns created object)}
          400:
            description: |
              Wrong arguments:
              - OK0044: Error validating fields
          401:
            description: |
              Unauthorized:
              - OK0005: This resource requires authorization
          403:
            description: |
              Forbidden:
              - OK0006: Bad secret
        security:
        - secret: []
        """
        self.check_cluster_secret(raises=True)
        await super().post(organization_id=organization_id, **kwargs)

    async def patch(self, organization_id, **data):
        """
        ---
        description: |
          Acknowledge all events
          Required permission: ACK_EVENT
        tags: [events]
        summary: Acknowledge all events
        parameters:
        - in: path
          name: organization_id
          description: id of the related organization
          type: string
          required: true
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              resolution:
                type: string
                required: false
                description: resolution info
              timestamp:
                type: integer
                required: false
                description: acknowledge all events before timestamp
        responses:
          200: {description: Success}
          400:
            description: |
              Wrong arguments:
              - OK0028: Timestamp should be positive int
              - OK0030: Unexpected arguments
          401:
            description: |
              Unauthorized:
              - OK0003: Unauthorized
              - OK0005: This resource requires authorization
          403:
            description: |
              Forbidden:
              - OK0002: Forbidden
          404:
            description: |
              Not found:
              - K0004: Organization not found
        security:
        - token: []
        """
        await self.check_permissions("POLL_EVENT", "organization", organization_id)
        data = self._request_body()
        data.update({"token": self.token, "organization_id": organization_id})
        try:
            res = await self.controller.ack_all(**data)
        except UnauthorizedException as exc:
            raise OptHTTPError.from_opt_exception(401, exc)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        self.write_json(res)


class EventCountAsyncHandler(ReportHandler):
    def _get_controller_class(self):
        return EventCountAsyncController

    def get_request_data(self):
        data = {
            "token": self.token,
            "ack_only": self.get_arg("ack_only", bool),
            "levels": self.get_arg("level", str, repeated=True),
        }
        return {k: v for k, v in data.items() if v is not None}

    async def get(self, organization_id):
        """
        ---
        description: |
          Get event count
          Required permission: POLL_EVENT
        tags: [events]
        summary: Get event count
        parameters:
        - in: path
          name: organization_id
          type: string
          required: true
          description: id the organization
        - in: query
          name: ack_only
          type: boolean
          required: false
          description: only count event which require acknowledgement
        - name: levels
          type: array
          in: query
          items:
            type: string
          collectionFormat: multi
          required: false
          description: count only events of the specified levels
        responses:
          200:
            description: Success
            schema:
              type: object
              example:
                count: 30
                levels:
                - WARNING
                - ERROR
                - INFO
          400:
            description: |
              Wrong arguments:
              - OK0045: Invalid query parameter
              - OK0046: Wrong boolean value
          401:
            description: |
              Unauthorized:
              - OK0003: Unauthorized
              - OK0005: This resource requires authorization
          403:
            description: |
              Forbidden:
              - OK0002: Forbidden
          404:
            description: |
              Not found:
              - K0004: Organization not found
        security:
        - token: []
        """
        await self.check_permissions("POLL_EVENT", "organization", organization_id)
        data = self.get_request_data()
        data.update({"token": self.token, "organization_id": organization_id})
        try:
            res = await self.controller.get_count(**data)
        except UnauthorizedException as exc:
            raise OptHTTPError.from_opt_exception(401, exc)
        self.write_json(res)


class EventAckAsyncHandler(AuthHandler):
    def _get_controller_class(self):
        return EventAsyncController

    async def get(self, id):
        """
        ---
        description: |
          Get event by id
          Required permission: POLL_EVENT
        tags: [events]
        summary: Get event by id
        parameters:
        - in: path
          name: id
          description: event id
          required: true
        responses:
          200:
            description: Success
            schema:
              type: object
              example:
                id: 59bb70044926aa000174131f
                time: 1502975432
                level: INFO
                evt_class: ORGANIZATION_CREATED
                object_id: 340e6f8b-6f9b-4af5-83c4-317938d6da6e
                object_type: organization
                object_name: My Test organization
                organization_id: d3af8fba-9ef4-46c3-bab0-50835d54daad
                description: Organization My Test organization
                  (d3af8fba-9ef4-46c3-bab0-50835d54daad) created
                ack: true
                acknowledged: 1502975555
                acknowledged_by: 2af23d9fd3fb34693c3a95bbc21afb9f
                acknowledged_user: John Doe (jdoe@email.com)
                resolution: That will do
                read: true
          401:
            description: |
              Unauthorized:
              - OK0003: Unauthorized
              - OK0005: This resource requires authorization
          403:
            description: |
              Forbidden:
              - OK0002: Forbidden
          404:
            description: |
              Not found:
              - OK0004: Event not found
        security:
        - token: []
        """
        try:
            res = await self.controller.get(id, self.token)
        except UnauthorizedException as exc:
            raise OptHTTPError.from_opt_exception(401, exc)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        self.write_json(res)

    async def patch(self, id, **data):
        """
        ---
        description: |
          Acknowledge event by id
          Required permission: ACK_EVENT
        tags: [events]
        summary: Acknowledge event by id
        parameters:
        - in: path
          name: id
          description: event id
          required: true
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              resolution:
                type: string
                required: false
                description: resolution text
        responses:
          200: {description: Success}
          400:
            description: |
              Wrong arguments:
              - OK0018: Event not ACK-able or already ACK-ed
          401:
            description: |
              Unauthorized:
              - OK0003: Unauthorized
              - OK0005: This resource requires authorization
          403:
            description: |
              Forbidden:
              - OK0002: Forbidden
          404:
            description: |
              Not found:
              - OK0004: Event not found
        security:
        - token: []
        """
        data = self._request_body()
        data.update({"token": self.token})
        try:
            res = await self.controller.ack(id, **data)
        except UnauthorizedException as exc:
            raise OptHTTPError.from_opt_exception(401, exc)
        except ForbiddenException as exc:
            raise OptHTTPError.from_opt_exception(403, exc)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        self.write_json(res)
