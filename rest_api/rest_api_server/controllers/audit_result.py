import boto3
from sqlalchemy import exists, and_
from rest_api.rest_api_server.models.models import Organization
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from tools.optscale_exceptions.common_exc import NotFoundException
from rest_api.rest_api_server.exceptions import Err
from botocore.exceptions import ClientError as BotoCoreClientError
from boto3.session import Config as BotoConfig

BUCKET_NAME = 'audit-results'


class AuditResultController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._s3_client = None

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
        return self._s3_client

    def _is_organization_exists(self, organization_id):
        return self.session.query(
            exists().where(and_(
                Organization.id == organization_id,
                Organization.deleted.is_(False)
            ))
        ).scalar()

    def download_audit_result(self, organization_id, audit_id):
        if not self._is_organization_exists(organization_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        try:
            result = self._get_s3_audit_result(organization_id, audit_id)
            return result['Body'].read()
        except BotoCoreClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                raise NotFoundException(Err.OE0002, ['Audit', audit_id])
            raise

    def _get_s3_audit_result(self, organization_id, audit_id):
        return self.s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key='%s/%s.bin' % (organization_id, audit_id)
        )


class AuditResultAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AuditResultController
