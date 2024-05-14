import logging
from collections import defaultdict

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.insecure_security_groups import (
    InsecureSecurityGroups as InsecureSecurityGroupsRecommendation
)


LOG = logging.getLogger(__name__)


class InsecureSecurityGroups(ArchiveBase,
                             InsecureSecurityGroupsRecommendation):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.reason_description_map[
            ArchiveReason.FAILED_DEPENDENCY] = 'security group has been detached'
        self.reason_description_map[
            ArchiveReason.RECOMMENDATION_APPLIED] = 'security group has been changed'

    @property
    def supported_cloud_types(self):
        return list(self.get_cloud_func_map().keys())

    def _is_in_instance_sgs(self, instance, sg_id, cloud_type):
        sgs_ids = instance.get('meta', {}).get('security_groups', [])
        if cloud_type == 'aws_cnr':
            sgs_ids = [x['GroupId'] for x in sgs_ids]
        if sg_id in sgs_ids:
            return True

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):

        cloud_func_map = self.get_cloud_func_map()

        insecure_ports = previous_options.get('insecure_ports')

        opt_instances_ids = set()
        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)
            opt_instances_ids.add(optimization['resource_id'])

        _, active_instances = self.rest_client.cloud_resources_discover(
            self.organization_id, 'instance')

        active_instances_map = {x['cloud_resource_id']: x
                                for x in active_instances['data']}

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            opt_instances = [
                active_instances_map[x['cloud_resource_id']]
                for x in optimizations_
                if (x['cloud_resource_id'] in active_instances_map
                    and x['cloud_account_id'] == cloud_account_id)
            ]
            cloud_config = cloud_accounts_map[cloud_account_id]
            cloud_config.update(cloud_config.get('config', {}))
            security_group_call = cloud_func_map[cloud_config['type']]
            if not security_group_call:
                continue
            try:
                security_groups = security_group_call(
                        cloud_config, opt_instances, [], insecure_ports)
            except Exception as ex:
                LOG.exception(ex)
                continue
            cloud_res_id_sgs = defaultdict(list)
            for security_group_info in security_groups:
                cloud_res_id_sgs[security_group_info[
                    'cloud_resource_id']].append(security_group_info)
            for optimization in optimizations_:
                inst_cloud_res_id = optimization['cloud_resource_id']
                if inst_cloud_res_id not in active_instances_map:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RESOURCE_DELETED)
                    result.append(optimization)
                    continue

                curr_sgs_list = cloud_res_id_sgs[inst_cloud_res_id]
                opt_sg_id = optimization['security_group_id']
                curr_insecure_sg = [x for x in curr_sgs_list
                                    if x['security_group_id'] == opt_sg_id]
                instance = active_instances_map[inst_cloud_res_id]
                if not curr_insecure_sg and not self._is_in_instance_sgs(
                        instance, opt_sg_id, cloud_config['type']):
                    # security group is detached from instance
                    reason = ArchiveReason.FAILED_DEPENDENCY
                elif not curr_insecure_sg:
                    # all security group's ports become secure
                    reason = ArchiveReason.RECOMMENDATION_APPLIED
                else:
                    reason = ArchiveReason.OPTIONS_CHANGED
                self._set_reason_properties(optimization, reason)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InsecureSecurityGroups(
        organization_id, config_client, created_at).get()
