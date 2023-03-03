import logging
from rest_api_server.controllers.profiling.base import BaseProfilingController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.employee import EmployeeController
from rest_api_server.controllers.profiling.executor import ExecutorController
from rest_api_server.controllers.profiling.run import (
    RunController, RUN_STATUS_COMPLETED)
from optscale_exceptions.common_exc import NotFoundException, ConflictException
from rest_api_server.models.models import Employee
from sqlalchemy.sql import and_
from rest_api_server.exceptions import Err
from requests.exceptions import HTTPError
from datetime import datetime, timedelta


LOG = logging.getLogger(__name__)


class ApplicationController(BaseProfilingController):
    @staticmethod
    def merge_goals(app_goals, kwargs):
        attach = kwargs.pop('attach', [])
        detach = kwargs.pop('detach', [])
        app_goals.update(attach)
        return list(app_goals.difference(detach))

    def get_employee(self, user_id, org_id):
        employee_ctrl = EmployeeController(
            self.session, self._config, self.token)
        return employee_ctrl.get_employee_by_user_and_organization(
            user_id, org_id)

    def get_employee_info(self, employee_id, organization_id):
        return self.session.query(Employee).filter(
            and_(
                Employee.deleted.is_(False),
                Employee.id == employee_id,
                Employee.organization_id == organization_id
            )
        ).one_or_none()

    def formatted_application(self, application, organization_id, token):
        owner_id = application.get('owner_id')
        owner = {}
        if owner_id:
            employee = self.get_employee_info(owner_id, organization_id)
            if employee:
                owner = {'id': employee.id, 'name': employee.name}
        application['owner'] = owner
        status = None
        last_run, last_successful_run, last_run_duration, exec_cnt = 0, 0, 0, 0
        last_run_cost = 0
        last_run_executor = None
        runs = RunController(
            self.session, self._config, self.token
        ).list(organization_id, application['id'], token)
        runs_count = len(runs)
        total_cost = 0
        last_30_days_cost = 0
        last_30_days_start = int(
            (datetime.utcnow() - timedelta(days=30)).timestamp()
        )
        run_goals = {}
        if runs:
            for r in runs:
                run_cost = r.get('cost', 0)
                total_cost += run_cost
                if r['start'] > last_30_days_start:
                    last_30_days_cost += run_cost
                for goal in r.get('goals'):
                    goal_id = goal['id']
                    value = r.get('data', {}).get(goal['key'])
                    if goal_id not in run_goals:
                        run_goals[goal_id] = goal
                        run_goals[goal_id]['history'] = list()
                    if value is not None:
                        run_goals[goal_id]['history'].append(value)
                        run_goals[goal_id]['last_run_value'] = value
            last = sorted(runs, key=lambda d: d['start'])[-1]
            last_run = last['start']
            status = last['status']
            completed_runs = list(filter(
                lambda x: x.get('state') == RUN_STATUS_COMPLETED, runs))
            if completed_runs:
                last_comp = sorted(
                    completed_runs, key=lambda d: d['start'])[-1]
                last_successful_run = last_comp['start']
            if last:
                executor_ids = last.get('executors', [])
                exec_cnt = len(executor_ids)
                if executor_ids:
                    executors = ExecutorController(
                        self.session, self._config, self.token
                    ).list(
                        organization_id, [], token, run_ids=[last['id']]
                    )
                    if executors:
                        last_run_executor = executors[-1]
                last_run_cost = last['cost']
                last_run_duration = last['duration']
        application.update({
            'status': status or 'created',
            'last_run': last_run, 'last_run_duration': last_run_duration,
            'last_successful_run': last_successful_run,
            'runs_count': runs_count,
            'last_run_executor': last_run_executor,
            'executors_count': exec_cnt,
            'last_run_cost': last_run_cost,
            'last_30_days_cost': last_30_days_cost,
            'total_cost': total_cost,
            'run_goals': list(run_goals.values())
        })
        return application

    def get_organization_employees(self, organization_id):
        employees = EmployeeController(
            self.session, self._config, self.token).list(organization_id)
        return {e['id']: {'id': e['id'], 'name': e['name']} for e in employees}

    def create(self, organization_id, profiling_token, **kwargs):
        owner_id = kwargs.get('owner_id')
        if not owner_id:
            auth_user_id = self.get_user_id()
            default_employee = self.get_employee(auth_user_id, organization_id)
            kwargs['owner_id'] = default_employee.id
        else:
            self.validate_owner(owner_id, organization_id)
        application_key = kwargs.pop('key')
        try:
            app = self.create_application(
                profiling_token, application_key=application_key, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(
                    Err.OE0534, [application_key])
            raise
        return self.formatted_application(
            app, organization_id, profiling_token)

    def validate_owner(self, owner_id, organization_id):
        employee = self.get_employee_info(owner_id, organization_id)
        if not employee:
            raise NotFoundException(Err.OE0002, ['Employee', owner_id])

    def get(self, organization_id, application_id, profiling_token):
        try:
            application = self.get_application(profiling_token, application_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Application', application_id])
            raise
        return self.formatted_application(application, organization_id,
                                          profiling_token)

    def list(self, organization_id, profiling_token):
        response = self.list_applications(profiling_token)
        return [self.formatted_application(app, organization_id, profiling_token)
                for app in response]

    def edit(self, organization_id, application_id, profiling_token, **kwargs):
        goals = None
        if 'attach' in kwargs or 'detach' in kwargs:
            app = self.get(organization_id, application_id, profiling_token)
            app_goals = set(map(lambda x: x['id'], app['goals']))
            goals = self.merge_goals(app_goals, kwargs)
        if goals is not None:
            kwargs['goals'] = goals
        owner_id = kwargs.get('owner_id')
        if owner_id is not None:
            self.validate_owner(owner_id, organization_id)
        self.update_application(profiling_token, application_id, **kwargs)
        return self.get(organization_id, application_id, profiling_token)

    def delete(self, application_id, profiling_token):
        try:
            self.delete_application(profiling_token, application_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Application', application_id])
            raise


class ApplicationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ApplicationController
