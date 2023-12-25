import json
from urllib.parse import urlencode
from optscale_client.rest_api_client.client import Client as Client_v1


class Client(Client_v1):
    def __init__(self, address="127.0.0.1", port="80", api_version="v2",
                 url=None, http_provider=None, token='', secret='',
                 verify=True):
        super().__init__(address=address, port=port, api_version=api_version,
                         url=url, http_provider=http_provider, token=token,
                         secret=secret, verify=verify)

    def get(self, url, body=None):
        if body:
            url = url + self.query_url(**body)
        return self._request(url, "GET")

    @staticmethod
    def query_url(**query):
        query = {
            key: value for key, value in query.items() if value is not None
        }
        encoded_query = urlencode(query, doseq=True)
        return "?" + encoded_query

    def context_get(self, type, uuid):
        url = self.context_url() + self.query_url(
            type=type, uuid=uuid)
        return self.get(url)

    def resources_get(self, payload: list):
        params = {}
        for k, v in payload:
            if params.get(k):
                params[k].append(v)
                continue
            params[k] = [v]
        url = self.resource_url() + self.query_url(**params)
        return self.get(url)

    @staticmethod
    def organization_url(id=None):
        url = 'organizations'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    def organization_create(self, params):
        return self.post(self.organization_url(), params)

    def organization_get(self, org_id, details=False):
        url = self.organization_url(org_id) + self.query_url(details=details)
        return self.get(url)

    def organization_update(self, org_id, params):
        return self.patch(self.organization_url(org_id), params)

    def organization_delete(self, org_id):
        return self.delete(self.organization_url(org_id))

    def organization_list(self, params=None):
        url = self.organization_url()
        if params:
            url += self.query_url(**params)
        return self.get(url)

    @staticmethod
    def cloud_account_url(id=None, org_id=None):
        url = 'cloud_accounts'
        if id is not None:
            url = '%s/%s' % (url, id)
        if org_id is not None:
            url = '%s/%s' % (Client.organization_url(org_id), url)
        return url

    @staticmethod
    def cloud_account_verify_url():
        return 'cloud_account_verify'

    def cloud_account_create(self, org_id, params):
        return self.post(self.cloud_account_url(org_id=org_id), params)

    def cloud_account_get(self, cloud_account_id, details=False):
        url = self.cloud_account_url(cloud_account_id) + self.query_url(
            details=details
        )
        return self.get(url)

    def cloud_account_update(self, cloud_account_id, params):
        return self.patch(self.cloud_account_url(cloud_account_id), params)

    def cloud_account_delete(self, cloud_account_id):
        return self.delete(self.cloud_account_url(cloud_account_id))

    def cloud_account_list(self, org_id, details=False, auto_import=None,
                           type=None, only_linked=None,
                           process_recommendations=None):
        url = self.cloud_account_url(org_id=org_id) + self.query_url(
            details=details, auto_import=auto_import, type=type,
            only_linked=only_linked,
            process_recommendations=process_recommendations
        )
        return self.get(url)

    def cloud_account_verify(self, params):
        return self.post(self.cloud_account_verify_url(), params)

    @staticmethod
    def employee_url(id=None, org_id=None):
        url = 'employees'
        if id is not None:
            url = '%s/%s' % (url, id)
        if org_id is not None:
            url = '%s/%s' % (Client.organization_url(org_id), url)
        return url

    def employee_create(self, org_id, params):
        return self.post(self.employee_url(org_id=org_id), params)

    def employee_get(self, employee_id):
        return self.get(self.employee_url(employee_id))

    def employee_update(self, employee_id, params):
        return self.patch(self.employee_url(employee_id), params)

    def employee_delete(self, employee_id, new_owner_id=None):
        url = self.employee_url(employee_id)
        if new_owner_id:
            url = url + self.query_url(new_owner_id=new_owner_id)
        return self.delete(url)

    def employee_list(self, org_id, current_only=None, roles=False,
                      exclude_myself=False, fields=None):
        query_params = {
            'roles': roles,
            'exclude_myself': exclude_myself
        }
        if current_only:
            query_params['current_only'] = current_only
        if fields:
            query_params['field'] = fields
        return self.get(self.employee_url(org_id=org_id) +
                        self.query_url(**query_params))

    @staticmethod
    def pool_url(id=None):
        url = 'pools'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    def pool_get(self, pool_id, details=False, children=False):
        url = self.pool_url(pool_id) + self.query_url(
            details=details, children=children)
        return self.get(url)

    def pool_update(self, pool_id, params):
        return self.patch(self.pool_url(pool_id), params)

    def pool_delete(self, pool_id):
        return self.delete(self.pool_url(pool_id))

    def cloud_resource_discovery_url(self, organization_id):
        return self.organization_url(organization_id) + "/cloud_resources"

    @staticmethod
    def cloud_resource_url(id=None, cloud_account_id=None):
        url = 'cloud_resources'
        if id is not None:
            url = '%s/%s' % (url, id)
        if cloud_account_id is not None:
            url = '%s/%s' % (Client.cloud_account_url(
                cloud_account_id), url)
        return url

    @staticmethod
    def cloud_resource_bulk_url(cloud_account_id):
        return '%s/cloud_resources/bulk' % Client.cloud_account_url(
            cloud_account_id)

    def cloud_resource_create(self, cloud_account_id, params):
        return self.post(self.cloud_resource_url(
            cloud_account_id=cloud_account_id), params)

    def cloud_resource_create_bulk(self, cloud_account_id, params,
                                   behavior='error_existing',
                                   return_resources=False,
                                   is_report_import=False):
        url = self.cloud_resource_bulk_url(cloud_account_id)
        url += self.query_url(behavior=behavior,
                              return_resources=return_resources,
                              is_report_import=is_report_import)
        return self.post(url, params)

    def cloud_resource_get(self, cloud_resource_id, details=False):
        url = self.cloud_resource_url(
            cloud_resource_id) + self.query_url(details=details)
        return self.get(url)

    def cloud_resource_update(self, cloud_resource_id, params):
        return self.patch(self.cloud_resource_url(cloud_resource_id), params)

    def cloud_resource_delete(self, cloud_resource_id):
        return self.delete(self.cloud_resource_url(cloud_resource_id))

    def cloud_resource_list(self, cloud_account_id, cloud_resource_id=None):
        url = self.cloud_resource_url(cloud_account_id=cloud_account_id)
        query_params = {}
        if cloud_resource_id:
            query_params['cloud_resource_id'] = cloud_resource_id
        if query_params:
            url += self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def report_upload_url(cloud_acc_id):
        return '%s/report_upload' % Client.cloud_account_url(cloud_acc_id)

    def report_upload(self, cloud_account_id, file_path):
        with open(file_path, 'rb') as f:
            return self._http_provider.request(
                path=self._url(self.report_upload_url(cloud_account_id)),
                method='POST',
                data=f)

    @staticmethod
    def schedule_import_url():
        return 'schedule_imports'

    def schedule_import(self, period=None, cloud_account_id=None, organization_id=None,
                        cloud_account_type=None, priority=None):
        body = {
            'period': period,
            'cloud_account_id': cloud_account_id,
            'organization_id': organization_id,
            'cloud_account_type': cloud_account_type,
            'priority': priority
        }
        return self.post(self.schedule_import_url(), body)

    @staticmethod
    def report_import_url(id=None, cloud_account_id=None):
        url = 'report_imports'
        if id is not None:
            url = '%s/%s' % (url, id)
        if cloud_account_id is not None:
            url = '%s/%s' % (Client.cloud_account_url(
                cloud_account_id), url)
        return url

    def report_import_get(self, report_import_id):
        return self.get(self.report_import_url(report_import_id))

    def report_import_update(self, report_import_id, params):
        return self.patch(self.report_import_url(report_import_id), params)

    def report_import_list(self, cloud_account_id, show_completed=False,
                           show_active=False):
        return self.get(self.report_import_url(
            cloud_account_id=cloud_account_id) + self.query_url(
            show_completed=show_completed, show_active=show_active))

    @staticmethod
    def invite_url(id=None):
        url = 'invites'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    def invite_create(self, params):
        return self.post(self.invite_url(), params)

    def invite_list(self):
        return self.get(self.invite_url())

    def invite_accept(self, invite_id):
        return self.patch(self.invite_url(invite_id), {'action': 'accept'})

    def invite_decline(self, invite_id):
        return self.patch(self.invite_url(invite_id), {'action': 'decline'})

    def invite_get(self, invite_id):
        return self.get(self.invite_url(invite_id))

    @staticmethod
    def pool_breakdown_expenses_url(pool_id):
        return 'pools_expenses/%s' % pool_id

    def pool_breakdown_expenses_get(self, pool_id, start_date, end_date,
                                    filter_by=None):
        url = self.pool_breakdown_expenses_url(pool_id)
        query_params = {
            'start_date': start_date,
            'end_date': end_date,
        }
        if filter_by is not None:
            query_params['filter_by'] = filter_by
        return self.get(url + self.query_url(**query_params))

    @staticmethod
    def cloud_expenses_url(cloud_acc_id):
        return 'clouds_expenses/%s' % cloud_acc_id

    def cloud_expenses_get(self, cloud_acc_id, start_date, end_date,
                           filter_by=None):
        url = self.cloud_expenses_url(cloud_acc_id)
        query_params = {
            'start_date': start_date,
            'end_date': end_date,
        }
        if filter_by is not None:
            query_params['filter_by'] = filter_by
        return self.get(url + self.query_url(**query_params))

    @staticmethod
    def employee_expenses_url(employee_id):
        return 'employees_expenses/%s' % employee_id

    def employee_expenses_get(self, employee_id, start_date, end_date,
                              filter_by=None):
        url = self.employee_expenses_url(employee_id)
        query_params = {
            'start_date': start_date,
            'end_date': end_date,
        }
        if filter_by is not None:
            query_params['filter_by'] = filter_by
        return self.get(url + self.query_url(**query_params))

    @staticmethod
    def assignment_url(organization_id):
        url = 'organizations/%s/assignments' % organization_id
        return url

    def assignment_create(self, organization_id, params):
        return self.post(self.assignment_url(
            organization_id=organization_id), params)

    def assignment_list(self, organization_id):
        return self.get(self.assignment_url(
            organization_id=organization_id))

    @staticmethod
    def assignment_requests_url(organization_id):
        url = 'organizations/%s/assignment_requests' % organization_id
        return url

    @staticmethod
    def assignment_request_url(id):
        url = 'assignment_requests/%s' % id
        return url

    def assignment_request_create(self, organization_id, params):
        return self.post(self.assignment_requests_url(
            organization_id=organization_id), params)

    def assignment_request_list(self, organization_id, req_type=None):
        url = self.assignment_requests_url(organization_id=organization_id)
        if req_type:
            url += self.query_url(type=req_type)
        return self.get(url)

    def assignment_request_patch(self, id, params):
        return self.patch(self.assignment_request_url(id=id), params)

    def assignment_request_accept(self, id, params):
        params.update({'action': 'accept'})
        return self.patch(self.assignment_request_url(id=id), params)

    def assignment_request_decline(self, id):
        return self.patch(self.assignment_request_url(id=id),
                          {'action': 'decline'})

    def assignment_request_cancel(self, id):
        return self.patch(self.assignment_request_url(id=id),
                          {'action': 'cancel'})

    def cloud_resources_discover(self, organization_id, resource_type,
                                 filters=None, sort=None, cached=True,
                                 cloud_type=None):
        url = self.cloud_resource_discovery_url(organization_id)
        if filters:
            filters = json.dumps(filters)
        if sort:
            sort = json.dumps(sort)
        query_params = {
            'type': resource_type,
            'filters': filters,
            'sort': sort,
            'cached': cached,
            'cloud_type': cloud_type,
        }
        return self.get(url + self.query_url(**query_params))

    @staticmethod
    def alerts_url(organization_id=None, id=None):
        url = 'alerts'
        if id is not None:
            url = '%s/%s' % (url, id)
        if organization_id is not None:
            url = '%s/%s' % (Client.organization_url(organization_id), url)
        return url

    @staticmethod
    def alerts_process_url(organization_id):
        return '%s/process_alerts' % Client.organization_url(organization_id)

    def alert_process(self, organization_id):
        return self.post(self.alerts_process_url(organization_id), None)

    def alert_create(self, organization_id, params):
        return self.post(self.alerts_url(organization_id), params)

    def alert_list(self, organization_id):
        return self.get(self.alerts_url(organization_id))

    def alert_get(self, alert_id):
        return self.get(self.alerts_url(id=alert_id))

    def alert_update(self, alert_id, params):
        return self.patch(self.alerts_url(id=alert_id), params)

    def alert_delete(self, alert_id):
        return self.delete(self.alerts_url(id=alert_id))

    @staticmethod
    def split_resources_request_url(organization_id):
        url = 'organizations/%s/split_resources/assign' % organization_id
        return url

    def split_resources(self, organization_id, resource_ids):
        return self.post(self.split_resources_request_url(
            organization_id=organization_id), resource_ids)

    @staticmethod
    def my_tasks_url(org_id):
        return '%s/my_tasks' % Client.organization_url(org_id)

    def my_tasks_get(self, org_id, types=None, **kwargs):
        url = self.my_tasks_url(org_id)
        query_params = kwargs
        if types is not None:
            query_params['type'] = types
        if query_params:
            url += self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def assignment_bulk_url(organization_id):
        url = 'organizations/%s/assignments/bulk' % organization_id
        return url

    def assignment_bulk(self, organization_id, params):
        return self.post(self.assignment_bulk_url(
            organization_id=organization_id), params)

    @staticmethod
    def assignment_request_bulk_url(organization_id):
        url = 'organizations/%s/assignment_requests/bulk' % organization_id
        return url

    def assignment_request_bulk(self, organization_id, params):
        return self.post(self.assignment_request_bulk_url(
            organization_id=organization_id), params)

    @staticmethod
    def pools_url(organization_id):
        url = 'organizations/%s/pools' % organization_id
        return url

    def pool_create(self, org_id, params):
        return self.post(self.pools_url(org_id), params)

    def pools_get(self, organization_id, permission=None, condition=None):
        url = self.pools_url(organization_id=organization_id)
        query_params = {
            'permission': permission,
            'condition': condition,
        }
        url += self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def raw_expenses_url(resource_id):
        return 'resources/%s/raw_expenses' % resource_id

    def raw_expenses_get(self, resource_id, start_date, end_date,
                         params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if params:
            query_params.update(params)
        url = self.raw_expenses_url(
            resource_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def pool_employees_url(pool_id):
        url = 'pools/%s/employees' % pool_id
        return url

    def pool_employees_get(self, pool_id, exclude_myself=False):
        url = self.pool_employees_url(pool_id=pool_id)
        if exclude_myself:
            url += self.query_url(exclude_myself=exclude_myself)
        return self.get(url)

    def bulk_call_aws_url(self, cloud_account_id):
        return '{}/bulk_call_aws'.format(self.cloud_account_url(
            cloud_account_id))

    def bulk_call_aws(self, cloud_account_id, params):
        return self.post(self.bulk_call_aws_url(cloud_account_id), params)

    @staticmethod
    def pool_expenses_url(organization_id):
        return 'organizations/%s/pool_expenses' % organization_id

    def pool_expenses_get(self, organization_id):
        url = self.pool_expenses_url(organization_id)
        return self.get(url)

    @staticmethod
    def clean_expenses_url(organization_id):
        return '%s/clean_expenses' % Client.organization_url(organization_id)

    def clean_expenses_get(self, organization_id, start_date, end_date,
                           params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if params:
            query_params.update(params)
        url = self.clean_expenses_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def summary_expenses_url(organization_id):
        return '%s/summary_expenses' % Client.organization_url(organization_id)

    def summary_expenses_get(self, organization_id, start_date, end_date,
                             params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if params:
            query_params.update(params)
        url = self.summary_expenses_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def rules_url(organization_id):
        return '%s/rules' % Client.organization_url(organization_id)

    def rules_list(self, organization_id, pool_id=None,
                   owner_id=None, valid_rules_only=None):
        url = self.rules_url(organization_id)
        query_params = {
            'pool_id': pool_id,
            'owner_id': owner_id,
            'valid_rules_only': valid_rules_only
        }
        return self.get(url + self.query_url(**query_params))

    def rules_create(self, organization_id, params):
        url = self.rules_url(organization_id)
        return self.post(url, params)

    @staticmethod
    def rule_url(rule_id):
        url = 'rules/%s' % rule_id
        return url

    @staticmethod
    def rule_priority_url(rule_id):
        url = 'rules/%s/priority' % rule_id
        return url

    def rule_get(self, rule_id):
        return self.get(self.rule_url(rule_id))

    def rule_update(self, rule_id, params):
        return self.patch(self.rule_url(rule_id), params)

    def rule_delete(self, rule_id):
        return self.delete(self.rule_url(rule_id))

    def rule_priority_update(self, rule_id, action):
        return self.patch(self.rule_priority_url(rule_id), {'action': action})

    def rule_prioritize(self, rule_id):
        return self.rule_priority_update(rule_id, 'prioritize')

    def rule_promote(self, rule_id):
        return self.rule_priority_update(rule_id, 'promote')

    def rule_demote(self, rule_id):
        return self.rule_priority_update(rule_id, 'demote')

    def rule_deprioritize(self, rule_id):
        return self.rule_priority_update(rule_id, 'deprioritize')

    @staticmethod
    def pool_policy_url(pool_id=None, policy_id=None):
        url = 'policies'
        if policy_id is not None:
            url = '%s/%s' % (url, policy_id)
        if pool_id is not None:
            url = '%s/%s' % (Client.pool_url(pool_id), url)
        return url

    def pool_policy_create(self, pool_id, params):
        url = self.pool_policy_url(pool_id)
        return self.post(url, params)

    def pool_policy_list(self, pool_id):
        url = self.pool_policy_url(pool_id)
        return self.get(url)

    def resource_policies_list(self, organization_id, details=False):
        url = '%s/%s' % (Client.organization_url(organization_id),
                         'resource_policies') + self.query_url(details=details)
        return self.get(url)

    def resource_constraints_list(self, organization_id, details=False):
        url = '%s/%s' % (
            Client.organization_url(organization_id),
            'resource_constraints') + self.query_url(details=details)
        return self.get(url)

    def pool_policy_get(self, policy_id):
        url = self.pool_policy_url(policy_id=policy_id)
        return self.get(url)

    def pool_policy_update(self, policy_id, params):
        return self.patch(self.pool_policy_url(policy_id=policy_id), params)

    def pool_policy_delete(self, policy_id):
        return self.delete(self.pool_policy_url(policy_id=policy_id))

    @staticmethod
    def resource_limit_hits_url(resource_id):
        return 'cloud_resources/%s/limit_hits' % resource_id

    def resource_limit_hits_list(self, resource_id):
        return self.get(self.resource_limit_hits_url(
            resource_id=resource_id))

    def pool_limit_hits_url(self, pool_id):
        return 'pools/%s/limit_hits' % pool_id

    def pool_limit_hits_list(self, pool_id):
        return self.get(self.pool_limit_hits_url(pool_id=pool_id))

    @staticmethod
    def resource_constraint_url(resource_id=None, constraint_id=None):
        url = 'constraints'
        if constraint_id is not None:
            url = '%s/%s' % (url, constraint_id)
        if resource_id is not None:
            url = '%s/%s' % ('cloud_resources/%s' % resource_id, url)
        return url

    def resource_constraint_create(self, resource_id, params):
        url = self.resource_constraint_url(resource_id)
        return self.post(url, params)

    def resource_constraint_list(self, resource_id):
        url = self.resource_constraint_url(resource_id)
        return self.get(url)

    def resource_constraint_get(self, constraint_id):
        url = self.resource_constraint_url(constraint_id=constraint_id)
        return self.get(url)

    def resource_constraint_update(self, constraint_id, params):
        return self.patch(
            self.resource_constraint_url(constraint_id=constraint_id), params)

    def resource_constraint_delete(self, constraint_id):
        return self.delete(self.resource_constraint_url(
            constraint_id=constraint_id))

    @staticmethod
    def region_expenses_url(organization_id):
        return 'organizations/%s/region_expenses' % organization_id

    def region_expenses_get(self, organization_id, start_date, end_date):
        url = self.region_expenses_url(organization_id)
        query_params = {
            'start_date': start_date,
            'end_date': end_date,
        }
        return self.get(url + self.query_url(**query_params))

    @staticmethod
    def checklist_url(checklist_id=None):
        url = 'checklists'
        if checklist_id is not None:
            url = '%s/%s' % (url, checklist_id)
        return url

    def checklist_list(self):
        url = self.checklist_url()
        return self.get(url)

    def checklist_update(self, checklist_id, params):
        return self.patch(
            self.checklist_url(checklist_id=checklist_id), params)

    @staticmethod
    def optimizations_url(organization_id):
        return '%s/optimizations' % Client.organization_url(organization_id)

    def optimizations_get(self, organization_id, types=None, limit=None,
                          status=None, cloud_account_ids=None, overview=None):
        url = self.optimizations_url(organization_id)
        query_params = {}
        if types is not None:
            query_params['type'] = types
        if cloud_account_ids is not None:
            query_params['cloud_account_id'] = cloud_account_ids
        if limit is not None:
            query_params['limit'] = limit
        if status is not None:
            query_params['status'] = status
        if overview is not None:
            query_params['overview'] = overview
        if query_params:
            url += self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def optimization_data_url(organization_id):
        return '%s/optimization_data' % Client.organization_url(
            organization_id)

    def optimization_data_get(self, organization_id, type=None, status=None,
                              cloud_account_ids=None, limit=None):
        url = self.optimization_data_url(organization_id)
        query_params = {}
        if type is not None:
            query_params['type'] = type
        if cloud_account_ids is not None:
            query_params['cloud_account_id'] = cloud_account_ids
        if status is not None:
            query_params['status'] = status
        if limit is not None:
            query_params['limit'] = limit
        if query_params:
            url += self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def live_demo_url():
        return 'live_demo'

    def live_demo_create(self, params=None):
        url = self.live_demo_url()
        return self.post(url, params or {})

    def live_demo_get(self):
        url = self.live_demo_url()
        return self.get(url, {})

    @staticmethod
    def observe_resources_url(organization_id):
        return '%s/resource_observer' % Client.organization_url(organization_id)

    def observe_resources(self, organization_id):
        url = self.observe_resources_url(organization_id)
        return self.post(url, {})

    @staticmethod
    def discovery_info_url(discovery_info_id=None, cloud_account_id=None):
        url = 'discovery_info'
        if discovery_info_id is not None:
            url = '%s/%s' % (url, discovery_info_id)
        if cloud_account_id is not None:
            url = '%s/%s' % (Client.cloud_account_url(
                id=cloud_account_id), url)
        return url

    def discovery_info_list(self, cloud_account_id, resource_type=None):
        url = self.discovery_info_url(cloud_account_id=cloud_account_id)
        query_params = {}
        if resource_type is not None:
            query_params['resource_type'] = resource_type
        if query_params:
            url += self.query_url(**query_params)
        return self.get(url)

    def discovery_info_update(self, discovery_info_id, params):
        return self.patch(self.discovery_info_url(
            discovery_info_id=discovery_info_id), params)

    def discovery_info_bulk_url(self, cloud_account_id):
        return '%s/bulk' % self.discovery_info_url(
            cloud_account_id=cloud_account_id)

    def discovery_info_create_bulk(self, cloud_account_id, params):
        url = self.discovery_info_bulk_url(cloud_account_id=cloud_account_id)
        return self.post(url, params)

    def discovery_info_delete_bulk(self, cloud_account_id, discovery_info_ids):
        body = {'discovery_info': discovery_info_ids}
        return self.delete(self.discovery_info_bulk_url(
            cloud_account_id=cloud_account_id), body)

    def discovery_info_switch_enable_url(self, cloud_account_id):
        return '%s/%s' % (Client.cloud_account_url(
            id=cloud_account_id), 'switch_enable')

    def discovery_info_switch_enable(self, cloud_account_id, resource_type,
                                     enabled):
        return self.patch(self.discovery_info_switch_enable_url(
            cloud_account_id=cloud_account_id),
            {'resource_type': resource_type, 'enabled': enabled})

    @staticmethod
    def cleanup_scripts_url(cloud_account_id, module_name):
        return '%s/cleanup_%s.sh' % (Client.cloud_account_url(cloud_account_id),
                                     module_name)

    def get_cleanup_script(self, cloud_account_id, module_name):
        return self.get(self.cleanup_scripts_url(cloud_account_id, module_name))

    @staticmethod
    def ttl_analysis_url(pool_id):
        return '%s/ttl_analysis' % Client.pool_url(pool_id)

    def ttl_analysis_get(self, pool_id, start_date, end_date=None, ttl=None):
        url = self.ttl_analysis_url(pool_id)
        query_params = {
            'start_date': start_date,
            'end_date': end_date,
            'ttl': ttl,
        }
        url += self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def rules_apply_url(organization_id):
        return '%s/rules_apply' % Client.organization_url(id=organization_id)

    def rules_apply(self, organization_id, pool_id=None,
                    include_children=None):
        body = {
            'pool_id': pool_id,
            'include_children': include_children,
        }
        return self.post(self.rules_apply_url(organization_id), body)

    @staticmethod
    def resource_optimization_url(resource_id):
        return 'resources/%s/optimizations' % resource_id

    def resource_optimization_update(
            self, resource_id, recommendation, action):
        return self.patch(self.resource_optimization_url(resource_id),
                          {'action': action, 'recommendation': recommendation})

    def resource_optimization_dismiss(self, resource_id, recommendation):
        return self.resource_optimization_update(
            resource_id, recommendation, 'dismiss')

    def resource_optimization_activate(self, resource_id, recommendation):
        return self.resource_optimization_update(
            resource_id, recommendation, 'activate')

    @staticmethod
    def organizations_overview_url():
        return 'organizations_overview'

    def organizations_overview_list(self, details=False):
        url = self.organizations_overview_url() + self.query_url(
            details=details)
        return self.get(url)

    @staticmethod
    def organization_options_url(org_id, option_name=None):
        url = '%s/options' % Client.organization_url(org_id)
        if option_name is not None:
            url = '%s/%s' % (url, option_name)
        return url

    def organization_options_list(self, org_id, with_values=False):
        url = self.organization_options_url(org_id) + self.query_url(
            with_values=with_values)
        return self.get(url)

    def organization_option_get(self, org_id, option_name):
        url = self.organization_options_url(org_id, option_name)
        return self.get(url)

    def organization_option_update(self, org_id, option_name, value):
        url = self.organization_options_url(org_id, option_name)
        return self.patch(url, value)

    def organization_option_create(self, org_id, option_name, value):
        return self.organization_option_update(org_id, option_name, value)

    def organization_option_delete(self, org_id, option_name):
        url = self.organization_options_url(org_id, option_name)
        return self.delete(url)

    @staticmethod
    def cluster_type_url(cluster_type_id=None, organization_id=None):
        url = 'cluster_types'
        if cluster_type_id is not None:
            url = '%s/%s' % (url, cluster_type_id)
        if organization_id is not None:
            url = '%s/%s' % (Client.organization_url(organization_id), url)
        return url

    @staticmethod
    def cluster_type_priority_url(cluster_type_id):
        url = '%s/priority' % Client.cluster_type_url(cluster_type_id)
        return url

    def cluster_type_list(self, organization_id):
        url = self.cluster_type_url(organization_id=organization_id)
        return self.get(url)

    def cluster_type_create(self, organization_id, params):
        url = self.cluster_type_url(organization_id=organization_id)
        return self.post(url, params)

    def cluster_type_delete(self, cluster_type_id):
        return self.delete(self.cluster_type_url(cluster_type_id=cluster_type_id))

    def cluster_type_priority_update(self, cluster_type_id, action):
        return self.patch(self.cluster_type_priority_url(cluster_type_id),
                          {'action': action})

    def cluster_type_prioritize(self, cluster_type_id):
        return self.cluster_type_priority_update(cluster_type_id, 'prioritize')

    def cluster_type_promote(self, cluster_type_id):
        return self.cluster_type_priority_update(cluster_type_id, 'promote')

    def cluster_type_demote(self, cluster_type_id):
        return self.cluster_type_priority_update(cluster_type_id, 'demote')

    def cluster_type_deprioritize(self, cluster_type_id):
        return self.cluster_type_priority_update(
            cluster_type_id, 'deprioritize')

    @staticmethod
    def cluster_types_apply_url(organization_id):
        return '%s/cluster_types_apply' % Client.organization_url(id=organization_id)

    def cluster_types_apply(self, organization_id):
        return self.post(self.cluster_types_apply_url(organization_id), {})

    @staticmethod
    def pool_expenses_export_url(pool_id):
        return '%s/expenses_export' % Client.pool_url(pool_id)

    def pool_expenses_export_create(self, pool_id):
        return self.post(self.pool_expenses_export_url(pool_id), {})

    @staticmethod
    def pool_expenses_export_data_url(export_id):
        url = 'pool_expenses_exports'
        if export_id is not None:
            url = '%s/%s' % (url, export_id)
        return url

    def pool_expenses_export_data_get(
            self, export_id, start_date=None, end_date=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        url = self.pool_expenses_export_data_url(
            export_id) + self.query_url(**query_params)
        return self.get(url)

    def pool_expenses_export_delete(self, pool_id):
        return self.delete(self.pool_expenses_export_url(pool_id))

    @staticmethod
    def node_bulk_url(cloud_account_id):
        url = 'cloud_accounts/%s/nodes/bulk' % cloud_account_id
        return url

    def node_create_bulk(self, cloud_account_id, params):
        return self.post(self.node_bulk_url(
            cloud_account_id=cloud_account_id), params)

    @staticmethod
    def node_url(cloud_account_id):
        url = 'cloud_accounts/%s/nodes' % cloud_account_id
        return url

    def node_list(self, cloud_account_id):
        return self.get(self.node_url(cloud_account_id=cloud_account_id))

    @staticmethod
    def metric_url(resource_id):
        url = 'cloud_resources/%s/metrics' % resource_id
        return url

    @staticmethod
    def k8s_rightsizing_url(organization_id):
        url = 'organizations/%s/k8s_rightsizing' % organization_id
        return url

    def resource_metrics_get(self, resource_id, query_params):
        url = self.metric_url(
            resource_id=resource_id) + self.query_url(**query_params)
        return self.get(url)

    def k8s_rightsizing_get(self, organization_id, query_params):
        url = self.k8s_rightsizing_url(
            organization_id=organization_id) + self.query_url(**query_params)
        return self.get(url)

    def cost_model_url(self, organization_id):
        url = self.organization_url(organization_id) + "/cost_models"
        return url

    def cost_model_list(self, organization_id):
        return self.get(self.cost_model_url(organization_id=organization_id))

    @staticmethod
    def cloud_account_cost_model_url(cost_model_id=None):
        url = 'cloud_account_cost_models'
        if cost_model_id is not None:
            url = '%s/%s' % (url, cost_model_id)
        return url

    def cloud_account_cost_model_update(self, cost_model_id, params):
        return self.patch(self.cloud_account_cost_model_url(
            cost_model_id), params)

    def cloud_account_cost_model_get(self, cost_model_id):
        return self.get(self.cloud_account_cost_model_url(cost_model_id))

    @staticmethod
    def resource_cost_model_url(cost_model_id=None):
        url = 'resource_cost_models'
        if cost_model_id is not None:
            url = '%s/%s' % (url, cost_model_id)
        return url

    def resource_cost_model_update(self, cost_model_id, params):
        return self.patch(self.resource_cost_model_url(
            cost_model_id), params)

    def resource_cost_model_get(self, cost_model_id):
        return self.get(self.resource_cost_model_url(cost_model_id))

    @staticmethod
    def sku_cost_model_url(cost_model_id=None):
        url = 'sku_cost_models'
        if cost_model_id is not None:
            url = '%s/%s' % (url, cost_model_id)
        return url

    def sku_cost_model_update(self, cost_model_id, params):
        return self.patch(self.sku_cost_model_url(
            cost_model_id), params)

    def sku_cost_model_get(self, cost_model_id, details=False):
        return self.get(self.sku_cost_model_url(
            cost_model_id) + self.query_url(details=details))

    @staticmethod
    def resource_violations_url(organization_id):
        return '%s/resource_violations' % Client.organization_url(organization_id)

    def process_resource_violations(self, organization_id):
        url = self.resource_violations_url(organization_id)
        return self.post(url, {})

    @staticmethod
    def environment_resource_url(id=None, organization_id=None):
        url = 'environment_resources'
        if id is not None:
            url = '%s/%s' % (url, id)
        if organization_id is not None:
            url = '%s/%s' % (Client.organization_url(organization_id), url)
        return url

    def environment_resource_create(self, organization_id, params):
        return self.post(self.environment_resource_url(
            organization_id=organization_id), params)

    def environment_resource_get(self, environment_resource_id,
                                 details=False):
        url = self.environment_resource_url(
            environment_resource_id) + self.query_url(details=details)
        return self.get(url)

    def environment_resource_update(self, environment_resource_id, params):
        return self.patch(self.environment_resource_url(
            environment_resource_id), params)

    def environment_resource_delete(self, environment_resource_id):
        return self.delete(self.environment_resource_url(
            environment_resource_id))

    def environment_resource_list(self, organization_id, params=None):
        url = self.environment_resource_url(organization_id=organization_id)
        if params:
            url += self.query_url(**params)
        return self.get(url)

    @staticmethod
    def shareable_book_collection_url(organization_id):
        url = 'organizations/%s/shareable_book' % organization_id
        return url

    def shareable_book_create(self, organization_id, params):
        return self.post(self.shareable_book_collection_url(
            organization_id=organization_id), params)

    def shareable_book_list(self, organization_id, start_date, end_date=None):
        query_params = {'start_date': start_date}
        if end_date:
            query_params['end_date'] = end_date
        url = self.shareable_book_collection_url(
            organization_id=organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def shareable_book_item_url(item_id):
        url = 'shareable/%s' % item_id
        return url

    def shareable_book_get(self, item_id):
        return self.get(self.shareable_book_item_url(
            item_id=item_id))

    def shareable_book_release(self, item_id, params):
        return self.patch(self.shareable_book_item_url(
            item_id=item_id), params)

    def shareable_book_delete(self, item_id):
        return self.delete(self.shareable_book_item_url(
            item_id=item_id))

    @staticmethod
    def shareable_resources_list_url(organization_id):
        url = 'organizations/%s/shareable_resources' % organization_id
        return url

    def shareable_resources_list(self, organization_id, params=None):
        url = self.shareable_resources_list_url(
            organization_id=organization_id)
        if params:
            url += self.query_url(**params)
        return self.get(url)

    @staticmethod
    def shareable_bulk_url(organization_id):
        url = 'organizations/%s/shareable/bulk' % organization_id
        return url

    def resources_bulk_share(self, organization_id, resource_ids):
        body = {'resource_ids': resource_ids}
        return self.post(self.shareable_bulk_url(organization_id), body)

    @staticmethod
    def shareable_split_url(organization_id):
        url = 'organizations/%s/shareable_split' % organization_id
        return url

    def shareable_resources_get(self, organization_id, resource_ids):
        body = {'resource_ids': resource_ids}
        return self.post(self.shareable_split_url(organization_id), body)

    def resource_bookings_get_url(self, resource_id):
        url = 'shareable/%s/bookings' % resource_id
        return url

    def resource_bookings_get(self, resource_id):
        return self.get(self.resource_bookings_get_url(resource_id))

    def env_properties_script_url(self, cloud_resource_id):
        url = '%s/env_properties_script'
        return url % self.cloud_resource_url(id=cloud_resource_id)

    def env_properties_script_get(self, cloud_resource_id):
        return self.get(self.env_properties_script_url(cloud_resource_id))

    def env_properties_collector_url(self, cloud_resource_id):
        url = '%s/env_properties_collector'
        return url % self.cloud_resource_url(id=cloud_resource_id)

    def env_properties_send(self, cloud_resource_id, properties):
        return self.post(self.env_properties_collector_url(cloud_resource_id),
                         body=properties)

    def env_properties_history_url(self, cloud_resource_id):
        url = '%s/env_properties_history'
        return url % self.cloud_resource_url(id=cloud_resource_id)

    def env_properties_history_get(self, cloud_resource_id, start_date=None,
                                   end_date=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        url = self.env_properties_history_url(
            cloud_resource_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def calendar_synchronizations_url(id=None):
        url = 'calendar_synchronizations'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    def calendar_synchronization_create(self, params):
        return self.post(self.calendar_synchronizations_url(), params)

    def calendar_synchronization_list(self):
        return self.get(self.calendar_synchronizations_url())

    def calendar_synchronization_update(self, calendar_synchronization_id,
                                        params):
        return self.patch(self.calendar_synchronizations_url(
            calendar_synchronization_id), params)

    def calendar_synchronization_delete(self, calendar_synchronization_id):
        return self.delete(self.calendar_synchronizations_url(
            calendar_synchronization_id))

    @staticmethod
    def organization_calendars_url(organization_id):
        return 'organization_calendars/%s' % organization_id

    def organization_calendar_get(self, organization_id):
        return self.get(self.organization_calendars_url(organization_id))

    @staticmethod
    def observe_calendars_url(organization_id):
        return '%s/calendar_observer' % Client.organization_url(organization_id)

    def observe_calendar(self, organization_id):
        url = self.observe_calendars_url(organization_id)
        return self.post(url, {})

    @staticmethod
    def webhooks_url(id=None, org_id=None):
        url = 'webhooks'
        if id is not None:
            url = '%s/%s' % (url, id)
        if org_id is not None:
            url = '%s/%s' % (Client.organization_url(org_id), url)
        return url

    def webhook_create(self, org_id, params):
        return self.post(self.webhooks_url(org_id=org_id), params)

    def webhook_get(self, webhook_id):
        return self.get(self.webhooks_url(webhook_id))

    def webhook_update(self, webhook_id, params):
        return self.patch(self.webhooks_url(webhook_id), params)

    def webhook_delete(self, webhook_id):
        return self.delete(self.webhooks_url(webhook_id))

    def webhook_list(self, org_id, params=None):
        url = self.webhooks_url(org_id=org_id)
        if params:
            url += self.query_url(**params)
        return self.get(url)

    @staticmethod
    def webhook_logs_url(webhook_id):
        return '%s/logs' % Client.webhooks_url(webhook_id)

    def webhook_logs_get(self, webhook_id, format=None):
        return self.get(
            self.webhook_logs_url(webhook_id) + self.query_url(format=format))

    @staticmethod
    def authorized_employees_url(organization_id):
        return '%s/authorized_employees' % Client.organization_url(
            organization_id)

    def authorized_employee_list(self, organization_id, object_type, object_id,
                                 permissions):
        query_params = {
            'object_type': object_type,
            'object_id': object_id,
            'permission': permissions
        }
        url = self.authorized_employees_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def code_report_upload_url(organization_id):
        return '%s/code_report_upload' % Client.organization_url(
            organization_id)

    def code_report_upload(self, organization_id, file_path):
        with open(file_path, 'rb') as f:
            return self._http_provider.request(
                path=self._url(self.code_report_upload_url(organization_id)),
                method='POST',
                data=f)

    @staticmethod
    def submit_for_audit_url(organization_id):
        return '%s/submit_for_audit' % Client.organization_url(
            organization_id)

    def submit_for_audit(self, organization_id):
        return self.post(self.submit_for_audit_url(organization_id), {})

    @staticmethod
    def ssh_keys_url(id=None, employee_id=None):
        url = 'ssh_keys'
        if id is not None:
            url = '%s/%s' % (url, id)
        if employee_id is not None:
            url = '%s/%s' % (Client.employee_url(employee_id), url)
        return url

    def ssh_key_create(self, employee_id, params):
        return self.post(self.ssh_keys_url(employee_id=employee_id), params)

    def ssh_key_list(self, employee_id):
        return self.get(self.ssh_keys_url(employee_id=employee_id))

    def ssh_key_get(self, ssh_key_id):
        return self.get(self.ssh_keys_url(ssh_key_id))

    def ssh_key_update(self, ssh_key_id, params):
        return self.patch(self.ssh_keys_url(ssh_key_id), params)

    def ssh_key_delete(self, ssh_key_id):
        return self.delete(self.ssh_keys_url(ssh_key_id))

    @staticmethod
    def jira_issue_attachment_url(id=None, org_id=None):
        url = 'jira_issue_attachments'
        if id is not None:
            url = '%s/%s' % (url, id)
        if org_id is not None:
            url = '%s/%s' % (Client.organization_url(org_id), url)
        return url

    def jira_issue_attachment_create(self, org_id, params):
        return self.post(self.jira_issue_attachment_url(org_id=org_id), params)

    def jira_issue_attachment_update(self, attachment_id, params):
        return self.patch(self.jira_issue_attachment_url(attachment_id), params)

    def jira_issue_attachment_delete(self, attachment_id):
        return self.delete(self.jira_issue_attachment_url(attachment_id))

    def jira_issue_attachment_list(self, org_id, client_key, project_key,
                                   issue_number):
        query_params = {
            'client_key': client_key,
            'project_key': project_key,
            'issue_number': issue_number
        }
        return self.get(self.jira_issue_attachment_url(org_id=org_id) +
                        self.query_url(**query_params))

    @staticmethod
    def download_audit_result_url(organization_id, audit_id):
        return '%s/audit_results/%s' % (
            Client.organization_url(organization_id), audit_id)

    def download_audit_result(self, organization_id, audit_id):
        return self.get(self.download_audit_result_url(organization_id,
                                                       audit_id))

    @staticmethod
    def resources_count_url(organization_id):
        return '%s/resources_count' % Client.organization_url(organization_id)

    def resources_count_get(self, organization_id, start_date, end_date,
                            breakdown_by=None, params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date,
        }
        if breakdown_by:
            query_params['breakdown_by'] = breakdown_by
        if params:
            query_params.update(params)
        url = self.resources_count_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def available_filters_url(organization_id):
        return '%s/available_filters' % Client.organization_url(organization_id)

    def available_filters_get(self, organization_id, start_date, end_date,
                              params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if params:
            query_params.update(params)
        url = self.available_filters_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def breakdown_expenses_url(organization_id):
        return '%s/breakdown_expenses' % Client.organization_url(
            organization_id)

    def breakdown_expenses_get(self, organization_id, start_date, end_date,
                               breakdown_by=None, params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if breakdown_by:
            query_params['breakdown_by'] = breakdown_by
        if params:
            query_params.update(params)
        url = self.breakdown_expenses_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def organization_constraint_url(id=None, org_id=None):
        url = 'organization_constraints'
        if id is not None:
            url = '%s/%s' % (url, id)
        if org_id is not None:
            url = '%s/%s' % (Client.organization_url(org_id), url)
        return url

    def organization_constraint_create(self, org_id, params):
        return self.post(self.organization_constraint_url(org_id=org_id),
                         params)

    def organization_constraint_list(self, org_id, hit_days=None, type=None):
        url = self.organization_constraint_url(org_id=org_id)
        if type:
            url += self.query_url(type=type)
        if hit_days:
            url += self.query_url(hit_days=hit_days)
        return self.get(url)

    def organization_constraint_get(self, constraint_id):
        return self.get(self.organization_constraint_url(constraint_id))

    def organization_constraint_update(self, constraint_id, params):
        return self.patch(self.organization_constraint_url(constraint_id),
                          params)

    def organization_constraint_delete(self, constraint_id):
        return self.delete(self.organization_constraint_url(constraint_id))

    @staticmethod
    def organization_limit_hit_url(id=None, org_id=None):
        url = 'organization_limit_hits'
        if id is not None:
            url = '%s/%s' % (url, id)
        if org_id is not None:
            url = '%s/%s' % (Client.organization_url(org_id), url)
        return url

    def organization_limit_hit_create(self, org_id, params):
        return self.post(self.organization_limit_hit_url(org_id=org_id),
                         params)

    def organization_limit_hit_list(self, org_id, constraint_id=None):
        query_params = {
            'constraint_id': constraint_id,
        }
        url = self.organization_limit_hit_url(org_id=org_id) + self.query_url(
            **query_params)
        return self.get(url)

    def organization_limit_hit_update(self, hit_id, params):
        return self.patch(self.organization_limit_hit_url(hit_id),
                          params)

    @staticmethod
    def breakdown_tags_url(organization_id):
        return '%s/breakdown_tags' % Client.organization_url(
            organization_id)

    def breakdown_tags_get(self, organization_id, start_date, end_date,
                           params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if params:
            query_params.update(params)
        url = self.breakdown_tags_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def traffic_processing_task_url(id=None, cloud_account_id=None):
        url = 'traffic_processing_tasks'
        if id is not None:
            url = '%s/%s' % (url, id)
        if cloud_account_id is not None:
            url = '%s/%s' % (Client.cloud_account_url(cloud_account_id), url)
        return url

    def traffic_processing_task_create(self, cloud_account_id, params):
        return self.post(self.traffic_processing_task_url(
            cloud_account_id=cloud_account_id), params)

    def traffic_processing_task_list(self, cloud_account_id):
        url = self.traffic_processing_task_url(
            cloud_account_id=cloud_account_id)
        return self.get(url)

    def traffic_processing_task_delete(self, task_id):
        return self.delete(self.traffic_processing_task_url(task_id))

    @staticmethod
    def traffic_expenses_url(organization_id):
        return '%s/traffic_expenses' % Client.organization_url(organization_id)

    def traffic_expenses_get(self, organization_id, start_date, end_date,
                             params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if params:
            query_params.update(params)
        url = self.traffic_expenses_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def breakdown_archived_recommendations_url(organization_id):
        return '{}/breakdown_archived_recommendations'.format(
            Client.organization_url(organization_id))

    def breakdown_archived_recommendations_get(
            self, organization_id, start_date, end_date, params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if params:
            query_params.update(params)
        url = self.breakdown_archived_recommendations_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def archived_recommendations_details_url(organization_id):
        return '{}/archived_recommendations_details'.format(
            Client.organization_url(organization_id))

    def archived_recommendations_details_get(
            self, organization_id, type, reason, archived_at, **params):
        query_params = {
            'type': type,
            'reason': reason,
            'archived_at': archived_at,
            **params
        }
        url = self.archived_recommendations_details_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def archived_recommendations_count_url(organization_id):
        return '{}/archived_recommendations_count'.format(
            Client.organization_url(organization_id))

    def archived_recommendations_count_get(
            self, organization_id, start_date, end_date, params=None):
        query_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if params:
            query_params.update(params)
        url = self.archived_recommendations_count_url(
            organization_id) + self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def applications_url(organization_id, id=None):
        url = '%s/applications' % Client.organization_url(organization_id)
        if id is not None:
            url += '/%s' % id
        return url

    @staticmethod
    def profiling_token_url(organization_id):
        return '%s/profiling_token' % Client.organization_url(organization_id)

    @staticmethod
    def infra_profiling_token_url(infrastructure_token):
        return 'infrastructure/%s/profiling_token' % infrastructure_token

    @staticmethod
    def goals_url(organization_id, id=None):
        url = '%s/goals' % Client.organization_url(organization_id)
        if id is not None:
            url += '/%s' % id
        return url

    @staticmethod
    def executors_url(organization_id):
        return '%s/executors' % Client.organization_url(organization_id)

    @staticmethod
    def executors_breakdown_url(organization_id):
        return '%s/executors_breakdown' % Client.organization_url(
            organization_id)

    @staticmethod
    def runs_url(organization_id, id=None, application_id=None):
        base_url = Client.organization_url(organization_id)
        if application_id:
            base_url += '/applications/%s' % application_id
        base_url += '/runs'
        if id:
            base_url += '/%s' % id
        return base_url

    @staticmethod
    def runs_breakdown_url(organization_id, id):
        return '%s/breakdown' % Client.runs_url(organization_id, id)

    @staticmethod
    def runs_bulk_url(organization_id, application_id):
        url = "%s/runs/bulk" % Client.applications_url(organization_id,
                                                       application_id)
        return url

    @staticmethod
    def application_optimizations_url(organization_id, application_id):
        return '%s/optimizations' % Client.applications_url(
            organization_id, application_id)

    def application_create(self, organization_id, params):
        return self.post(self.applications_url(organization_id), params)

    def application_list(self, organization_id):
        return self.get(self.applications_url(organization_id))

    def application_get(self, organization_id, application_id):
        return self.get(self.applications_url(
            organization_id, application_id))

    def application_update(self, organization_id, application_id, params):
        return self.patch(
            self.applications_url(organization_id, application_id), params)

    def application_delete(self, organization_id, application_id):
        return self.delete(self.applications_url(
            organization_id, application_id))

    def profiling_token_get(self, organization_id):
        return self.get(self.profiling_token_url(organization_id))

    def goal_create(self, organization_id, params):
        return self.post(self.goals_url(organization_id), params)

    def goal_list(self, organization_id):
        return self.get(self.goals_url(organization_id))

    def goal_get(self, organization_id, goal_id):
        return self.get(self.goals_url(organization_id, goal_id))

    def goal_update(self, organization_id, name, goal_id):
        return self.patch(self.goals_url(organization_id, name), goal_id)

    def goal_delete(self, organization_id, goal_id):
        return self.delete(self.goals_url(
            organization_id, goal_id))

    def executor_list(self, organization_id, application_ids=None,
                      run_ids=None):
        url = self.executors_url(organization_id) + self.query_url(
            application_id=application_ids, run_id=run_ids)
        return self.get(url)

    def executors_breakdown_get(self, organization_id):
        url = self.executors_breakdown_url(organization_id)
        return self.get(url)

    def run_get(self, organization_id, run_id):
        return self.get(self.runs_url(organization_id, run_id))

    def run_breakdown_get(self, organization_id, run_id):
        return self.get(self.runs_breakdown_url(organization_id, run_id))

    def run_list(self, organization_id, application_id, **kwargs):
        url = self.runs_url(organization_id, application_id=application_id
                            ) + self.query_url(**kwargs)
        return self.get(url)

    def application_optimizations_get(self, organization_id, application_id,
                                      types=None, status=None):
        url = self.application_optimizations_url(
            organization_id, application_id)
        query_params = {}
        if types is not None:
            query_params['type'] = types
        if status is not None:
            query_params['status'] = status
        if query_params:
            url += self.query_url(**query_params)
        return self.get(url)

    @staticmethod
    def risp_processing_task_url(id=None, cloud_account_id=None):
        url = 'risp_processing_tasks'
        if id is not None:
            url = '%s/%s' % (url, id)
        if cloud_account_id is not None:
            url = '%s/%s' % (Client.cloud_account_url(cloud_account_id), url)
        return url

    def risp_processing_task_create(self, cloud_account_id, params):
        return self.post(self.risp_processing_task_url(
            cloud_account_id=cloud_account_id), params)

    def risp_processing_task_list(self, cloud_account_id):
        url = self.risp_processing_task_url(cloud_account_id=cloud_account_id)
        return self.get(url)

    def risp_processing_task_delete(self, task_id):
        return self.delete(self.risp_processing_task_url(task_id))

    def ri_sp_usage_breakdown_url(self, organization_id):
        return '%s/ri_sp_usage_breakdown' % self.organization_url(
            organization_id)

    def ri_sp_usage_breakdown_get(self, organization_id, **kwargs):
        url = self.ri_sp_usage_breakdown_url(organization_id) + self.query_url(
            **kwargs)
        return self.get(url)

    def ri_sp_expenses_breakdown_url(self, organization_id):
        return '%s/ri_sp_expenses_breakdown' % self.organization_url(
            organization_id)

    def ri_sp_expenses_breakdown_get(self, organization_id, **kwargs):
        url = self.ri_sp_expenses_breakdown_url(organization_id) + self.query_url(
            **kwargs)
        return self.get(url)

    def profiling_token_by_infrastructure_token_get(self, infrastructure_token):
        return self.get(self.infra_profiling_token_url(infrastructure_token))

    @staticmethod
    def templates_url(organization_id, id=None):
        url = '%s/templates' % Client.organization_url(organization_id)
        if id is not None:
            url += '/%s' % id
        return url

    @staticmethod
    def templates_overview_url(organization_id):
        return '%s/templates_overview' % Client.organization_url(
            organization_id)

    def template_create(self, organization_id, params):
        return self.post(self.templates_url(organization_id), params)

    def templates_overview(self, organization_id):
        return self.get(self.templates_overview_url(organization_id))

    def template_get(self, organization_id, template_id):
        return self.get(self.templates_url(organization_id, template_id))

    def template_update(self, organization_id, template_id, params):
        return self.patch(self.templates_url(
            organization_id, template_id), params)

    def template_delete(self, organization_id, template_id):
        return self.delete(self.templates_url(organization_id, template_id))

    @staticmethod
    def template_runsets_url(organization_id, template_id):
        return '%s/runsets' % Client.templates_url(organization_id, template_id)

    @staticmethod
    def runsets_url(organization_id, id=None):
        url = '%s/runsets' % Client.organization_url(organization_id)
        if id is not None:
            url += '/%s' % id
        return url

    def runset_create(self, organization_id, template_id, params):
        return self.post(self.template_runsets_url(
            organization_id, template_id), params)

    def runset_update(self, organization_id, runset_id, params):
        return self.patch(self.runsets_url(
            organization_id, runset_id), params)

    def runset_get(self, organization_id, runset_id):
        return self.get(self.runsets_url(organization_id, runset_id))

    def runset_list(self, organization_id, template_id):
        return self.get(self.template_runsets_url(
            organization_id, template_id))

    @staticmethod
    def runners_url(organization_id, runset_id):
        return '%s/runners' % Client.runsets_url(organization_id, runset_id)

    def runners_list(self, organization_id, runset_id):
        return self.get(self.runners_url(organization_id, runset_id))

    @staticmethod
    def runset_runs_url(organization_id, runset_id):
        return '%s/runsets/%s/runs' % (
            Client.organization_url(organization_id), runset_id)

    def runset_run_list(self, organization_id, runset_id):
        return self.get(self.runset_runs_url(organization_id, runset_id))

    @staticmethod
    def bi_url(*, id_=None, org_id=None):
        url = 'bi'
        if id_ is not None:
            url = '%s/%s' % (url, id_)
        if org_id is not None:
            url = '%s/%s' % (Client.organization_url(org_id), url)
        return url

    def bi_list(self, org_id=None, params=None):
        url = self.bi_url(org_id=org_id)
        return self.get(url, body=params)

    def bi_create(self, org_id, type_: str, name: str = None,
                  days: int = 180, **meta):
        body = {
            "type": type_,
            "days": days
        }
        if name:
            body['name'] = name
        if meta:
            body['meta'] = meta

        return self.post(self.bi_url(org_id=org_id), body)

    def bi_get(self, id_):
        return self.get(self.bi_url(id_=id_))

    def bi_update(self, id_, params):
        return self.patch(self.bi_url(id_=id_), params)

    def bi_delete(self, id_):
        return self.delete(self.bi_url(id_=id_))

    @staticmethod
    def relevant_flavors_url(org_id):
        return '%s/relevant_flavors' % Client.organization_url(org_id)

    def get_relevant_flavors(self, org_id, region, **kwargs):
        params = {
            'region': region
        }
        if kwargs:
            params.update(kwargs)
        url = self.relevant_flavors_url(org_id) + self.query_url(**params)
        return self.get(url)

    @staticmethod
    def geminis_url(id_=None, organization_id=None):
        url = 'geminis'
        if id_ is not None:
            url = '%s/%s' % (url, id_)
        if organization_id is not None:
            url = '%s/%s' % (Client.organization_url(organization_id), url)
        return url

    @staticmethod
    def disconnect_survey_url(organization_id):
        url = 'disconnect_survey'
        url = '%s/%s' % (Client.organization_url(organization_id), url)
        return url

    @staticmethod
    def geminis_data_url(id_):
        return 'geminis/%s/data' % id_

    def gemini_list(self, organization_id=None, params=None):
        url = self.geminis_url(organization_id=organization_id)
        return self.get(url, body=params)

    def gemini_create(self, organization_id, params):
        return self.post(self.geminis_url(organization_id=organization_id),
                         params)

    def gemini_get(self, id_):
        return self.get(self.geminis_url(id_=id_))

    def gemini_data_get(self, id_, params=None):
        url = self.geminis_data_url(id_=id_)
        if params:
            url += self.query_url(**params)
        return self.get(url)

    def gemini_update(self, id_, params):
        return self.patch(self.geminis_url(id_=id_), params)

    def gemini_delete(self, id_):
        return self.delete(self.geminis_url(id_=id_))

    def disconnect_survey_submit(self, organization_id, survey_type, payload):
        body = {
            "survey_type": survey_type,
            "payload": payload
        }
        return self.post(self.disconnect_survey_url(
            organization_id=organization_id), body)

    @staticmethod
    def power_schedules_url(id_=None, organization_id=None):
        url = 'power_schedules'
        if id_ is not None:
            url = '%s/%s' % (url, id_)
        if organization_id is not None:
            url = '%s/%s' % (Client.organization_url(organization_id), url)
        return url

    def power_schedules_actions_url(self, id_):
        return '%s/actions' % self.power_schedules_url(id_=id_)

    def power_schedule_list(self, organization_id=None):
        return self.get(
            self.power_schedules_url(organization_id=organization_id))

    def power_schedule_create(self, organization_id, params):
        return self.post(
            self.power_schedules_url(organization_id=organization_id), params)

    def power_schedule_get(self, id_):
        return self.get(self.power_schedules_url(id_=id_))

    def power_schedule_update(self, id_, params):
        return self.patch(self.power_schedules_url(id_=id_), params)

    def power_schedule_delete(self, id_):
        return self.delete(self.power_schedules_url(id_=id_))

    def power_schedule_actions(self, id_, params):
        url = self.power_schedules_actions_url(id_=id_)
        return self.post(url, params)

    def leaderboard_url(self, organization_id, application_id):
        return '%s/leaderboard' % Client.applications_url(
            organization_id, application_id)

    @staticmethod
    def leaderboard_dataset_url(organization_id, leaderboard_dataset_id):
        return '%s/leaderboard_datasets/%s' % (
            Client.organization_url(organization_id), leaderboard_dataset_id)

    @staticmethod
    def leaderboard_generate_url(organization_id, leaderboard_dataset_id):
        return "%s/generate" % (Client.leaderboard_dataset_url(
            organization_id, leaderboard_dataset_id))

    @staticmethod
    def leaderboard_datasets_url(organization_id, leaderboard_id):
        return '%s/leaderboards/%s/leaderboard_datasets' % (
            Client.organization_url(organization_id), leaderboard_id)

    def leaderboard_create(self, organization_id, application_id, params):
        return self.post(
            self.leaderboard_url(organization_id, application_id), params)

    def leaderboard_get(self, organization_id, application_id, details=False):
        url = self.leaderboard_url(
            organization_id, application_id) + self.query_url(details=details)
        return self.get(url)

    def leaderboard_update(self, organization_id, application_id, params):
        return self.patch(
            self.leaderboard_url(organization_id, application_id), params)

    def leaderboard_delete(self, organization_id, application_id):
        return self.delete(
            self.leaderboard_url(organization_id, application_id))

    @staticmethod
    def datasets_url(organization_id, id=None):
        url = '%s/datasets' % Client.organization_url(organization_id)
        if id is not None:
            url += '/%s' % id
        return url

    def dataset_create(self, organization_id, params):
        return self.post(self.datasets_url(organization_id), params)

    def dataset_update(self, organization_id, dataset_id, params):
        return self.patch(self.datasets_url(
            organization_id, dataset_id), params)

    def dataset_delete(self, organization_id, dataset_id):
        return self.delete(self.datasets_url(organization_id, dataset_id))

    def dataset_get(self, organization_id, dataset_id):
        return self.get(self.datasets_url(organization_id, dataset_id))

    def dataset_list(self, organization_id):
        return self.get(self.datasets_url(organization_id))

    @staticmethod
    def labels_url(organization_id):
        return '%s/labels' % Client.organization_url(organization_id)

    def labels_list(self, organization_id):
        return self.get(self.labels_url(organization_id))

    def leaderboard_dataset_get(self, organization_id, leaderboard_dataset_id,
                                details=False):
        url = self.leaderboard_dataset_url(
            organization_id, leaderboard_dataset_id) + self.query_url(
            details=details)
        return self.get(url)

    def leaderboard_dataset_create(self, organization_id, name, leaderboard_id,
                                   dataset_ids):
        params = {
            "name": name,
            "dataset_ids": dataset_ids
        }
        url = self.leaderboard_datasets_url(organization_id, leaderboard_id)
        return self.post(url, params)

    def leaderboard_dataset_update(self, organization_id,
                                   leaderboard_dataset_id,  name=None,
                                   dataset_ids=None):
        params = {
            "name": name,
            "dataset_ids": dataset_ids
        }
        url = self.leaderboard_dataset_url(organization_id,
                                           leaderboard_dataset_id)
        return self.patch(url, params)

    def leaderboard_dataset_delete(self, organization_id,
                                   leaderboard_dataset_id):
        url = self.leaderboard_dataset_url(organization_id,
                                           leaderboard_dataset_id)
        return self.delete(url)

    def leaderboard_generate(self, organization_id, leaderboard_dataset_id):
        return self.get(self.leaderboard_generate_url(organization_id,
                                                      leaderboard_dataset_id))

    def runs_bulk_get(self, organization_id, application_id, run_ids):
        url = Client.runs_bulk_url(organization_id, application_id)
        url += self.query_url(
            run_id=run_ids,
        )
        return self.get(url)

    def leaderboard_dataset_list(self, organization_id, leaderboard_id):
        url = self.leaderboard_datasets_url(
            organization_id, leaderboard_id)
        return self.get(url)

    @staticmethod
    def layouts_url(org_id, layout_id=None):
        url = '%s/layouts' % Client.organization_url(org_id)
        if layout_id is not None:
            url = '%s/%s' % (url, layout_id)
        return url

    def layouts_create(self, organization_id, params):
        return self.post(self.layouts_url(organization_id), params)

    def layouts_list(self, org_id, layout_type=None, include_shared=False,
                     entity_id=None):
        url = self.layouts_url(org_id) + self.query_url(
            layout_type=layout_type, include_shared=include_shared,
            entity_id=entity_id)
        return self.get(url)

    def layout_get(self, org_id, layout_id):
        url = self.layouts_url(org_id, layout_id)
        return self.get(url)

    def layout_update(self, org_id, layout_id, params):
        url = self.layouts_url(org_id, layout_id)
        return self.patch(url, params)

    def layout_delete(self, org_id, layout_id):
        url = self.layouts_url(org_id, layout_id)
        return self.delete(url)
