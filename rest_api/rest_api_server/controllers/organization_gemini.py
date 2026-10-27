import json
import logging
import uuid
from typing import List

import clickhouse_connect
import tools.optscale_time as opttime
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from sqlalchemy import and_, exists, or_

from rest_api.rest_api_server.controllers.base import (
    BaseController, ClickHouseMixin)
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.models.models import (
    OrganizationGemini, GeminiData)
from rest_api.rest_api_server.models.enums import GeminiStatuses
from rest_api.rest_api_server.utils import (
    check_int_attribute, check_dict_attribute, check_list_attribute,
    check_float_attribute
)
from tools.optscale_exceptions.common_exc import (
    NotFoundException, FailedDependency, ForbiddenException, ConflictException)
from rest_api.rest_api_server.exceptions import Err


LOG = logging.getLogger(__name__)


class GeminiController(BaseController):
    """
    Controller for /restapi/v2/geminis/{id}
    """

    def _get_model_type(self):
        return OrganizationGemini

    @staticmethod
    def _validate_stats(**kwargs):
        stats = kwargs.get('stats')
        check_dict_attribute('stats', stats, allow_empty=True)
        if stats:
            for param in ['total_objects', 'filtered_objects',
                          'duplicated_objects']:
                value = stats.get(param)
                if value is not None:
                    check_int_attribute(param, value, check_length=False)
            for param in ['total_size', 'duplicates_size', 'monthly_savings']:
                value = stats.get(param)
                if value is not None:
                    check_float_attribute(param, value, check_length=False)

    def edit(self, item_id, **kwargs):
        self._validate_stats(**kwargs)
        stats = kwargs.get('stats')
        if stats:
            kwargs['stats'] = json.dumps(stats)
        return super().edit(item_id, **kwargs)


class GeminiAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return GeminiController


class GeminiDataController(BaseController, ClickHouseMixin):
    """
    Controller for /restapi/v2/geminis/{id}/data
    """
    EXCHANGE_NAME = 'gemini-tasks'
    ROUTING_KEY = 'gemini-data'
    RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                    'interval_step': 1, 'interval_max': 3}

    def _get_model_type(self):
        return GeminiData

    @property
    def clickhouse_client(self):
        if not self._clickhouse_client:
            user, password, host, _, port, secure = (
                self._config.clickhouse_params())
            self._clickhouse_client = clickhouse_connect.get_client(
                host=host, password=password, database="gemini", user=user,
                port=port, secure=secure)
        return self._clickhouse_client

    @staticmethod
    def _generate_string_from_buckets(buckets: list[str]) -> str:
        return ",".join(buckets)

    def publish_task(self, task_params):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self._config.read_branch('/rabbit')),
            transport_options=self.RETRY_POLICY)

        task_exchange = Exchange(self.EXCHANGE_NAME, type='direct')
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                task_params,
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=self.ROUTING_KEY,
                retry=True,
                retry_policy=self.RETRY_POLICY,
            )

    def create(self, gemini_id: str, buckets: list) -> GeminiData:
        org_gemini = self.session.query(OrganizationGemini).filter(
            OrganizationGemini.id == gemini_id,
            OrganizationGemini.deleted.is_(False)
        ).one_or_none()
        if not org_gemini:
            raise NotFoundException(
                Err.OE0002, [OrganizationGemini.__name__, gemini_id])
        if org_gemini.status != GeminiStatuses.SUCCESS:
            raise FailedDependency(Err.OE0572, [org_gemini.status.value])
        now_ts = opttime.utcnow_timestamp()
        unique_buckets = list(dict.fromkeys(buckets))
        buckets_str = self._generate_string_from_buckets(unique_buckets)
        existing_id = self.session.query(GeminiData.id).filter(
            self.model_type.gemini_id == gemini_id,
            self.model_type.deleted.is_(False),
            or_(
                self.model_type.valid_until > now_ts,
                self.model_type.valid_until == 0,
            ),
            self.model_type.buckets == buckets_str,
            self.model_type.status != GeminiStatuses.FAILED
        ).scalar()
        if existing_id:
            raise ConflictException(
                Err.OE0573, [self.model_type.__name__, existing_id])
        try:
            gemini_data_id = str(uuid.uuid4())
            gemini_data = GeminiData(id=gemini_data_id, gemini_id=gemini_id,
                                     buckets=buckets_str)
            self.session.add(gemini_data)
            self.session.commit()
            self.publish_task({'gemini_data_id': gemini_data_id})
        except Exception:
            self.session.rollback()
            raise
        return gemini_data

    def list(self, gemini_id, only_active=False, **kwargs) -> List[GeminiData]:
        query = self.session.query(self.model_type).filter(
            self.model_type.gemini_id == gemini_id,
            self.model_type.deleted_at.is_(False)
        )
        if only_active:
            now_ts = opttime.utcnow_timestamp()
            query = query.filter(
                or_(
                    self.model_type.valid_until > now_ts,
                    self.model_type.valid_until == 0,
                ),
                self.model_type.status != GeminiStatuses.FAILED
            )
        return query.all()

    def get(self, gemini_data_id, **kwargs) -> GeminiData:
        gemini_data = super().get(gemini_data_id, **kwargs)
        if not gemini_data:
            raise NotFoundException(
                Err.OE0002, [GeminiData.__name__, gemini_data_id])
        return gemini_data

    def get_download_url(self, gemini_data_id: str, **kwargs):
        gemini_data = self.get(gemini_data_id, **kwargs)
        if gemini_data.status != GeminiStatuses.SUCCESS:
            raise FailedDependency(Err.OE0572, [gemini_data.status.value])
        url = gemini_data.url
        if not url or gemini_data.valid_until < opttime.utcnow_timestamp():
            raise ForbiddenException(Err.OE0234, [])
        return url


class GeminiDataAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return GeminiDataController


class OrganizationGeminiController(BaseController):
    """
    Controller for /restapi/v2/organizations/{id}/geminis and /restapi/v2/geminis
    """

    def _get_model_type(self):
        return OrganizationGemini

    def list(self, organization_id: str = None, **kwargs) -> List[OrganizationGemini]:
        if organization_id:
            return super().list(organization_id=organization_id)
        else:
            return super().list()

    def _validate_filters(self, filters):
        check_dict_attribute('filters', filters, allow_empty=True)
        if filters:
            if 'buckets' in filters:
                check_list_attribute('buckets', filters['buckets'])
            if 'min_size' in filters:
                check_int_attribute('min_size', filters['min_size'])

    def create(self, organization_id: str, filters: dict) -> OrganizationGemini:
        self._validate_filters(filters)
        return super().create(organization_id=organization_id,
                              filters=json.dumps(filters))

    def delete_for_org(self, organization_id) -> None:
        geminis = self.list(organization_id)
        for gemini in geminis:
            self.delete(gemini.id)


class OrganizationGeminiAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self) -> type:
        return OrganizationGeminiController
