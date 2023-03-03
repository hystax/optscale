import os
import logging
import argparse
import tornado.ioloop
import pydevd_pycharm
from etcd import Lock as EtcdLock
from tornado.web import RedirectHandler

import config_client.client

import rest_api_server.handlers.v1 as h_v1
import rest_api_server.handlers.v2 as h_v2
from rest_api_server.constants import urls_v2
from rest_api_server.handlers.v1.base import DefaultHandler
from rest_api_server.models.db_factory import DBType, DBFactory
from rest_api_server.handlers.v1.swagger import SwaggerStaticFileHandler


DEFAULT_PORT = 8999
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80

LOG = logging.getLogger(__name__)

BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)
SWAGGER_PATH = os.path.join(BASEDIR_PATH, 'swagger')

BASE_URL_PREFIX = "/restapi"
URL_PREFIX_v2 = "/restapi/v2"


def get_handlers(handler_kwargs, version=None):
    result = []
    versions_map = {
        'v2': (urls_v2, h_v2)
    }
    if version:
        versions = [versions_map.get(version)]
    else:
        versions = [v for _, v in versions_map.items()]
    for urls, handlers in versions:
        result.extend([
            (urls.context,
             get_handler_version(handlers, "context"
                                 ).ContextAsyncHandler, handler_kwargs),
            (urls.auth_hierarchy,
             get_handler_version(handlers, "auth_hierarchy"
                                 ).AuthHierarchyAsyncHandler, handler_kwargs),
            (urls.resources_info,
             get_handler_version(handlers, "resources"
                                 ).ResourcesAsyncHandler, handler_kwargs),
        ])

    # v2 only
    if not version or version == 'v2':
        profiling_urls = [
            (urls_v2.applications_collection,
             h_v2.profiling.applications.ApplicationsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.applications,
             h_v2.profiling.applications.ApplicationsAsyncItemHandler,
             handler_kwargs),
            (urls_v2.profiling_executors,
             h_v2.profiling.executors.ExecutorAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.executors_breakdown,
             h_v2.profiling.executors.ExecutorBreakdownAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.goals_collection,
             h_v2.profiling.goals.GoalAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.goals,
             h_v2.profiling.goals.GoalsAsyncItemHandler,
             handler_kwargs),
            (urls_v2.profiling_token_collection,
             h_v2.profiling.profiling_tokens.ProfilingTokenAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.runs,
             h_v2.profiling.runs.RunAsyncItemHandler,
             handler_kwargs),
            (urls_v2.runs_breakdown,
             h_v2.profiling.runs.RunBreakdownItemHandler,
             handler_kwargs),
            (urls_v2.application_runs,
             h_v2.profiling.runs.RunAsyncCollectionHandler,
             handler_kwargs),
        ]
        result.extend([
            (urls_v2.organizations_collection,
             h_v2.organizations.OrganizationAsyncCollectionHandler, handler_kwargs),
            (urls_v2.organizations,
             h_v2.organizations.OrganizationAsyncItemHandler, handler_kwargs),
            (urls_v2.organization_options_collection,
             h_v2.organization_options.OrganizationOptionsAsyncCollectionHandler, handler_kwargs),
            (urls_v2.organization_options,
             h_v2.organization_options.OrganizationOptionsAsyncItemHandler, handler_kwargs),
            (urls_v2.cloud_account_collection,
             h_v2.cloud_account.CloudAccountAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.cloud_account,
             h_v2.cloud_account.CloudAccountAsyncItemHandler,
             handler_kwargs),
            (urls_v2.employees_collection,
             h_v2.employees.EmployeeAsyncCollectionHandler, handler_kwargs),
            (urls_v2.employees,
             h_v2.employees.EmployeeAsyncItemHandler, handler_kwargs),
            (urls_v2.pools,
             h_v2.pools.PoolAsyncItemHandler, handler_kwargs),
            (urls_v2.cloud_resources_collection,
             h_v2.cloud_resources.CloudResourceAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.cloud_resources,
             h_v2.cloud_resources.CloudResourceAsyncItemHandler,
             handler_kwargs),
            (urls_v2.cloud_account_verify,
             h_v2.cloud_account_verify.CloudAccountVerifyHandler,
             handler_kwargs),
            (urls_v2.schedule_imports,
             h_v2.schedule_imports.ScheduleImportsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.pool_breakdown_expenses,
             h_v2.expenses.ExpenseAsyncPoolHandler, handler_kwargs),
            (urls_v2.cloud_account_expenses,
             h_v2.expenses.ExpenseAsyncCloudHandler,
             handler_kwargs),
            (urls_v2.employees_expenses,
             h_v2.expenses.ExpenseAsyncEmployeeHandler, handler_kwargs),
            (urls_v2.report_imports_collection,
             h_v2.report_imports.ReportImportAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.report_imports,
             h_v2.report_imports.ReportImportAsyncItemHandler,
             handler_kwargs),
            (urls_v2.invites,
             h_v2.invites.InvitesAsyncItemHandler, handler_kwargs),
            (urls_v2.invites_collection,
             h_v2.invites.InviteAsyncCollectionHandler, handler_kwargs),
            (urls_v2.assignment_requests_collection,
             h_v2.assignment_request.AssignmentRequestAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.assignment_requests,
             h_v2.assignment_request.AssignmentRequestAsyncItemHandler,
             handler_kwargs),
            (urls_v2.assignment_collection,
             h_v2.assignment.AssignmentAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.cloud_resources_discovery,
             h_v2.cloud_resources_discover.CloudResourceDiscoverAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.alerts,
             h_v2.pool_alerts.PoolAlertsItemHandler,
             handler_kwargs),
            (urls_v2.alerts_collection,
             h_v2.pool_alerts.PoolAlertsCollectionHandler,
             handler_kwargs),
            (urls_v2.process_alerts,
             h_v2.pool_alerts.PoolAlertsProcessHandler,
             handler_kwargs),
            (urls_v2.split_resources,
             h_v2.cloud_resources_split.SplitResourcesAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.my_tasks, h_v2.my_tasks.MyTasksAsyncHandler,
             handler_kwargs),
            (urls_v2.assignment_collection_bulk,
             h_v2.assignment_bulk.AssignmentAsyncCollectionBulkHandler,
             handler_kwargs),
            (urls_v2.assignment_requests_collection_bulk,
             h_v2.assignment_request_bulk.AssignmentRequestAsyncCollectionBulkHandler,
             handler_kwargs),
            (urls_v2.org_pools_collection,
             h_v2.pools.PoolAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.raw_expenses, h_v2.expenses.RawExpenseAsyncHandler,
             handler_kwargs),
            (urls_v2.pool_employee_collection,
             h_v2.pool_employees.PoolEmployeesAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.pool_expenses,
             h_v2.pool_expenses.PoolExpensesAsyncHandler,
             handler_kwargs),
            (urls_v2.cloud_resources_bulk,
             h_v2.cloud_resources_bulk.CloudResourceAsyncBulkCollectionHandler,
             handler_kwargs),
            (urls_v2.clean_expenses, h_v2.expenses.CleanExpenseAsyncHandler,
             handler_kwargs),
            (urls_v2.summary_expenses, h_v2.expenses.SummaryExpenseAsyncHandler,
             handler_kwargs),
            (urls_v2.rules_collection, h_v2.rule.RuleAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.rule_priority, h_v2.rule.RulePriorityAsyncItemHandler,
             handler_kwargs),
            (urls_v2.rules, h_v2.rule.RuleAsyncItemHandler,
             handler_kwargs),
            (urls_v2.report_upload, h_v2.report_uploads.ReportImportAsyncHandler,
             handler_kwargs),
            (urls_v2.pool_policies_collection,
             h_v2.pool_policies.PoolPoliciesAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.pool_policies,
             h_v2.pool_policies.PoolPoliciesAsyncItemHandler,
             handler_kwargs),
            (urls_v2.resource_limit_hits, h_v2.limit_hits.RecourceLimitHitsAsyncItemHandler,
             handler_kwargs),
            (urls_v2.pool_limit_hits, h_v2.limit_hits.PoolLimitHitsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.resource_constraints_collection,
             h_v2.resource_constraints.ResourceConstraintsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.resource_constraints,
             h_v2.resource_constraints.ResourceConstraintsAsyncItemHandler,
             handler_kwargs),
            (urls_v2.region_expenses, h_v2.expenses.RegionExpenseAsyncCloudHandler,
             handler_kwargs),
            (urls_v2.checklists_collection, h_v2.checklists.ChecklistAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.checklists, h_v2.checklists.ChecklistAsyncItemHandler,
             handler_kwargs),
            (urls_v2.optimizations, h_v2.optimizations.OptimizationAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.optimization_data,
             h_v2.optimizations.OptimizationDataAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.live_demo, h_v2.live_demos.LiveDemoAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.resource_observer, h_v2.resources_observer.ResourcesObserverAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.resource_violations,
             h_v2.resources_observer.ResourcesViolationsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.discovery_info_collection, h_v2.discovery_infos.DiscoveryInfosAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.discovery_info_bulk, h_v2.discovery_infos_bulk.DiscoveryInfosAsyncBulkHandler,
             handler_kwargs),
            (urls_v2.discovery_info, h_v2.discovery_infos.DiscoveryInfosAsyncItemHandler,
             handler_kwargs),
            (urls_v2.discovery_info_switch_enable,
             h_v2.discovery_infos.DiscoveryInfosAsyncSwitchEnableHandler,
             handler_kwargs),
            (urls_v2.cleanup_scripts,
             h_v2.cleanup_scripts.CleanupScriptAsyncItemHandler,
             handler_kwargs),
            (urls_v2.ttl_analysis,
             h_v2.ttl_analysis.TtlAnalysisAsyncItemHandler,
             handler_kwargs),
            (urls_v2.rules_apply,
             h_v2.rule.RulesApplyAsyncHandler, handler_kwargs),
            (urls_v2.resource_optimizations,
             h_v2.optimizations.OptimizationDataAsyncItemHandler,
             handler_kwargs),
            (urls_v2.organizations_overview,
             h_v2.organizations_overview.OrganizationsOverviewAsyncHandler,
             handler_kwargs),
            (urls_v2.cluster_types_collection, h_v2.cluster_types.ClusterTypeAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.cluster_types, h_v2.cluster_types.ClusterTypeAsyncItemHandler,
             handler_kwargs),
            (urls_v2.cluster_type_priority, h_v2.cluster_types.ClusterTypePriorityAsyncHandler,
             handler_kwargs),
            (urls_v2.cluster_types_apply, h_v2.cluster_types.ClusterTypeApplyAsyncHandler,
             handler_kwargs),
            (urls_v2.pool_expenses_export_data, h_v2.pool_expenses_export_data.PoolExpensesExportDataAsyncItemHandler,
             handler_kwargs),
            (urls_v2.pool_expense_exports, h_v2.pool_expenses_export.PoolExpensesExportAsyncItemHandler,
             handler_kwargs),
            (urls_v2.nodes_collection_bulk, h_v2.nodes.NodesAsyncCollectionBulkHandler,
             handler_kwargs),
            (urls_v2.nodes_collection, h_v2.nodes.NodesAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.resource_metrics, h_v2.resource_metrics.ResourceMetricsAsyncItemHandler,
             handler_kwargs),
            (urls_v2.cost_models_collection, h_v2.cost_models.CostModelsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.cloud_account_cost_models, h_v2.cost_models.CloudAccountCostModelsAsyncHandler,
             handler_kwargs),
            (urls_v2.resource_cost_models, h_v2.cost_models.RecourceCostModelsAsyncHandler,
             handler_kwargs),
            (urls_v2.environment_resources_collection,
             h_v2.environment_resources.EnvironmentResourceAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.environment_resources,
             h_v2.environment_resources.EnvironmentResourceAsyncItemHandler,
             handler_kwargs),
            (urls_v2.shareable_book_collection, h_v2.shareable_resources.ShareableBookingAsyncHandler,
             handler_kwargs),
            (urls_v2.shareable_book,
             h_v2.shareable_resources.ShareableBookingAsyncItemHandler,
             handler_kwargs),
            (urls_v2.shareable_resource_collection,
             h_v2.shareable_resources.ShareableResourceAsyncHandler,
             handler_kwargs),
            (urls_v2.shareable_resource_bulk,
             h_v2.shareable_resource_bulk.ShareableResourceBulkAsyncHandler,
             handler_kwargs),
            (urls_v2.shareable_resource_split, h_v2.shareable_resources_split.SplitShareableResourceAsyncHandler,
             handler_kwargs),
            (urls_v2.shareable_resource_bookings,
             h_v2.shareable_resources.ShareableResourceBookingsAsyncHandler,
             handler_kwargs),
            (urls_v2.env_properties_script,
             h_v2.environment_resources_properties.EnvironmentResourcePropertiesScriptAsyncItemHandler,
             handler_kwargs),
            (urls_v2.env_properties_collector,
             h_v2.environment_resources_properties.EnvironmentResourcePropertiesCollectorAsyncItemHandler,
             handler_kwargs),
            (urls_v2.env_properties_history,
             h_v2.environment_resources_properties.EnvironmentResourcePropertiesHistoryAsyncItemHandler,
             handler_kwargs),
            (urls_v2.calendar_synchronizations_collection,
             h_v2.calendar_synchronizations.CalendarSynchronizationAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.calendar_synchronizations,
             h_v2.calendar_synchronizations.CalendarSynchronizationAsyncItemHandler,
             handler_kwargs),
            (urls_v2.organization_calendars,
             h_v2.calendar_synchronizations.OrganizationCalendarAsyncItemHandler,
             handler_kwargs),
            (urls_v2.calendar_observer, h_v2.calendars_observer.CalendarsObserverAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.webhooks_collection, h_v2.webhooks.WebhookAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.webhooks, h_v2.webhooks.WebhookAsyncItemHandler,
             handler_kwargs),
            (urls_v2.webhook_logs, h_v2.webhooks.WebhookLogsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.authorized_employees, h_v2.employees.AuthorizedEmployeeAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.code_report_upload, h_v2.code_report_uploads.CodeReportAsyncHandler,
             handler_kwargs),
            (urls_v2.submit_for_audit, h_v2.submit_for_audit.AuditSubmitAsyncItemHandler,
             handler_kwargs),
            (urls_v2.ssh_keys_collection,  h_v2.ssh_keys.SshKeysAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.ssh_keys, h_v2.ssh_keys.SshKeysAsyncItemHandler,
             handler_kwargs),
            (urls_v2.jira_issue_attachments_collection,
             h_v2.jira_issue_attachments.JiraIssueAttachmentCollectionHandler,
             handler_kwargs),
            (urls_v2.jira_issue_attachments,
             h_v2.jira_issue_attachments.JiraIssueAttachmentItemHandler,
             handler_kwargs),
            (urls_v2.audit_results, h_v2.audit_results.AuditResultAsyncItemHandler,
             handler_kwargs),
            (urls_v2.resources_count, h_v2.resources_count.ResourcesCountAsyncHandler,
             handler_kwargs),
            (urls_v2.available_filters,
             h_v2.available_filters.AvailableFiltersAsyncHandler,
             handler_kwargs),
            (urls_v2.breakdown_expenses,
             h_v2.breakdown_expenses.BreakdownExpensesAsyncHandler,
             handler_kwargs),
            (urls_v2.organization_constraints_collection,
             h_v2.organization_constraints.OrganizationConstraintsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.organization_constraints,
             h_v2.organization_constraints.OrganizationConstraintsAsyncItemHandler,
             handler_kwargs),
            (urls_v2.organization_limit_hits_collection,
             h_v2.organization_limit_hits.OrganizationLimitHitsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.organization_limit_hits,
             h_v2.organization_limit_hits.OrganizationLimitHitsAsyncItemHandler,
             handler_kwargs),
            (urls_v2.breakdown_tags,
             h_v2.breakdown_tags.BreakdownTagsAsyncHandler,
             handler_kwargs),
            (urls_v2.org_resource_policies_collection,
             h_v2.pool_policies.OrganizationPoliciesAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.org_resource_constraints_collection,
             h_v2.resource_constraints.OrganizationConstraintsAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.traffic_processing_tasks,
             h_v2.traffic_processing_tasks.TrafficProcessingTaskAsyncItemHandler,
             handler_kwargs),
            (urls_v2.traffic_processing_tasks_collection,
             h_v2.traffic_processing_tasks.TrafficProcessingTaskAsyncCollectionHandler,
             handler_kwargs),
            (urls_v2.traffic_expenses, h_v2.traffic_expenses.TrafficExpensesAsyncHandler,
             handler_kwargs),
            (urls_v2.breakdown_archived_recommendations,
             h_v2.archived_recommendations.BreakdownArchivedRecommendationsAsyncHandler,
             handler_kwargs),
            (urls_v2.archived_recommendations_details,
             h_v2.archived_recommendations.ArchivedRecommendationsDetailsAsyncHandler,
             handler_kwargs),
            (urls_v2.archived_recommendations_count,
             h_v2.archived_recommendations.ArchivedRecommendationsCountAsyncHandler,
             handler_kwargs),
            (urls_v2.k8s_rightsizing, h_v2.k8s_rightsizing.K8sRightsizingAsyncHandler,
             handler_kwargs),
            *profiling_urls,
        ])
    return result


