import logging
from docker_images.keeper_executor.executors.base import BaseEventExecutor
from docker_images.keeper_executor.events import Events

LOG = logging.getLogger(__name__)


class MainEventExecutor(BaseEventExecutor):
    @property
    def action_event_map(self):
        return {
            'katara_task_failed': Events.N0022,
            'power_schedule_created': Events.N0023,
            'power_schedule_updated': Events.N0024,
            'power_schedule_deleted': Events.N0025,
            'power_schedule_processed': Events.N0026,
            'organization_created': Events.N0027,
            'organization_deleted': Events.N0028,
            'organization_updated': Events.N0029,
            'resource_discovery_failed': Events.N0030,
            'alert_removed': Events.N0065,
            'cloud_account_created': Events.N0066,
            'cloud_account_updated': Events.N0067,
            'cloud_account_deleted': Events.N0068,
            'report_import_completed': Events.N0069,
            'report_import_failed': Events.N0070,
            'report_import_throttled': Events.N0163,
            'assignment_request_accepted': Events.N0071,
            'assignment_request_declined': Events.N0072,
            'root_assigned_resource': Events.N0076,
            'rules_processing_completed': Events.N0079,
            'resources_discovered': Events.N0080,
            'rule_applied': Events.N0081,
            'rule_deactivated': Events.N0082,
            'rules_processing_started': Events.N0083,
            'recommendations_dismissed': Events.N0084,
            'recommendations_reactivated': Events.N0085,
            'rule_created': Events.N0086,
            'rule_deleted': Events.N0087,
            'rule_updated': Events.N0088,
            'pool_deleted': Events.N0089,
            'pool_created': Events.N0090,
            'pool_updated': Events.N0091,
            'policy_enabled': Events.N0092,
            'policy_disabled': Events.N0093,
            'policy_created': Events.N0094,
            'policy_deleted': Events.N0095,
            'policy_updated': Events.N0096,
            'employee_invited': Events.N0097,
            'resource_assigned': Events.N0098,
            'constraint_created': Events.N0099,
            'constraint_deleted': Events.N0100,
            'constraint_updated': Events.N0101,
            'cloud_account_warning': Events.N0102,
            'alert_added': Events.N0103,
            'cluster_types_processing_started': Events.N0104,
            'cluster_type_applied': Events.N0105,
            'cluster_types_processing_done': Events.N0106,
            'cluster_resources_deleted': Events.N0107,
            'resources_clustered_discovered': Events.N0108,
            'recalculation_started': Events.N0109,
            'recalculation_completed': Events.N0110,
            'recalculation_failed': Events.N0111,
            'shareable_resource_changed': Events.N0113,
            'shareable_resource_deleted': Events.N0114,
            'shareable_booking_released': Events.N0115,
            'calendar_warning': Events.N0116,
            'calendar_connected': Events.N0117,
            'calendar_disconnected': Events.N0118,
            'calendar_observer_warning': Events.N0119,
            'technical_audit_submit': Events.N0120,
            'env_power_mngmt': Events.N0122,
            'organization_disabled': Events.N0161,
            'organization_enabled': Events.N0162,
        }

    def _execute(self, event, task):
        action = task.get('action')
        organization_id = task.get('organization_id')
        object_id = task.get('object_id')
        object_type = task.get('object_type')
        required_params = [organization_id, object_id, object_type, action]
        if any(map(lambda x: x is None, required_params)):
            raise Exception('Invalid task received: {}'.format(task))
        LOG.info('Started processing for %s object: %s, object type: %s, '
                 'organization %s' % (action, object_id, object_type,
                                      organization_id))
        meta = task.get('meta') or {}
        user_id = meta.get('user_id')
        user_display_name = meta.get('user_display_name')
        user_email = meta.get('user_email')
        description_tmp, param_list, level = event.value
        params = {
            param: task.get(param) or meta.get(param) for param in param_list
        }
        params.update({
            'user_display_name': user_display_name,
            'user_id': user_id,
            'user_email': user_email
        })
        description = description_tmp.format(**params)
        localized = self.get_localized(event.name, param_list, params)
        return {
            'evt_class': action.upper(),
            'organization_id': organization_id,
            'object_id': object_id,
            'object_name': meta.get('object_name') or task.get('object_name'),
            'object_type': object_type,
            'description': description,
            'localized': localized,
            'level': level,
            'user_id': user_id,
            'user_display_name': user_display_name,
            'ack': meta.get('ack', False)
        }
