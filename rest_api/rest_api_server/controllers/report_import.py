import logging
import uuid
from sqlalchemy import and_, true, or_, exists
from datetime import datetime
import boto3
from tools.optscale_exceptions.common_exc import (
    NotFoundException, FailedDependency, WrongArgumentsException
)
from boto3.session import Config as BotoConfig
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from tools.cloud_adapter.cloud import Cloud as CloudAdapter

from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import ImportStates, CloudTypes
from rest_api.rest_api_server.models.models import (ReportImport, CloudAccount,
                                                    Organization)
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.checklist import ChecklistController
from rest_api.rest_api_server.utils import (raise_unexpected_exception,
                                            check_int_attribute)

ACTIVE_IMPORT_THRESHOLD = 1800  # 30 min
NOT_PROCESSED_REPORT_THRESHOLD = 10800  # 3 hrs
LOG = logging.getLogger(__name__)


class ReportImportBaseController(BaseController):
    def _get_model_type(self):
        return ReportImport

    REPORT_IMPORT_QUEUE = 'report-imports'
    RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                    'interval_step': 1, 'interval_max': 3}

    def create(self, cloud_account_id, import_file=None, recalculate=False, priority=1):
        report_import = super().create(
            cloud_account_id=cloud_account_id,
            import_file=import_file,
            is_recalculation=recalculate
        )
        self.publish_task({'report_import_id': report_import.id}, priority)
        if recalculate:
            self._publish_report_import_activity(
                report_import, 'recalculation_started')
        return report_import

    def check_unprocessed_imports(self, cloud_account_id):
        dt = datetime.utcnow().timestamp()
        scheduled_threshold = dt - NOT_PROCESSED_REPORT_THRESHOLD
        active_threshold = dt - ACTIVE_IMPORT_THRESHOLD
        return self.session.query(
            exists().where(and_(
                ReportImport.cloud_account_id == cloud_account_id,
                ReportImport.deleted_at.is_(False),
                or_(
                    and_(
                        ReportImport.state == ImportStates.SCHEDULED,
                        ReportImport.created_at >= scheduled_threshold
                    ),
                    and_(
                        ReportImport.state == ImportStates.IN_PROGRESS,
                        ReportImport.updated_at >= active_threshold
                    )
                )
            ))
        ).scalar()

    def _publish_report_import_activity(self, report_import, action,
                                        level='INFO', error_reason=None):
        cloud_account = report_import.cloud_account
        meta = {
            'object_name': cloud_account.name,
            'cloud_account_id': cloud_account.id,
            'level': level
        }
        if error_reason:
            meta.update({'error_reason': error_reason})
        self.publish_activities_task(
            cloud_account.organization_id, report_import.id, 'report_import',
            action, meta, 'report_import.{action}'.format(action=action),
            add_token=True)

    def is_initial_completed_report(self, updated_report):
        completed_import = self.session.query(ReportImport).filter(
            and_(
                ReportImport.cloud_account_id == updated_report.cloud_account_id,
                ReportImport.state == ImportStates.COMPLETED,
                ReportImport.deleted.is_(False)
            )
        ).order_by(ReportImport.created_at).first()
        return completed_import and completed_import.id == updated_report.id

    def edit(self, item_id, **kwargs):
        kwargs['updated_at'] = int(datetime.utcnow().timestamp())
        updated_report = super().edit(item_id, **kwargs)
        state = kwargs.get('state')
        if updated_report.is_recalculation:
            if state == ImportStates.COMPLETED.value:
                self._publish_report_import_activity(updated_report,
                                                     'recalculation_completed')
            if state == ImportStates.FAILED.value:
                error_reason = kwargs.get('state_reason', '')
                self._publish_report_import_activity(
                    updated_report, 'recalculation_failed',
                    error_reason=error_reason, level='ERROR')
            return updated_report

        if state == ImportStates.COMPLETED.value:
            is_initial_report = self.is_initial_completed_report(
                updated_report)
            if is_initial_report:
                LOG.info('Scheduling checklist run')
                ChecklistController(
                    self.session, self._config, self.token).schedule_next_run(
                    updated_report.cloud_account.organization_id)
            if is_initial_report or updated_report.import_file:
                self._publish_report_import_activity(
                    updated_report, 'report_import_completed')
        elif state == ImportStates.FAILED.value:
            error_reason = kwargs.get('state_reason', '')
            self._publish_report_import_activity(
                updated_report, 'report_import_failed',
                error_reason=error_reason, level='ERROR')
        return updated_report

    def publish_task(self, task_params, priority=1):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self._config.read_branch('/rabbit')),
            transport_options=self.RETRY_POLICY)

        task_exchange = Exchange('billing-reports', type='direct')
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                task_params,
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=self.REPORT_IMPORT_QUEUE,
                retry=True,
                retry_policy=self.RETRY_POLICY,
                priority=priority,
            )