def get_swagger_urls():
    return [
        (r'%s/swagger/(.*)' % URL_PREFIX_v2,
         SwaggerStaticFileHandler, {'path': SWAGGER_PATH}),
        (r"%s/?" % URL_PREFIX_v2, RedirectHandler,
         {"url": "%s/swagger/spec.html" % URL_PREFIX_v2}),
    ]


def get_handler_version(h_v, handler, default_version=h_v1):
    res = getattr(h_v, handler, None) or getattr(default_version, handler)
    return res


def make_app(db_type, etcd_host, etcd_port, wait=False):
    config_cl = config_client.client.Client(host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()

    db = DBFactory(db_type, config_cl).db
    if wait:
        # Use lock to avoid migration problems with several restapis
        # starting at the same time on cluster
        LOG.info('Waiting for migration lock')
        with EtcdLock(config_cl, 'restapi_migrations'):
            db.create_schema()
    else:
        db.create_schema()

    handler_kwargs = {
        "engine": db.engine,
        "config": config_cl,
    }
    config_cl.tell_everybody_that_i_am_ready()
    return tornado.web.Application(
        get_handlers(handler_kwargs) + get_swagger_urls(),
        default_handler_class=DefaultHandler
    )


def main():
    if os.environ.get('PYCHARM_DEBUG_HOST'):
        pydevd_pycharm.settrace(
            host=os.environ['PYCHARM_DEBUG_HOST'],
            port=int(os.environ.get('PYCHARM_DEBUG_PORT', 3000)),
            stdoutToServer=True,
            stderrToServer=True,
            suspend=False,
        )

    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)

    parser = argparse.ArgumentParser()
    parser.add_argument('--etcdhost', type=str, default=etcd_host)
    parser.add_argument('--etcdport', type=int, default=etcd_port)
    args = parser.parse_args()

    app = make_app(DBType.MySQL, args.etcdhost, args.etcdport, wait=True)
    LOG.info("start listening on port %d", DEFAULT_PORT)
    app.listen(DEFAULT_PORT, decompress_request=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
