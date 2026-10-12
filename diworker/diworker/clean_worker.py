#!/usr/bin/env python
import logging
import time
from collections import defaultdict
from datetime import datetime

from diworker.diworker.importers.base import BaseReportImporter
from diworker.diworker.importers.factory import get_importer_class
from diworker.diworker.worker_base import (
    BaseWorker, CLEAN_QUEUE, _is_rate_limit_exc, run_worker)

LOG = logging.getLogger(__name__)
ENVIRONMENT_CLOUD_TYPE = 'environment'


def _restore_dates_map(raw_dates_map):
    return {
        ca_id: {
            'start_date': datetime.fromtimestamp(dates['start']),
            'end_date': datetime.fromtimestamp(dates['end']),
        }
        for ca_id, dates in raw_dates_map.items()
    }


class CleanWorker(BaseWorker):
    """Worker 3: generates clean expenses and finalises the import."""

    QUEUE_NAME = CLEAN_QUEUE
    SERVICE_NAME = 'diworker-clean'

    def process_task(self, task, config_cl, rest_cl, mongo_cl, clickhouse_cl):
        report_import_id = task['report_import_id']
        with self._active_lock:
            self._active_ids.add(report_import_id)

        _, import_dict = rest_cl.report_import_get(report_import_id)
        cloud_acc_id = import_dict['cloud_account_id']
        _, ca = rest_cl.cloud_account_get(cloud_acc_id)
        previous_attempt_ts = ca.get('last_import_attempt_at', 0)
        start_last_import_ts = ca.get('last_import_at', 0)

        import_dict['import_from'] = task.get('import_from')
        import_dict['import_to'] = task.get('import_to')
        import_dict['reimport'] = task.get('reimport', False)

        importer_params = self.get_importer_params(
            cloud_acc_id, import_dict, config_cl, rest_cl, mongo_cl,
            clickhouse_cl)
        importer_class = get_importer_class(
            ca['type'], ca['config'].get('expense_import_scheme'))

        importer = None
        try:
            importer = importer_class(**importer_params)
            self._restore_importer_state(importer, task)
            self._run(importer, import_dict, ca, task)

            rest_cl.report_import_update(report_import_id, {'state': 'completed'})
            self._maybe_publish_first_import_event(
                rest_cl, ca, start_last_import_ts)
        except Exception as exc:
            if hasattr(exc, 'details'):
                LOG.error('Mongo exception details: %s', exc.details)
            now = int(time.time())
            rest_cl.report_import_update(report_import_id, {
                'state': 'failed', 'state_reason': str(exc)})
            if importer is None:
                importer = BaseReportImporter(
                    **{**importer_params, 'detect_period_start': False})
            importer.update_cloud_import_attempt(now, str(exc))
            self.send_report_failed_email(
                ca, previous_attempt_ts, now,
                is_throttled=_is_rate_limit_exc(exc))
            raise
        return True

    @staticmethod
    def _restore_importer_state(importer, task):
        billing_periods = task.get('billing_periods', [])
        detected_accounts = task.get('detected_accounts', [])
        raw_dates_map = task.get('raw_dates_map', {})
        file_states = task.get('file_states', [])

        if hasattr(importer, 'billing_periods') and billing_periods:
            importer.billing_periods = set(billing_periods)
        if hasattr(importer, 'detected_cloud_accounts') and detected_accounts:
            importer.detected_cloud_accounts = set(detected_accounts)
        if raw_dates_map:
            restored = _restore_dates_map(raw_dates_map)
            importer.imported_raw_dates_map = defaultdict(dict, restored)
        if file_states and hasattr(importer, 'report_cloud_etags'):
            # Restore etag state so _save_one_file_state() works correctly
            for fs in file_states:
                importer.report_cloud_etags[fs['key']] = fs['current_etag']
                importer._previous_file_states[fs['key']] = {
                    'etag': fs['stored_etag']}
        importer_state = task.get('importer_state', {})
        if importer_state:
            importer.restore_serialized_state(importer_state)

    @staticmethod
    def _run(importer, import_dict, ca, task):
        regeneration = task.get('regeneration', False)
        skip_generate = task.get('skip_generate', False)
        file_states = task.get('file_states', [])

        try:
            if not skip_generate:
                LOG.info('Finalizing raw import for %s',
                         import_dict['cloud_account_id'])
                importer.finalize_raw_import()

                LOG.info('Generating clean records for %s',
                         import_dict['cloud_account_id'])
                importer.generate_clean_records(regeneration=regeneration)

                for fs in file_states:
                    importer._save_one_file_state(fs['key'])

            LOG.info('Updating import time')
            importer.update_cloud_import_time(int(time.time()))
            importer.update_cloud_account_config()

            LOG.info('Processing alerts')
            importer.process_alerts()

            LOG.info('Creating traffic/risp tasks')
            importer.create_traffic_processing_tasks()
            importer.create_risp_processing_tasks()
        finally:
            LOG.info('Cleanup')
            importer.cleanup()

    def _maybe_publish_first_import_event(self, rest_cl, ca, start_last_import_ts):
        if start_last_import_ts != 0 or ca['type'] == ENVIRONMENT_CLOUD_TYPE:
            return
        organization_id = ca['organization_id']
        _, resp = rest_cl.cloud_account_list(organization_id)
        all_done = all(
            acc['type'] == ENVIRONMENT_CLOUD_TYPE or acc['last_import_at'] != 0
            for acc in resp['cloud_accounts']
        )
        if all_done:
            self.publish_activities_task(
                organization_id, organization_id, 'organization',
                'report_import_passed', 'organization.report_import.passed')


if __name__ == '__main__':
    run_worker(CleanWorker)
