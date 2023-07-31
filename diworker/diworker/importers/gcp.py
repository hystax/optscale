from collections import defaultdict
import hashlib
import logging
from datetime import datetime, timedelta
from diworker.importers.base import BaseReportImporter

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
CORES_SYSTEM_TAG = 'compute.googleapis.com/cores'
FLAVOR_SYSTEM_TAG = 'compute.googleapis.com/machine_spec'
OPTSCALE_RESOURCE_ID_TAG = 'optscale_tracking_id'


class GcpReportImporter(BaseReportImporter):

    def get_unique_field_list(self):
        return [
            'start_date',
            'resource_id',
            'resource_hash',
            'cloud_account_id',
            'sku',
            'service'
        ]

    def get_update_fields(self):
        return ['cost', 'usage_amount', 'usage_amount_in_pricing_units', 'credits']

    def _get_resource_region(self, region_data):
        """Gcp provides location info in format:
        {
          "location": "europe-west3",
          "country": "DE",
          "region": "europe-west3",
          "zone": None
        }
        Sometimes region and zone data is None, so use
        country or location as resource's region
        """
        if not region_data:
            return None
        elif region_data.get('region'):
            return region_data['region']
        elif region_data.get('zone'):
            return self.cloud_adapter.zone_region(
                region_data['zone'])
        # see https://datatrendstech.atlassian.net/browse/OS-5071 on why we
        # prefer location over country
        region = region_data['location'] or region_data['country']
        return region.lower() if region else None

    @staticmethod
    def _generate_tags_hash(tags: dict[str: str]) -> str:
        return hashlib.sha1(repr(sorted(tags.items())).encode()).hexdigest()

    @staticmethod
    def _generate_resource_id(row_dict):
        tags_hash = GcpReportImporter._generate_tags_hash(row_dict['tags'])
        return f"{row_dict['sku']} {row_dict['region']} {tags_hash}"

    @staticmethod
    def _convert_tags_list_to_dict(tags):
        if isinstance(tags, list):
            result = {}
            for tag_dict in tags:
                result[tag_dict['key']] = tag_dict['value']
            return result
        else:
            return tags

    def _process_row_cost(self, row_dict: dict):
        # to get the final billed cost we need to add credits,
        # which are usually negative, to cost values.
        # original value of the cost field is stored for visibility.
        row_dict['original_cost'] = row_dict['cost']
        row_dict['cost'] += sum(credit['amount'] for credit in row_dict['credits'])

    def _row_to_dict(self, row):
        row_dict = dict(row.items())
        self._process_row_cost(row_dict)
        row_dict['region'] = self._get_resource_region(
            row_dict.pop('location', None))
        row_dict['cloud_account_id'] = self.cloud_acc_id
        row_dict['tags'] = self._convert_tags_list_to_dict(row_dict['tags'])
        row_dict['system_tags'] = self._convert_tags_list_to_dict(
            row_dict['system_tags'])
        resource_hash = row_dict['tags'].get(OPTSCALE_RESOURCE_ID_TAG)
        # Check that hash is sha1. This is only needed for our hystaxcom account
        # where we experimented with our resource tagging strategies
        # and some expenses have unexpected values for resource hash.
        if resource_hash and len(resource_hash) == 40:
            row_dict['resource_hash'] = resource_hash
        else:
            row_dict['resource_id'] = self._generate_resource_id(row_dict)
        return row_dict

    def _merge_same_billing_items(self, items):
        unique_fields = self.get_unique_field_list()
        update_fields = self.get_update_fields()

        b_item_map = defaultdict(list)
        for b_item in items:
            key = tuple(b_item.get(f) for f in unique_fields)
            b_item_map[key].append(b_item)

        for k, items_list in b_item_map.items():
            if len(items_list) <= 1:
                continue
            common_item = {k: v for k, v in items_list[0].items()}
            for item in items_list[1:]:
                for field in update_fields:
                    value = item.get(field)
                    if value:
                        common_item[field] += value
            b_item_map[k] = [common_item]
        updated_billing_items = [v[0] for v in b_item_map.values()]
        return updated_billing_items

    def load_raw_data(self):
        current_day = self.period_start.replace(
            hour=0, minute=0, second=0, microsecond=0)
        now = datetime.utcnow()
        while current_day <= now:
            chunk = []
            end_date = current_day + timedelta(days=1)
            # sometimes Gcp splits the same expenses for a date into
            # several bills, so merge them into one
            usage_rows = self.cloud_adapter.get_usage(current_day, end_date)
            usage_rows = [self._row_to_dict(r) for r in usage_rows]
            usage_rows = self._merge_same_billing_items(usage_rows)
            for r in usage_rows:
                chunk.append(r)
                if len(chunk) == CHUNK_SIZE:
                    self.update_raw_records(chunk)
                    chunk = []
            if chunk:
                self.update_raw_records(chunk)
            current_day = end_date

    @staticmethod
    def _get_resource_type_and_name(expense):
        cost_type = expense.get('cost_type')
        sku = expense.get('sku')
        region = expense.get('region')
        service = expense.get('service')
        r_name = None
        if cost_type == 'regular':
            if 'Snapshot' in sku:
                r_type = 'Snapshot'
            elif 'PD Capacity' in sku:
                r_type = 'Volume'
            elif 'Storage' in sku:
                r_type = 'Bucket'
            elif 'Instance' in sku and 'discount' not in sku:
                r_type = 'Instance'
            else:
                r_type = f'{service}'
            r_name = f'{sku} {region}'
        elif cost_type == 'tax':
            r_type = 'Tax'
        elif cost_type == 'rounding_error':
            r_type = 'Rounding Error'
            r_name = f'{service} {r_type}'
        elif cost_type == 'adjustment':
            r_type = 'Adjustment'
        else:
            raise Exception(f'Unknown cost_type: {cost_type}')
        if not r_name:
            r_name = f'{sku} {r_type}'
        return r_type, r_name

    def _get_cloud_extras(self, info):
        res = defaultdict(dict)
        for k in ['cpu_count', 'flavor']:
            val = info.get(k)
            if val:
                res['meta'][k] = val
        return res

    def get_resource_info_from_expenses(self, expenses):
        r_type, r_name = self._get_resource_type_and_name(
            expenses[-1])
        service = expenses[-1].get('service')
        region = expenses[-1].get('region')
        first_seen = datetime.utcnow()
        last_seen = datetime.utcfromtimestamp(0).replace()
        tags = {}
        system_tags = {}
        for e in expenses:
            start_date = e['start_date']
            if start_date and start_date < first_seen:
                first_seen = start_date
            end_date = e['end_date']
            if end_date and end_date > last_seen:
                last_seen = end_date
            tags.update(e.get('tags', {}))
            system_tags.update(e.get('system_tags', {}))
        if last_seen < first_seen:
            last_seen = first_seen
        info = {
            'name': r_name,
            'type': r_type,
            'region': region,
            'service_name': service,
            'tags': tags,
            'first_seen': int(first_seen.timestamp()),
            'last_seen': int(last_seen.timestamp())
        }
        if FLAVOR_SYSTEM_TAG in system_tags:
            info['flavor'] = system_tags[FLAVOR_SYSTEM_TAG]
        if CORES_SYSTEM_TAG in system_tags:
            info['cpu_count'] = system_tags[CORES_SYSTEM_TAG]
        LOG.debug('Detected resource info: %s', info)
        return info

    def generate_clean_records(self, regeneration=False):
        def save_expenses(resources_unique_ids, unique_id_field):
            resource_count = len(resources_unique_ids)
            progress = 0
            for i in range(0, resource_count, CHUNK_SIZE):
                new_progress = round(i / resource_count * 100)
                if new_progress != progress:
                    progress = new_progress
                    LOG.info('Progress: %s', progress)

                filters = base_filters + [{unique_id_field: {
                    '$in': resources_unique_ids[i:i + CHUNK_SIZE]
                }}]
                expenses = self.mongo_raw.aggregate([
                    {'$match': {
                        '$and': filters,
                    }},
                    {'$group': {
                        '_id': {
                            unique_id_field: '$%s' % unique_id_field,
                            'start_date': {'$dayOfYear': '$start_date'},
                        },
                        'expenses': {'$push': '$$ROOT'}
                    }},
                ], allowDiskUse=True)
                chunk = defaultdict(list)
                for e in expenses:
                    chunk[e['_id'][unique_id_field]].extend(e['expenses'])
                self.save_clean_expenses(self.cloud_acc_id, chunk,
                                         unique_id_field=unique_id_field)

        base_filters = [{'cloud_account_id': self.cloud_acc_id}]
        if self.period_start:
            base_filters.append({'start_date': {'$gte': self.period_start}})

        distinct_filters = {}
        for f in base_filters:
            distinct_filters.update(f)

        r_id_filters = distinct_filters.copy()
        r_id_filters['resource_id'] = {'$exists': True, '$ne': None}
        resource_ids = self.mongo_raw.distinct('resource_id', r_id_filters)

        r_hash_filters = distinct_filters.copy()
        r_hash_filters['$or'] = [{'resource_id': {'$exists': False}},
                                 {'resource_id': {'$eq': None}}]
        r_hash_filters['resource_hash'] = {'$exists': True}
        resource_hashes = self.mongo_raw.distinct('resource_hash', r_hash_filters)

        LOG.info('Resources with ids count: %s', len(resource_ids))
        save_expenses(resource_ids, 'resource_id')
        LOG.info('Resources without ids count: %s', len(resource_hashes))
        save_expenses(resource_hashes, 'resource_hash')

    def create_traffic_processing_tasks(self):
        self._create_traffic_processing_tasks()
