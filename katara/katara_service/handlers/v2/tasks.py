import json

from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException,
    NotFoundException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException
)
from tools.optscale_exceptions.http_exc import OptHTTPError

from katara.katara_service.controllers.task import TaskAsyncController
from katara.katara_service.exceptions import Err
from katara.katara_service.handlers.v2.base import (
    BaseAsyncItemHandler,
    BaseAsyncCollectionHandler
)
from katara.katara_service.utils import (
    strtobool, check_list_attribute, ModelEncoder)


class TaskAsyncItemHandler(BaseAsyncItemHandler):
    def _get_controller_class(self):
        return TaskAsyncController

    async def delete(self, _task_id, **kwargs):
        self.raise405()

    async def get(self, task_id):
        """
        ---
        description: >
            Gets task with specified ID\n\n
            Required permission: CLUSTER_SECRET
        tags: [tasks]
        summary: Get task
        parameters:
        -   name: id
            in: path
            description: Task ID
            required: true
            type: string
        -   name: expanded
            in: query
            description: "Respond task object in simple or expanded format"
            required: false
            type: boolean
        responses:
            200:
                description: Task data
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique task id"}
                        created_at: {type: integer,
                            description: "Created timestamp (service field)"}
                        completed_at: {type: integer,
                            description: "Task completed timestamp"}
                        state: {type: string,
                            description: "Task state"}
                        result: {type: string,
                            description: "Task result (report data)"}
                        schedule_id: {type: string,
                            description: "Schedule id
                             (part of simple response)"}
                        schedule:
                             type: object
                             description: "Task schedule
                              (part of expanded response)"
                             properties:
                                id: {type: string,
                                    description: "Unique schedule id"}
                                created_at: {type: integer,
                                    description: "Created timestamp
                                     (service field)"}
                                crontab: {type: string,
                                    description: "Schedule in crontab format"}
                                last_run: {type: integer,
                                    description: "Last job run timestamp
                                     (service field)"}
                                next_run: {type: integer,
                                    description: "Next job run timestamp
                                     (service field)"}
                                report:
                                    type: object
                                    properties:
                                        id: {type: string,
                                        description: "Unique report id"}
                                        created_at: {type: integer,
                                            description:
                                              "Created timestamp
                                              (service field)"}
                                        name: {type: string,
                                            description: "Report name"}
                                        module_name: {type: string,
                                            description: "Report module name"}
                                        report_format: {type: string,
                                            description: "Report format"}
                                        template: {type: string,
                                            description: "Report template"}
                                        description: {type: string,
                                            description: "Report description"}
                                recipient:
                                    type: object
                                    properties:
                                        id: {type: string,
                                        description: "Unique recipient id"}
                                        created_at: {type: integer,
                                            description: "Created timestamp
                                             (service field)"}
                                        role_purpose: {type: string,
                                            description: "Role purpose of
                                             recipient"}
                                        scope_id: {type: string,
                                            description: "Recipient scope id"}
                                        user_id: {type: string,
                                            description: "Recipient user id"}
                                        meta: {type: string,
                                            description: "Recipient metadata"}
            400:
                description: |
                    Wrong arguments:
                    - OKA0026: Expanded should be false or true
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
                    - OKA0013: Task not found
        security:
        - secret: []
        """
        expanded = self.get_argument('expanded', default='False')
        try:
            expanded = strtobool(expanded)
        except ValueError:
            raise OptHTTPError(400, Err.OKA0026, ['Expanded'])
        item = await self._get_item(task_id)
        self.write(item.to_json(expanded))

    async def patch(self, task_id, **kwargs):
        """
        ---
        tags: [tasks]
        summary: Edit task
        description: >
            Modifies a task with specified id \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: task_id
            in: path
            description: Task ID
            required: true
            type: string
        -   in: body
            name: body
            description: Task changes
            required: true
            schema:
                type: object
                properties:
                    state: {type: string,
                        description: "Task state"}
                    result: {type: string,
                        description: "Task result (report data)"}
        responses:
            200: {description: Success (returns modified task data)}
            400:
                description: |
                    Wrong arguments:
                    - OKA0009: Incorrect request body received
                    - OKA0012: Unexpected parameters
                    - OKA0018: Incorrect result format
                    - OKA0022: Incorrect task state
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
                    - OKA0013: Task not found
        security:
        - secret: []
        """
        await super().patch(task_id, **kwargs)


class TaskAsyncCollectionHandler(BaseAsyncCollectionHandler):
    def _get_controller_class(self):
        return TaskAsyncController

    async def post(self, **url_params):
        """
        ---
        tags: [tasks]
        summary: Create tasks
        description: >
            Adds new tasks \n\n
            Required permission: CLUSTER_SECRET
        parameters:
        -   in: body
            name: body
            description: Tasks to add
            required: true
            schema:
                type: object
                properties:
                    tasks:
                        type: array
                        description: "Tasks payload"
                        items:
                            type: object
                            properties:
                                schedule_id: {type: string,
                                    description: "Schedule id"}
                                state: {type: string,
                                    description: "Task state"}
                                result: {type: string,
                                    description: "Task result (report data)"}
                                parent_id: {type: string,
                                    description: "Parent task id"}
        responses:
            201: {description: Success (returns created tasks data)}
            400:
                description: |
                    Wrong arguments:
                    - OKA0009: Incorrect request body received
                    - OKA0012: Unexpected parameters
                    - OKA0017: Database error
                    - OKA0018: Incorrect result format
                    - OKA0022: Incorrect task state completed
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
                    - OKA0004: Schedule or Task does not exist
        security:
        - secret: []
        """
        data = self._request_body()
        tasks_payload = data.get('tasks')
        try:
            check_list_attribute('tasks', tasks_payload, required=True)
            self._validate_params(**data)
            items = await self.controller.create(tasks_payload)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ConflictException as ex:
            raise OptHTTPError.from_opt_exception(409, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.set_status(201)
        self.write(json.dumps([item.to_dict() for item in items],
                              cls=ModelEncoder))
