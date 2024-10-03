#!/usr/bin/env python
import logging
from datetime import datetime, timedelta
from diworker.diworker.importers.base import BaseReportImporter

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200


class EnvironmentReportImporter(BaseReportImporter):
    """
    Environment Report Importer
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._insider_client = None
        self._nodes_provider = None
        self.period_start = None
        if self.cloud_acc.get('last_import_at'):
            last_import_at = self.get_last_import_date(self.cloud_acc_id)
            if last_import_at:
                self.period_start = last_import_at.replace(
                    hour=0, minute=0, second=0, microsecond=0)
        if self.period_start is None:
            self.set_period_start()

    def get_update_fields(self):
        return [
            'value',
            'cost',
            'resource_type'
        ]

    def get_unique_field_list(self):
        return [
            'start_date',
            'end_date',
            'resource_id',
            'cloud_account_id',
        ]

    def load_raw_data(self):
        now = datetime.utcnow()
        org_id = self.cloud_acc['organization_id']
        _, resources = self.rest_cl.environment_resource_list(org_id)

        environment_resources_map = {
            r['id']: r for r in resources.get('resources', [])
            if r.get('active')
        }
        _, cost_models = self.rest_cl.cost_model_list(org_id)
        cost_model_map = {
            c['id']: c['value'] for c in cost_models['cost_models']
        }

        chunk = []
        for k, v in environment_resources_map.items():
            created_at = datetime.fromtimestamp(v['created_at'])
            start_date = self.period_start if (
                    self.period_start > created_at) else created_at
            hourly_cost = cost_model_map.get(k, {}).get('hourly_cost')
            if not hourly_cost:
                continue
            current_day = start_date
            LOG.info('Generating raw expenses for environment resource (%s) '
                     'from %s' % (k, start_date))
            while current_day < now:
                if len(chunk) == CHUNK_SIZE:
                    self.update_raw_records(chunk)
                    chunk = []
                current_day_start = current_day.replace(
                    hour=0, minute=0, second=0, microsecond=0)
                next_day_start = current_day_start + timedelta(days=1)
                current_day_end = next_day_start - timedelta(seconds=1)
                date_end = next_day_start
                if date_end > now:
                    date_end = now
                value = (date_end - current_day).total_seconds() / 3600
                expense = {
                    'start_date': current_day_start,
                    'value': value,
                    'resource_id': v['cloud_resource_id'],
                    'cost': value * hourly_cost,
                    'end_date': current_day_end,
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_type': v['resource_type']
                }
                chunk.append(expense)
                current_day = next_day_start
        if chunk:
            self.update_raw_records(chunk)

    def get_resource_info_from_expenses(self, expenses):
        first_seen = datetime.utcnow()
        last_seen = datetime.utcfromtimestamp(0)
        resource_type = None
        for e in expenses:
            if not resource_type:
                resource_type = e['resource_type']
            start_date = e['start_date']
            if start_date and start_date < first_seen:
                first_seen = start_date
            end_date = e['end_date']
            if end_date and end_date > last_seen:
                last_seen = end_date
        if last_seen < first_seen:
            last_seen = first_seen
        info = {
            'tags': {},
            'first_seen': int(first_seen.timestamp()),
            'last_seen': int(last_seen.timestamp()),
            'resource_type': resource_type
        }
        LOG.debug('Detected resource info: %s', info)
        return info

    def get_resource_data(self, r_id, info,
                          unique_id_field='cloud_resource_id'):
        return {
            'cloud_resource_id': r_id,
            'tags': info['tags'],
            'service_name': info.get('service_name'),
            'first_seen': info['first_seen'],
            'last_seen': info['last_seen'],
            'resource_type': info['resource_type'],
            **self._get_fake_cad_extras(info)
        }

    def get_resource_ids(self, cloud_account_id, period_start):
        all_resource_ids = super().get_resource_ids(cloud_account_id,
                                                    period_start)
        not_deleted_resource_ids = []
        for i in range(0, len(all_resource_ids), CHUNK_SIZE):
            chunk = all_resource_ids[i:i+CHUNK_SIZE]
            chunk_res_ids = [
                x['cloud_resource_id'] for x in self.mongo_resources.find({
                    'cloud_account_id': self.cloud_acc_id,
                    'cloud_resource_id': {'$in': chunk},
                    'deleted_at': 0}, {'cloud_resource_id': 1})]
            not_deleted_resource_ids.extend(chunk_res_ids)
        return not_deleted_resource_ids

    def generate_clean_records(self, regeneration=False):
        if regeneration:
            self.period_start = None
        super().generate_clean_records(regeneration)

    def clean_expenses_for_resource(self, resource_id, expenses):
        clean_expenses = {}
        for e in expenses:
            usage_date = e['start_date']
            if usage_date in clean_expenses:
                clean_expenses[usage_date]['cost'] += e['cost']
            else:
                clean_expenses[usage_date] = {
                    'date': usage_date,
                    'cost': e['cost'],
                    'resource_id': resource_id,
                    'cloud_account_id': e['cloud_account_id']
                }
        return clean_expenses

    def update_cloud_import_time(self, ts):
        if not self.recalculate:
            super().update_cloud_import_time(ts)

    def recalculate_raw_expenses(self):
        organization_id = self.cloud_acc['organization_id']
        _, resources = self.rest_cl.environment_resource_list(organization_id)
        environment_resources_map = {
            r['id']: r for r in resources.get('resources', [])
            if r.get('active')
        }
        _, cost_models = self.rest_cl.cost_model_list(organization_id)
        cost_model_map = {
            c['id']: c['value'] for c in cost_models['cost_models']
        }
        cloud_resource_cost_map = {}
        for r_id, cost_model in cost_model_map.items():
            resource = environment_resources_map.get(r_id)
            hourly_cost = cost_model.get('hourly_cost')
            if not resource or not hourly_cost:
                continue
            cloud_resource_cost_map[
                resource['cloud_resource_id']] = hourly_cost
        if not cloud_resource_cost_map:
            return
        expenses = self.mongo_raw.find({
            'cloud_account_id': self.cloud_acc_id,
            'resource_id': {'$in': list(cloud_resource_cost_map.keys())}
        })
        chunk = []
        for e in expenses:
            hourly_cost = cloud_resource_cost_map[e['resource_id']]
            if e['value'] * hourly_cost != e['cost']:
                e['cost'] = e['value'] * hourly_cost
                chunk.append(e)
            if len(chunk) == CHUNK_SIZE:
                self.update_raw_records(chunk)
                chunk = []
        if chunk:
            self.update_raw_records(chunk)
