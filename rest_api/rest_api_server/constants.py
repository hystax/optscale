class Urls:
    url_prefix = '/restapi'

    urls_map = {
        'context': r"%s/context",
        'auth_hierarchy': r"%s/auth_hierarchy",
        'resources_info': r"%s/resources_info",
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV2(Urls):
    url_prefix = '/restapi/v2'
    urls_map = dict(Urls.urls_map, **{
        'organizations_collection': r"%s/organizations",
        'organizations': r"%s/organizations/(?P<id>[^/]+)",
        'organization_options_collection': r"%s/organizations/(?P<organization_id>[^/]+)/options",
        'organization_options': r"%s/organizations/(?P<organization_id>[^/]+)/options/(?P<option_name>[^/]+)",
        'pool_breakdown_expenses': r"%s/pools_expenses/(?P<pool_id>[^/]+)",
        'cloud_account_collection': r"%s/organizations/(?P<organization_id>[^/]+)/cloud_accounts",
        'cloud_account': r"%s/cloud_accounts/(?P<id>[^/]+)",
        'cloud_account_expenses': r"%s/clouds_expenses/(?P<cloud_account_id>[^/]+)",
        'employees_collection': r"%s/organizations/(?P<organization_id>[^/]+)/employees",
        'employees': r"%s/employees/(?P<id>[^/]+)",
        'employees_expenses': r"%s/employees_expenses/(?P<employee_id>[^/]+)",
        'pools': r"%s/pools/(?P<id>[^/]+)",
        'cloud_resources_collection': r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/cloud_resources",
        'cloud_resources': r"%s/cloud_resources/(?P<id>[^/]+)",
        'cloud_account_verify': r"%s/cloud_account_verify",
        'report_upload': r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/report_upload",
        'schedule_imports': r"%s/schedule_imports",
        'report_imports_collection': r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/report_imports",
        'report_imports': r"%s/report_imports/(?P<id>[^/]+)",
        'invites': r"%s/invites/(?P<id>[^/]+)",
        'invites_collection': r"%s/invites",
        'assignment_requests_collection': r"%s/organizations/(?P<organization_id>[^/]+)/assignment_requests",
        'assignment_requests': r"%s/assignment_requests/(?P<id>[^/]+)",
        'split_resources': r"%s/organizations/(?P<organization_id>[^/]+)/split_resources/assign",
        'assignment_collection': r"%s/organizations/(?P<organization_id>[^/]+)/assignments",
        'assignment_collection_bulk': r"%s/organizations/(?P<organization_id>[^/]+)/assignments/bulk",
        'assignment_requests_collection_bulk':
            r"%s/organizations/(?P<organization_id>[^/]+)/assignment_requests/bulk",
        'org_pools_collection': r"%s/organizations/(?P<organization_id>[^/]+)/pools",
        'cloud_resources_discovery': r"%s/organizations/(?P<organization_id>[^/]+)/cloud_resources",
        'alerts': r"%s/alerts/(?P<id>[^/]+)",
        'alerts_collection': r"%s/organizations/(?P<organization_id>[^/]+)/alerts",
        'process_alerts': r"%s/organizations/(?P<organization_id>[^/]+)/process_alerts",
        'my_tasks': r"%s/organizations/(?P<organization_id>[^/]+)/my_tasks",
        'raw_expenses': r"%s/resources/(?P<resource_id>[^/]+)/raw_expenses",
        'pool_employee_collection': r"%s/pools/(?P<pool_id>[^/]+)/employees",
        'pool_expenses': r"%s/organizations/(?P<organization_id>[^/]+)/pool_expenses",
        'cloud_resources_bulk': r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/cloud_resources/bulk",
        'clean_expenses': r"%s/organizations/(?P<organization_id>[^/]+)/clean_expenses",
        'rules_collection': r"%s/organizations/(?P<organization_id>[^/]+)/rules",
        'rule_priority': r"%s/rules/(?P<rule_id>[^/]+)/priority",
        'rules': r"%s/rules/(?P<id>[^/]+)",
        'pool_policies_collection': r"%s/pools/(?P<pool_id>[^/]+)/policies",
        'pool_policies': r"%s/policies/(?P<id>[^/]+)",
        'resource_limit_hits': r"%s/cloud_resources/(?P<resource_id>[^/]+)/limit_hits",
        'pool_limit_hits': r"%s/pools/(?P<pool_id>[^/]+)/limit_hits",
        'resource_constraints_collection': r"%s/cloud_resources/(?P<resource_id>[^/]+)/constraints",
        'resource_constraints': r"%s/constraints/(?P<id>[^/]+)",
        'region_expenses': r"%s/organizations/(?P<organization_id>[^/]+)/region_expenses",
        'checklists_collection': r"%s/checklists",
        'checklists': r"%s/checklists/(?P<id>[^/]+)",
        'optimizations': r"%s/organizations/(?P<organization_id>[^/]+)/optimizations",
        'optimization_data': r"%s/organizations/(?P<organization_id>[^/]+)/optimization_data",
        'live_demo': r"%s/live_demo",
        'resource_observer': r"%s/organizations/(?P<organization_id>[^/]+)/resource_observer",
        'resource_violations': r"%s/organizations/(?P<organization_id>[^/]+)/resource_violations",
        'discovery_info_collection': r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/discovery_info",
        'discovery_info_bulk': r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/discovery_info/bulk",
        'discovery_info': r"%s/discovery_info/(?P<id>[^/]+)",
        'discovery_info_switch_enable':
            r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/switch_enable",
        'cleanup_scripts': r'%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/cleanup_(?P<module_name>[A-Za-z0-9_]+).sh',
        'ttl_analysis': r'%s/pools/(?P<pool_id>[^/]+)/ttl_analysis',
        'rules_apply': r'%s/organizations/(?P<organization_id>[^/]+)/rules_apply',
        'resource_optimizations': r"%s/resources/(?P<resource_id>[^/]+)/optimizations",
        'cluster_types_collection': r"%s/organizations/(?P<organization_id>[^/]+)/cluster_types",
        'cluster_types': r"%s/cluster_types/(?P<id>[^/]+)",
        'cluster_type_priority': r"%s/cluster_types/(?P<id>[^/]+)/priority",
        'cluster_types_apply': r'%s/organizations/(?P<organization_id>[^/]+)/cluster_types_apply',
        'organizations_overview': r"%s/organizations_overview",
        'pool_expenses_export_data': r"%s/pool_expenses_exports/(?P<export_id>[^/]+)",
        'pool_expense_exports': r"%s/pools/(?P<pool_id>[^/]+)/expenses_export",
        'nodes_collection_bulk': r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/nodes/bulk",
        'nodes_collection': r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/nodes",
        'resource_metrics': r"%s/cloud_resources/(?P<resource_id>[^/]+)/metrics",
        'cost_models_collection': r"%s/organizations/(?P<organization_id>[^/]+)/cost_models",
        'cloud_account_cost_models': r"%s/cloud_account_cost_models/(?P<id>[^/]+)",
        'resource_cost_models': r"%s/resource_cost_models/(?P<id>[^/]+)",
        'sku_cost_models': r"%s/sku_cost_models/(?P<id>[^/]+)",
        'environment_resources_collection': r"%s/organizations/(?P<organization_id>[^/]+)/environment_resources",
        'environment_resources': r"%s/environment_resources/(?P<id>[^/]+)",
        'shareable_book_collection': r"%s/organizations/(?P<organization_id>[^/]+)/shareable_book",
        'shareable_book': r"%s/shareable/(?P<id>[^/]+)",
        'shareable_resource_collection': r"%s/organizations/(?P<organization_id>[^/]+)/shareable_resources",
        'shareable_resource_bulk': r"%s/organizations/(?P<organization_id>[^/]+)/shareable/bulk",
        'shareable_resource_split': r"%s/organizations/(?P<organization_id>[^/]+)/shareable_split",
        'shareable_resource_bookings': r"%s/shareable/(?P<id>[^/]+)/bookings",
        'env_properties_script': r"%s/cloud_resources/(?P<id>[^/]+)/env_properties_script",
        'env_properties_collector': r"%s/cloud_resources/(?P<id>[^/]+)/env_properties_collector",
        'env_properties_history': r"%s/cloud_resources/(?P<id>[^/]+)/env_properties_history",
        'calendar_synchronizations_collection': r"%s/calendar_synchronizations",
        'calendar_synchronizations': r"%s/calendar_synchronizations/(?P<id>[^/]+)",
        'organization_calendars': r"%s/organization_calendars/(?P<organization_id>[^/]+)",
        'calendar_observer': r"%s/organizations/(?P<organization_id>[^/]+)/calendar_observer",
        'webhooks_collection': r"%s/organizations/(?P<organization_id>[^/]+)/webhooks",
        'webhooks': r"%s/webhooks/(?P<id>[^/]+)",
        'webhook_logs': r"%s/webhooks/(?P<webhook_id>[^/]+)/logs",
        'authorized_employees': r"%s/organizations/(?P<organization_id>[^/]+)/authorized_employees",
        'code_report_upload': r"%s/organizations/(?P<organization_id>[^/]+)/code_report_upload",
        'submit_for_audit': r"%s/organizations/(?P<organization_id>[^/]+)/submit_for_audit",
        'ssh_keys_collection': r"%s/employees/(?P<employee_id>[^/]+)/ssh_keys",
        'ssh_keys': r"%s/ssh_keys/(?P<id>[^/]+)",
        'jira_issue_attachments_collection': r"%s/organizations/(?P<organization_id>[^/]+)/jira_issue_attachments",
        'jira_issue_attachments': r"%s/jira_issue_attachments/(?P<id>[^/]+)",
        'audit_results': r"%s/organizations/(?P<organization_id>[^/]+)/audit_results/(?P<audit_id>[^/]+)",
        'resources_count': r"%s/organizations/(?P<organization_id>[^/]+)/resources_count",
        'available_filters': r"%s/organizations/(?P<organization_id>[^/]+)/available_filters",
        'breakdown_expenses': r"%s/organizations/(?P<organization_id>[^/]+)/breakdown_expenses",
        'organization_constraints_collection': r"%s/organizations/(?P<organization_id>[^/]+)/organization_constraints",
        'organization_constraints': r"%s/organization_constraints/(?P<id>[^/]+)",
        'organization_limit_hits_collection': r"%s/organizations/(?P<organization_id>[^/]+)/organization_limit_hits",
        'organization_limit_hits': r"%s/organization_limit_hits/(?P<id>[^/]+)",
        'breakdown_tags': r"%s/organizations/(?P<organization_id>[^/]+)/breakdown_tags",
        'org_resource_policies_collection': r"%s/organizations/(?P<organization_id>["r"^/]+)/resource_policies",
        'org_resource_constraints_collection': r"%s/organizations/(?P<organization_id>["r"^/]+)/resource_constraints",
        'summary_expenses': r"%s/organizations/(?P<organization_id>["r"^/]+)/summary_expenses",
        'traffic_processing_tasks_collection':
            r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/traffic_processing_tasks",
        'traffic_processing_tasks': r"%s/traffic_processing_tasks/(?P<id>[^/]+)",
        'traffic_expenses': r"%s/organizations/(?P<organization_id>[^/]+)/traffic_expenses",
        'breakdown_archived_recommendations': r"%s/organizations/(?P<organization_id>[^/]+)/"
                                              r"breakdown_archived_recommendations",
        'archived_recommendations_details': r"%s/organizations/(?P<organization_id>[^/]+)/"
                                            r"archived_recommendations_details",
        'archived_recommendations_count': r"%s/organizations/(?P<organization_id>[^/]+)/"
                                            r"archived_recommendations_count",
        'k8s_rightsizing': r"%s/organizations/(?P<organization_id>[^/]+)/k8s_rightsizing",
        'tasks_collection': r"%s/organizations/(?P<organization_id>[^/]+)/tasks",
        'tasks': r"%s/organizations/(?P<organization_id>[^/]+)/tasks/(?P<task_id>[^/]+)",
        'task_optimizations':
            r"%s/organizations/(?P<organization_id>[^/]+)/tasks/(?P<task_id>[^/]+)/optimizations",
        'profiling_token_collection': r"%s/organizations/(?P<organization_id>[^/]+)/profiling_token",
        'profiling_token': r"%s/organizations/(?P<organization_id>[^/]+)/profiling_token/(?P<id>[^/]+)",
        'metrics_collection': r"%s/organizations/(?P<organization_id>[^/]+)/metrics",
        'metrics': r"%s/organizations/(?P<organization_id>[^/]+)/metrics/(?P<id>[^/]+)",
        'profiling_executors':
            r"%s/organizations/(?P<organization_id>[^/]+)/executors",
        'executors_breakdown':
            r"%s/organizations/(?P<organization_id>[^/]+)/executors_breakdown",
        'task_runs':
            r"%s/organizations/(?P<organization_id>[^/]+)/tasks/(?P<task_id>[^/]+)/runs",
        'runs': r"%s/organizations/(?P<organization_id>[^/]+)/runs/(?P<id>[^/]+)",
        'runs_breakdown': r"%s/organizations/(?P<organization_id>[^/]+)/runs/(?P<id>[^/]+)/breakdown",
        'risp_processing_tasks_collection':
            r"%s/cloud_accounts/(?P<cloud_account_id>[^/]+)/risp_processing_tasks",
        'risp_processing_tasks': r"%s/risp_processing_tasks/(?P<id>[^/]+)",
        'infra_profiling_token': r"%s/infrastructure/(?P<infrastructure_token>[^/]+)/profiling_token",
        'templates_collection': r"%s/organizations/(?P<organization_id>[^/]+)/templates",
        'templates': r"%s/organizations/(?P<organization_id>[^/]+)/templates/(?P<template_id>[^/]+)",
        'templates_overview': r"%s/organizations/(?P<organization_id>[^/]+)/templates_overview",
        'runsets_collection':
            r"%s/organizations/(?P<organization_id>[^/]+)/templates/(?P<template_id>[^/]+)/runsets",
        'runsets': r"%s/organizations/(?P<organization_id>[^/]+)/runsets/(?P<runset_id>[^/]+)",
        'runners_collection':
            r"%s/organizations/(?P<organization_id>[^/]+)/runsets/(?P<runset_id>[^/]+)/runners",
        'runset_runs_collection':
            r"%s/organizations/(?P<organization_id>[^/]+)/runsets/(?P<runset_id>[^/]+)/runs",
        'org_bi_collection': r"%s/organizations/(?P<organization_id>["r"^/]+)/bi",
        'bi_collection': r"%s/bi",
        'bi': r"%s/bi/(?P<organization_bi_id>["r"^/]+)",
        'relevant_flavors': r"%s/organizations/(?P<organization_id>[^/]+)/relevant_flavors",
        'organization_geminis_collection': r"%s/organizations/(?P<organization_id>["r"^/]+)/geminis",
        'geminis_collection': r"%s/geminis",
        'geminis': r"%s/geminis/(?P<gemini_id>["r"^/]+)",
        'geminis_data': r"%s/geminis/(?P<gemini_id>["r"^/]+)/data",
        'disconnect_survey': r"%s/organizations/(?P<organization_id>["r"^/]+)/disconnect_survey",
        'power_schedules_collection':
            r"%s/organizations/(?P<organization_id>[^/]+)/power_schedules",
        'power_schedules':
            r"%s/power_schedules/(?P<power_schedule_id>["r"^/]+)",
        'power_schedules_actions':
            r"%s/power_schedules/(?P<power_schedule_id>["r"^/]+)/actions",
        'leaderboard_templates': r"%s/organizations/(?P<organization_id>[^/]+)/tasks/"
                                 r"(?P<task_id>[^/]+)/leaderboard_template",
        'datasets_collection': r"%s/organizations/(?P<organization_id>[^/]+)/datasets",
        'datasets': r"%s/organizations/(?P<organization_id>[^/]+)/datasets/(?P<dataset_id>[^/]+)",
        'labels_collection': r"%s/organizations/(?P<organization_id>[^/]+)/labels",
        'leaderboard': r"%s/organizations/(?P<organization_id>[^/]+)/leaderboards/"
                       r"(?P<leaderboard_id>[^/]+)",
        'leaderboard_collection': r"%s/organizations/(?P<organization_id>[^/]+)/leaderboard_templates/"
                                  r"(?P<leaderboard_template_id>[^/]+)/leaderboards",
        'leaderboard_generate': r"%s/organizations/(?P<organization_id>[^/]+)/leaderboards/"
                                r"(?P<leaderboard_id>[^/]+)/generate",
        'runs_bulk': r"%s/organizations/(?P<organization_id>[^/]+)/tasks/"
                     r"(?P<task_id>[^/]+)/runs/bulk",
        'layouts_collection':
            r"%s/organizations/(?P<organization_id>[^/]+)/layouts",
        'layouts': r"%s/organizations/(?P<organization_id>[^/]+)/"
                   r"layouts/(?P<layout_id>[^/]+)",
        'ri_breakdown': r"%s/organizations/(?P<organization_id>["r"^/]+)/ri_breakdown",
        'sp_breakdown': r"%s/organizations/(?P<organization_id>["r"^/]+)/sp_breakdown",
        'offer_breakdown': r"%s/organizations/(?P<organization_id>["r"^/]+)/offer_breakdown",
        'ri_group_breakdown': r"%s/organizations/(?P<organization_id>["r"^/]+)/ri_group_breakdown",
        'models_collection':
            r"%s/organizations/(?P<organization_id>[^/]+)/models",
        'models':
            r"%s/organizations/(?P<organization_id>[^/]+)/"
            r"models/(?P<model_id>[^/]+)",
        'models_versions':
            r"%s/organizations/(?P<organization_id>[^/]+)/"
            r"runs/(?P<run_id>[^/]+)/models/(?P<model_id>[^/]+)/version",
        'models_versions_by_task':
            r"%s/organizations/(?P<organization_id>[^/]+)/"
            r"tasks/(?P<task_id>[^/]+)/model_versions",
        'artifacts_collection':
            r"%s/organizations/(?P<organization_id>[^/]+)/artifacts",
        'artifacts':
            r"%s/organizations/(?P<organization_id>[^/]+)/"
            r"artifacts/(?P<artifact_id>[^/]+)",
        'tags_collection': r"%s/organizations/(?P<organization_id>[^/]+)/"
                           r"tasks/(?P<task_id>[^/]+)/tags",
    })


urls_v2 = UrlsV2()