class ReportImportScheduleController(ReportImportBaseController):

    def _get_cloud_accounts(self, import_period, org_id,
                            cloud_account_id, cloud_account_type):
        org_subq = self.session.query(Organization.id).filter(
            Organization.deleted.is_(False)
        ).subquery()

        if import_period is not None:
            q = self.session.query(CloudAccount).filter(
                CloudAccount.organization_id.in_(org_subq),
                CloudAccount.deleted.is_(False),
                CloudAccount.auto_import == true(),
                CloudAccount.import_period == import_period,
            )
        else:
            q = self.session.query(CloudAccount).filter(
                or_(
                    CloudAccount.id == cloud_account_id,
                    CloudAccount.organization_id == org_id
                ),
                # ignoring auto import, because starting with this params only manually
                CloudAccount.deleted.is_(False),
                CloudAccount.organization_id.in_(org_subq),
            )
            if cloud_account_type:
                q = q.filter(CloudAccount.type == cloud_account_type)
        res = q.all()
        return res

    @staticmethod
    def _check_args(org_id,
                    cloud_account_id,
                    cloud_account_type,
                    priority):
        if org_id and cloud_account_id:
            raise WrongArgumentsException(
                Err.OE0528, []
            )
        if cloud_account_type and not org_id:
            raise WrongArgumentsException(
                Err.OE0529, []
            )
        if priority is not None and priority not in range(1, 10):
            raise WrongArgumentsException(Err.OE0530, [])
        if cloud_account_type is not None:
            try:
                CloudTypes(cloud_account_type)
            except ValueError:
                raise WrongArgumentsException(Err.OE0533, [cloud_account_type])

    def schedule(self, **kwargs):
        period = kwargs.pop('period', None)
        organization_id = kwargs.pop("organization_id", None)
        cloud_account_type = kwargs.pop("cloud_account_type", None)
        cloud_account_id = kwargs.pop("cloud_account_id", None)
        priority = kwargs.pop("priority", 1)
        if period is not None:
            # if import period is set there should be no other parameters
            if (organization_id is not None or
                    cloud_account_id is not None or
                    cloud_account_type is not None):
                raise WrongArgumentsException(Err.OE0531, [])
            check_int_attribute('period', period)
        if period is None and organization_id is None and cloud_account_id is None:
            raise WrongArgumentsException(Err.OE0532, [])
        if kwargs:
            raise_unexpected_exception(kwargs.keys())
        self._check_args(
            organization_id, cloud_account_id, cloud_account_type, priority)
        if cloud_account_type is not None:
            cloud_account_type = CloudTypes(cloud_account_type)

        cloud_accounts = self._get_cloud_accounts(
            period, organization_id, cloud_account_id, cloud_account_type)

        result = []
        for ca in cloud_accounts:
            if ca.type == CloudTypes.AWS_CNR:
                decoded_cfg = ca.decoded_config
                if decoded_cfg.get('linked', False):
                    continue
            if not self.check_unprocessed_imports(ca.id):
                result.append(self.create(ca.id, priority=priority))
        return result


class ExpensesRecalculationScheduleController(ReportImportBaseController):
    def schedule(self, cloud_account_id):
        cloud_acc = self.session.query(CloudAccount).filter(
            CloudAccount.deleted.is_(False),
            CloudAccount.type.in_([
                CloudTypes.KUBERNETES_CNR, CloudTypes.ENVIRONMENT,
                CloudTypes.DATABRICKS]),
            CloudAccount.id == cloud_account_id
        ).one_or_none()

        if cloud_acc:
            return self.create(cloud_acc.id, recalculate=True)


