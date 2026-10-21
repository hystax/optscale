#!/usr/bin/env python
import logging
import shutil
from contextlib import nullcontext

from diworker.diworker.importers.base import (
    CSVBaseReportImporter, _get_throttle_semaphore)
from diworker.diworker.importers.factory import get_importer_class
from diworker.diworker.worker_base import (
    BaseWorker, RAW_QUEUE, CLEAN_QUEUE, run_worker)

LOG = logging.getLogger(__name__)


def _serialize_dates_map(dates_map):
    return {
        ca_id: {
            'start': int(dates['start_date'].timestamp()),
            'end': int(dates['end_date'].timestamp()),
        }
        for ca_id, dates in dates_map.items()
    }


def _merge_dates_map(base, new_serialized):
    result = dict(base)
    for ca_id, dates in new_serialized.items():
        if ca_id not in result:
            result[ca_id] = dates
        else:
            result[ca_id] = {
                'start': min(result[ca_id]['start'], dates['start']),
                'end': max(result[ca_id]['end'], dates['end']),
            }
    return result


class RawWorker(BaseWorker):
    """Worker 2: downloads one file and imports raw expenses."""

    QUEUE_NAME = RAW_QUEUE
    SERVICE_NAME = 'diworker-raw'

    def process_task(self, task, config_cl, rest_cl, mongo_cl, clickhouse_cl):
        report_import_id = task['report_import_id']
        recalculate = task.get('recalculate', False)
        with self._active_lock:
            self._active_ids.add(report_import_id)

        _, import_dict = rest_cl.report_import_get(report_import_id)
        cloud_acc_id = import_dict['cloud_account_id']
        _, ca = rest_cl.cloud_account_get(cloud_acc_id)

        import_dict['import_from'] = task.get('import_from')
        import_dict['import_to'] = task.get('import_to')
        import_dict['reimport'] = task.get('reimport', False)

        importer_params = self.get_importer_params(
            cloud_acc_id, import_dict, config_cl, rest_cl, mongo_cl,
            clickhouse_cl)
        importer_class = get_importer_class(
            ca['type'], ca['config'].get('expense_import_scheme'))
        importer = importer_class(**importer_params)

        parent_id = ca.get('parent_id')
        throttle = (
            _get_throttle_semaphore(parent_id,
                                    importer_params['max_tenant_concurrent'])
            if parent_id else nullcontext()
        )

        try:
            with throttle:
                self._run(task, importer, cloud_acc_id, recalculate)
        except Exception as exc:
            self.fail_import(rest_cl, report_import_id, ca, importer, exc)
            raise
        return True

    def _run(self, task, importer, cloud_acc_id, recalculate):
        report_import_id = task['report_import_id']
        files = task.get('files')  # None → API-based; list → file-based

        if recalculate and not isinstance(importer, CSVBaseReportImporter):
            # CSV importers ignore recalculate in their data_import(); only
            # non-CSV importers (Kubernetes, Environment, Databricks, etc.)
            # implement recalculate_raw_expenses().
            LOG.info('Recalculating raw for %s', report_import_id)
            importer.recalculate_raw_expenses()
            self.publish(CLEAN_QUEUE, {
                'report_import_id': report_import_id,
                'billing_periods': [],
                'detected_accounts': [cloud_acc_id],
                'raw_dates_map': {},
                'file_states': [],
                'importer_state': importer.get_state_to_serialize(),
                'regeneration': True,
                'import_from': task.get('import_from'),
                'import_to': task.get('import_to'),
                'reimport': task.get('reimport', False),
            })
            return

        if files is not None:
            self._run_file_based(task, importer, cloud_acc_id, files)
        else:
            self._run_api_based(task, importer, cloud_acc_id)

    def _run_file_based(self, task, importer, cloud_acc_id, files):
        report_import_id = task['report_import_id']
        acc_billing_periods = set(task.get('billing_periods', []))
        acc_detected_accounts = set(task.get('detected_accounts', [cloud_acc_id]))
        acc_raw_dates_map = task.get('raw_dates_map', {})
        acc_file_states = list(task.get('file_states', []))

        current_file = files[0]
        remaining = files[1:]

        LOG.info('Importing file %s for %s (%d remaining)',
                 current_file['report'].get('Key') or current_file['report'].get('name'),
                 report_import_id, len(remaining))

        try:
            account_id_ca_id_map = importer.get_linked_account_map()
            report_path = importer.prepare_one_file(
                current_file['date'], current_file['report'])
            report_key = importer.report_file_keys.get(report_path)
            importer.load_report(report_path, account_id_ca_id_map,
                                 report_key=report_key)
            importer.finalize_raw_import(report_key, is_last=not remaining)
            if report_key:
                acc_file_states.append({
                    'key': report_key,
                    'current_etag': importer.report_cloud_etags.get(report_key, ''),
                    'stored_etag': current_file.get('stored_etag', ''),
                })
        finally:
            shutil.rmtree(importer.reports_dir, ignore_errors=True)

        acc_billing_periods |= importer.billing_periods
        acc_detected_accounts |= importer.detected_cloud_accounts
        acc_raw_dates_map = _merge_dates_map(
            acc_raw_dates_map,
            _serialize_dates_map(importer.imported_raw_dates_map))

        if remaining:
            self.publish(RAW_QUEUE, {
                'report_import_id': report_import_id,
                'files': remaining,
                'billing_periods': list(acc_billing_periods),
                'detected_accounts': list(acc_detected_accounts),
                'raw_dates_map': acc_raw_dates_map,
                'file_states': acc_file_states,
                'import_from': task.get('import_from'),
                'import_to': task.get('import_to'),
                'reimport': task.get('reimport', False),
            }, priority=5)
        else:
            self.publish(CLEAN_QUEUE, {
                'report_import_id': report_import_id,
                'billing_periods': list(acc_billing_periods),
                'detected_accounts': list(acc_detected_accounts),
                'raw_dates_map': acc_raw_dates_map,
                'file_states': acc_file_states,
                'regeneration': False,
                'import_from': task.get('import_from'),
                'import_to': task.get('import_to'),
                'reimport': task.get('reimport', False),
            })

    def _run_api_based(self, task, importer, cloud_acc_id):
        report_import_id = task['report_import_id']
        LOG.info('Importing via API/manual for %s', report_import_id)
        is_csv = isinstance(importer, CSVBaseReportImporter)
        try:
            importer.prepare()
            importer.load_raw_data()
            importer.finalize_raw_import()
        finally:
            if is_csv:
                shutil.rmtree(importer.reports_dir, ignore_errors=True)
        billing_periods = list(getattr(importer, 'billing_periods', set()))
        detected_accounts = list(
            getattr(importer, 'detected_cloud_accounts', {cloud_acc_id}))
        self.publish(CLEAN_QUEUE, {
            'report_import_id': report_import_id,
            'billing_periods': billing_periods,
            'detected_accounts': detected_accounts,
            'raw_dates_map': _serialize_dates_map(importer.imported_raw_dates_map),
            'file_states': [],
            'importer_state': importer.get_state_to_serialize(),
            'regeneration': False,
            'import_from': task.get('import_from'),
            'import_to': task.get('import_to'),
            'reimport': task.get('reimport', False),
        })


if __name__ == '__main__':
    run_worker(RawWorker)
