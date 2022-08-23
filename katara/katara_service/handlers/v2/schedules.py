import json

from optscale_exceptions.http_exc import OptHTTPError
from katara_service.controllers.schedule import ScheduleAsyncController
from katara_service.exceptions import Err
from katara_service.handlers.v2.base import (
    BaseAsyncItemHandler, BaseAsyncCollectionHandler)
from katara_service.utils import ModelEncoder


class ScheduleAsyncItemHandler(BaseAsyncItemHandler):
    def _get_controller_class(self):
        return ScheduleAsyncController

    async def get(self, id):
        """
        ---
        description: >
            Gets schedule with specified ID \n\n
            Required permission: CLUSTER_SECRET
        tags: [schedules]
        summary: Get schedule
        parameters:
        -   name: id
            in: path
            description: Schedule ID
            required: true
            type: string
        responses:
            200:
                description: Schedule data
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique schedule id"}
                        created_at: {type: integer,
                            description: "Created timestamp (service field)"}
                        report_id: {type: string,
                            description: "Report id"}
                        recipient_id: {type: string,
                            description: "Recipient id"}
                        crontab: {type: string,
                            description: "Schedule in crontab format"}
                        last_run: {type: integer,
                            description: "Last job run timestamp (service field)"}
                        next_run: {type: integer,
                            description: "Next job run timestamp (service field)"}
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
                    - OKA0013: Schedule not found
        security:
        - secret: []
        """
        await super().get(id)

    async def patch(self, id, **kwargs):
        """
        ---
        tags: [schedules]
        summary: Edit schedule
        description: >
            Modifies a schedule with specified id \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: id
            in: path
            description: Schedule ID
            required: true
            type: string
        -   in: body
            name: body
            description: Schedule changes
            required: true
            schema:
                type: object
                properties:
                    crontab: {type: string,
                        description: "Schedule in crontab format"}
                    last_run: {type: integer,
                        description: "Schedule last_run"}
                    next_run: {type: integer,
                        description: "Schedule next_run"}
        responses:
            200: {description: Success (returns modified schedule data)}
            400:
                description: |
                    Wrong arguments:
                    - OKA0006: Incorrect crontab
                    - OKA0009: Incorrect request body received
                    - OKA0012: Unexpected parameters
                    - OKA0019: Parameter is immutable
                    - OKA0021: crontab is not provided
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
                    - OKA0013: Schedule not found
        security:
        - secret: []
        """
        await super().patch(id, **kwargs)

    async def delete(self, id, **kwargs):
        """
        ---
        tags: [schedules]
        summary: Delete schedule
        description: >
            Deletes schedule with specified id \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: id
            in: path
            description: Schedule ID
            required: true
            type: string
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
            404:
                description: |
                    Not found:
                    - OKA0013: Schedule not found
        security:
        - secret: []
        """
        await super().delete(id, **kwargs)


class ScheduleAsyncCollectionHandler(BaseAsyncCollectionHandler):
    def _get_controller_class(self):
        return ScheduleAsyncController

    async def post(self, **url_params):
        """
        ---
        tags: [schedules]
        summary: Create schedule
        description: >
            Adds a new schedule \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   in: body
            name: body
            description: Schedule to add
            required: true
            schema:
                type: object
                properties:
                    report_id: {type: string,
                        description: "Report id"}
                    recipient_id: {type: string,
                        description: "Recipient id"}
                    crontab: {type: string,
                        description: "Schedule in crontab format"}
        responses:
            201: {description: Success (returns created schedule data)}
            400:
                description: |
                    Wrong arguments:
                    - OKA0006: Incorrect crontab
                    - OKA0009: Incorrect request body received
                    - OKA0012: Unexpected parameters
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
                    - OKA0004: recipient or report does not exist
            409:
                description: |
                    Conflict:
                    - OKA0005: Report is already scheduled for recipient with rule
        security:
        - secret: []
        """
        await super().post(**url_params)

    async def get(self, **kwargs):
        """
        ---
        tags: [schedules]
        summary: List schedules
        description: >
            Gets a list of schedules \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: recipient_id
            in: path
            description: Schedule recipient id
            required: true
            type: string
        -   name: report_id
            in: path
            description: Schedule report id
            required: false
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        schedules:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Unique schedule id"}
                                    created_at: {type: integer,
                                        description: "Created timestamp (service field)"}
                                    report_id: {type: string,
                                        description: "Report id"}
                                    recipient_id: {type: string,
                                        description: "Recipient id"}
                                    crontab: {type: string,
                                        description: "Schedule in crontab format"}
                                    last_run: {type: integer,
                                        description: "Last job run timestamp (service field)"}
                                    next_run: {type: integer,
                                        description: "Next job run timestamp (service field)"}
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
        recipient_id = self.get_arg('recipient_id', str)
        report_id = self.get_arg('report_id', str)
        if not recipient_id:
            raise OptHTTPError(400, Err.OKA0021, ['recipient_id'])
        params = {'recipient_id': recipient_id}
        if report_id:
            params['report_id'] = report_id
        res = await self.controller.list(**params)
        schedule_dict = {'schedules': [
            schedule.to_dict() for schedule in res]}
        self.write(json.dumps(schedule_dict, cls=ModelEncoder))