class ReportImportFileController(ReportImportBaseController):
    BUCKET_NAME = 'report-imports'
    MAX_BUFFER_SIZE = 5 * 1024 * 1024

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 1
        self.buffer = bytes()
        self._s3_client = None
        self.filename = str(uuid.uuid4())
        self.parts = []
        self.mpu_id = None

    @property
    def s3_client(self):
        if self._s3_client is None:
            s3_params = self._config.read_branch('/minio')
            self._s3_client = boto3.client(
                's3',
                endpoint_url='http://{}:{}'.format(
                    s3_params['host'], s3_params['port']),
                aws_access_key_id=s3_params['access'],
                aws_secret_access_key=s3_params['secret'],
                config=BotoConfig(s3={'addressing_style': 'path'})
            )
            try:
                self._s3_client.create_bucket(Bucket=self.BUCKET_NAME)
            except self._s3_client.exceptions.BucketAlreadyOwnedByYou:
                pass
        return self._s3_client

    def initialize_upload(self, cloud_account_id):
        cloud_acc = self.get_cloud_account(cloud_account_id)
        if cloud_acc is None:
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, cloud_account_id])
        adapter_cls = CloudAdapter.get_adapter_type(cloud_acc.type.value)
        if not adapter_cls or not adapter_cls.SUPPORTS_REPORT_UPLOAD:
            raise FailedDependency(Err.OE0434, [cloud_acc.type.value])
        mpu = self.s3_client.create_multipart_upload(Bucket=self.BUCKET_NAME,
                                                     Key=self.filename)
        self.mpu_id = mpu['UploadId']

    def add_chunk(self, chunk):
        self.buffer += chunk
        if len(self.buffer) >= self.MAX_BUFFER_SIZE:
            self.flush_buffer()

    def flush_buffer(self):
        part = self.s3_client.upload_part(
            Body=self.buffer,
            Bucket=self.BUCKET_NAME,
            Key=self.filename,
            UploadId=self.mpu_id,
            PartNumber=self.count,
        )
        self.parts.append({'PartNumber': self.count, 'ETag': part['ETag']})
        self.count += 1
        self.buffer = bytes()

    def get_cloud_account(self, cloud_account_id):
        data_set = self.session.query(
            CloudAccount, Organization
        ).outerjoin(Organization, and_(
            Organization.id == CloudAccount.organization_id,
            Organization.deleted.is_(False)
        )).filter(and_(
            CloudAccount.id == cloud_account_id,
            CloudAccount.deleted.is_(False)
        )).one_or_none()
        if data_set:
            cloud_acc, org = data_set
            if cloud_acc and not org:
                raise NotFoundException(
                    Err.OE0005, [Organization.__name__, cloud_acc.organization_id])

            return cloud_acc

    def _validate(self, item, is_new=True, **kwargs):
        self.check_cloud_account(item.cloud_account_id)

    def complete_upload(self, cloud_account_id):
        if len(self.buffer) != 0:
            self.flush_buffer()
        self.s3_client.complete_multipart_upload(
            Bucket=self.BUCKET_NAME,
            Key=self.filename,
            UploadId=self.mpu_id,
            MultipartUpload={'Parts': self.parts},
        )
        report_import = self.create(
            cloud_account_id=cloud_account_id,
            import_file='{}/{}'.format(self.BUCKET_NAME, self.filename)
        )
        return report_import

    def list(self, cloud_account_id, show_completed=False, show_active=False):
        self.check_cloud_account(cloud_account_id)
        query = self.session.query(self.model_type).filter(
            self.model_type.deleted_at.is_(False),
            self.model_type.cloud_account_id == cloud_account_id,
        )
        if not show_completed:
            query = query.filter(
                self.model_type.state != ImportStates.COMPLETED
            )
        if show_active:
            ts = datetime.utcnow().timestamp() - ACTIVE_IMPORT_THRESHOLD
            query = query.filter(
                self.model_type.state == ImportStates.IN_PROGRESS,
                self.model_type.updated_at >= ts
            )
        return query.all()

    def get(self, item_id, **kwargs):
        report = super().get(item_id, **kwargs)
        if report:
            self.check_cloud_account(report.cloud_account_id)
        return report

    def check_cloud_account(self, cloud_account_id):
        cc = self.get_cloud_account(cloud_account_id)
        if cc is None:
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, cloud_account_id])


class ReportImportAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ReportImportFileController


class ReportImportScheduleAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ReportImportScheduleController
