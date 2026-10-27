#!/usr/bin/env python
import logging
import shutil

from diworker.diworker.importers.base import (
    BaseReportImporter, CSVBaseReportImporter)
from diworker.diworker.importers.factory import get_importer_class
from diworker.diworker.worker_base import (
    BaseWorker, RAW_QUEUE, CLEAN_QUEUE, ORCHESTRATOR_QUEUE, run_worker)

LOG = logging.getLogger(__name__)
ENVIRONMENT_CLOUD_TYPE = 'environment'
MIGRATIONS_READY_FILE = '/tmp/diworker-orchestrator-ready'


class OrchestratorWorker(BaseWorker):
    """Worker 1: validates the import request and routes to raw queue."""

    QUEUE_NAME = ORCHESTRATOR_QUEUE
    SERVICE_NAME = 'diworker'

    @staticmethod
    def setup_worker(config_cl):
        BaseWorker.setup_worker(config_cl)
        with open(MIGRATIONS_READY_FILE, 'w') as f:
            f.write('ready\n')

    @property
    def max_workers(self):
        return 1

    def process_task(self, task, config_cl, rest_cl, mongo_cl, clickhouse_cl):
        report_import_id = task.get('report_import_id')
        if not report_import_id:
            raise ValueError('invalid task: %s' % task)

        _, import_dict = rest_cl.report_import_get(report_import_id)

        cloud_acc_id = import_dict['cloud_account_id']

        active_imports = rest_cl.report_import_list(
            cloud_acc_id, show_active=True)[1]['report_imports']
        conflicts = [x for x in active_imports if x['id'] != report_import_id]
        if conflicts:
            reason = 'Import cancelled due another import: %s' % (
                conflicts[0]['id'])
            self._cancel_import(report_import_id, import_dict, reason,
                                config_cl, rest_cl, mongo_cl)
            return False

        _, ca = rest_cl.cloud_account_get(cloud_acc_id)
        _, org = rest_cl.organization_get(ca['organization_id'])
        if org.get('disabled'):
            reason = ('Import cancelled due to disabled organization: %s'
                      % report_import_id)
            self._cancel_import(report_import_id, import_dict, reason,
                                config_cl, rest_cl, mongo_cl)
            return False

        # added lock for heartbeats. Now we should return true
        with self._active_lock:
            self._active_ids.add(report_import_id)

        rest_cl.report_import_update(report_import_id, {'state': 'in_progress'})

        import_from = task.get('import_from')
        import_to = task.get('import_to')
        reimport = task.get('reimport', False)
        import_dict['import_from'] = import_from
        import_dict['import_to'] = import_to
        import_dict['reimport'] = reimport

        raw_task = {'report_import_id': report_import_id,
                    'recalculate': import_dict.get('is_recalculation', False),
                    'import_from': import_from,
                    'import_to': import_to,
                    'reimport': reimport}

        importer_class = get_importer_class(
            ca['type'], ca['config'].get('expense_import_scheme'))

        if (not import_dict.get('is_recalculation') and
                not import_dict.get('import_file') and
                issubclass(importer_class, CSVBaseReportImporter)):
            importer_params = self.get_importer_params(
                cloud_acc_id, import_dict, config_cl, rest_cl, mongo_cl,
                clickhouse_cl=None)
            importer = None
            try:
                importer = importer_class(**importer_params)
                files = importer.get_files_to_process()
            except Exception as exc:
                if importer is None:
                    importer = BaseReportImporter(
                        **{**importer_params, 'detect_period_start': False})
                self.fail_import(rest_cl, report_import_id, ca, importer, exc)
                raise
            finally:
                if isinstance(importer, CSVBaseReportImporter):
                    shutil.rmtree(importer.reports_dir, ignore_errors=True)
            if not files:
                LOG.info('No changed files for %s, skipping to finalize',
                         report_import_id)
                self.publish(CLEAN_QUEUE, {
                    'report_import_id': report_import_id,
                    'billing_periods': [],
                    'detected_accounts': [cloud_acc_id],
                    'raw_dates_map': {},
                    'file_states': [],
                    'skip_generate': True,
                    'regeneration': False,
                    'import_from': import_from,
                    'import_to': import_to,
                    'reimport': reimport,
                })
                return True
            raw_task['files'] = files

        LOG.info('Routing %s to raw queue', report_import_id)
        self.publish(RAW_QUEUE, raw_task)
        return True

    def _cancel_import(self, report_import_id, import_dict, reason,
                       config_cl, rest_cl, mongo_cl):
        try:
            rest_cl.report_import_update(report_import_id, {
                'state': 'failed', 'state_reason': reason})
        finally:
            if import_dict.get('import_file'):
                importer_params = self.get_importer_params(
                    import_dict['cloud_account_id'], import_dict, config_cl,
                    rest_cl, mongo_cl, clickhouse_cl=None)
                self.remove_import_file(BaseReportImporter(
                    **importer_params, detect_period_start=False))


if __name__ == '__main__':
    run_worker(OrchestratorWorker)
