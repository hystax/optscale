import json
import uuid
import logging

from sqlalchemy import and_
from cloud_adapter.model import ResourceTypes, RES_MODEL_MAP
from rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api_server.controllers.organization import OrganizationController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from rest_api_server.models.enums import CloudTypes
from rest_api_server.models.models import (CloudAccount, Employee, Pool,
                                           Organization, DiscoveryInfo,
                                           ClusterType)
from rest_api_server.utils import encoded_tags, is_uuid
from optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)
from cloud_adapter.cloud import Cloud as CloudAdapter
import cloud_adapter.model as ca_model


LOG = logging.getLogger(__name__)
ALLOWED_FILTERS = ('region', 'pool_id', 'owner_id',
                   'cloud_account_id')
NONE_SORT_FALLBACK = 'zzzzzzzzz'


class CloudResourceDiscover(BaseController, MongoMixin):

    def _check_organization(self, organization_id):
        organization = OrganizationController(self.session,
                                              self._config).get(organization_id)
        if organization is None:
            raise NotFoundException(Err.OE0002, [Organization.__name__,
                                                 organization_id])

    def get_pools_dict(self, organization_id):
        """
        Gets pools dict
        :param organization_id: str
        :return: dict(dict)
        example
        {
          "d9770e24-f11d-4498-9d78-d70890b3ec03":{
          "n":"Cool Corp."
        },
        "36745fcd-4e0f-4e43-9cc2-6b6b430e1158":{
          "n":"Cool Corp2"
          }
        }
        """
        result = self.session.query(
            Pool.id, Pool.purpose, Pool.name
        ).filter(
            Pool.deleted.is_(False),
            Pool.organization_id == organization_id
        ).all()
        pools = dict()
        for i in result:
            pool_id, pool_p, name = i
            pools[pool_id] = {
                'name': name,
                'purpose': pool_p.value
            }
        return pools

    def get_owners_dict(self, organization_id):
        """
        Gets owners dict
        :param organization_id: org id
        :return: dict({"owner_id": "name"))
        """
        owners = dict()
        pers = self.session.query(Employee.id, Employee.name).filter(
            and_(
                Employee.organization_id == organization_id,
                Employee.deleted.is_(False)
            )
        ).all()
        for i in pers:
            id_, name = i
            owners[id_] = name
        return owners

    def get_active_resources(self, discovery_infos, resource_type):
        cloud_account_last_discovery_map = {
            di.cloud_account_id: di.last_discovery_at
            for di in discovery_infos if di.last_discovery_at > 0}
        if not cloud_account_last_discovery_map:
            return {}
        query = [
            {'cloud_account_id': {
                '$in': list(cloud_account_last_discovery_map.keys())}},
            {'resource_type': resource_type},
            {'active': True}
        ]
        return self.get_resources(query, cloud_account_last_discovery_map)

    def get_resources(self, filters, cloud_account_last_discovery_map=None):
        result = dict()
        resources = self.resources_collection.aggregate(
            [{'$match': {'$and': filters}}])
        for resource in resources:
            cloud_account_id = resource.get('cloud_account_id')
            last_seen = resource.get('last_seen')
            last_discovery_at = (cloud_account_last_discovery_map or {}).get(
                cloud_account_id)
            if last_discovery_at and last_seen < last_discovery_at:
                continue
            if 'tags' in resource:
                resource['tags'] = encoded_tags(resource['tags'], decode=True)
            result[resource['cloud_resource_id']] = resource
        return result

    def _join_db_info(self, resources, db_resource_map, organization_id, cloud_acc_map):
        """
        Joins Cloud Output & Database data
        :param resources: (ref list) reference to the resources list
        :param organization_id: str
        :return: None
        """
        pools_dict = self.get_pools_dict(organization_id)
        owners_dict = self.get_owners_dict(organization_id)
        resource_type_status_date_fields = {
            ca_model.VolumeResource: ('attached', 'last_attached'),
            ca_model.InstanceResource: ('stopped_allocated', 'last_seen_not_stopped'),
            ca_model.IpAddressResource: ('available', 'last_used')
        }
        for res in resources:
            db_resource = db_resource_map.get(res.cloud_resource_id)
            if db_resource:
                res.resource_id = db_resource.get('_id')
                res.pool_id = db_resource.get('pool_id')
                res.owner_id = db_resource.get('employee_id')
                if res.tags is None:
                    res.tags = db_resource.get('tags')
                cloud_acc = cloud_acc_map.get(
                    db_resource.get('cloud_account_id'))
                if cloud_acc:
                    res.cloud_account_name = cloud_acc.name
                resource_obj_type = type(res)
                status_date_set = resource_type_status_date_fields.get(resource_obj_type)
                if status_date_set:
                    status_field, date_field = status_date_set
                    self._set_resource_status_date_fields(
                        res, db_resource, status_field, date_field)
            else:
                res.resource_id = str(uuid.uuid4())
            if res.pool_id:
                pool = pools_dict.get(res.pool_id)
                if pool:
                    res.pool_name = pool['name']
                    res.pool_purpose = pool['purpose']
                if res.owner_id:
                    owner_name = owners_dict.get(res.owner_id)
                    if owner_name:
                        res.owner_name = owner_name

        return resources

    @staticmethod
    def _set_resource_status_date_fields(resource, resource_info, status_field, date_field):
        meta = resource_info.get('meta') or {}
        setattr(resource, status_field, meta.get(status_field, False))
        setattr(resource, date_field, meta.get(date_field, 0))

    @staticmethod
    def check_filters(filters):
        if not filters:
            return
        if not(isinstance(filters, dict)):
            raise WrongArgumentsException(Err.OE0392, [])
        invalid_filters = list(filter(lambda x: x not in ALLOWED_FILTERS,
                                      filters.keys()))
        if invalid_filters:
            msg = ','.join(invalid_filters)
            raise WrongArgumentsException(Err.OE0390, [msg])
        for k, v in filters.items():
            if not isinstance(v, list):
                raise WrongArgumentsException(Err.OE0393, [k])

    @staticmethod
    def apply_filter(resources, filters):
        for k, v in filters.items():
            resources = list(filter(lambda x: getattr(x, k) in v, resources))
        return resources

    @staticmethod
    def check_sort(res_type, sort, is_cluster_type=False):
        if not sort:
            return
        if not isinstance(sort, dict):
            raise WrongArgumentsException(Err.OE0394, [])
        if len(sort) > 1:
            raise WrongArgumentsException(Err.OE0395, [])
        field, order = next(iter(sort.items()))
        if is_cluster_type:
            fields = ca_model.CloudResource().fields()
        else:
            fields = RES_MODEL_MAP[res_type.name]().fields()
        if field not in fields:
            msg = ', '.join(fields)
            resource_type = 'Cluster' if is_cluster_type else res_type.value
            raise WrongArgumentsException(Err.OE0389, [field, resource_type, msg])
        if order not in ['asc', 'desc']:
            raise WrongArgumentsException(Err.OE0399, [])

    @staticmethod
    def sorter(x, field):
        sort = getattr(x, field)
        if sort is not None:
            if isinstance(sort, str):
                sort = sort.lower()
        else:
            sort = NONE_SORT_FALLBACK
        return sort

    def apply_sort(self, resources, sort):
        if sort:
            field, order = next(iter(sort.items()))
            if order in ['asc']:
                resources.sort(key=lambda x: self.sorter(x, field))
            else:
                resources.sort(key=lambda x: self.sorter(x, field),
                               reverse=True)
        return resources

    @staticmethod
    def try_load(param, type_):
        try:
            dict_ = json.loads(param)
            return dict_
        except (json.JSONDecodeError, TypeError):
            raise WrongArgumentsException(Err.OE0398, [type_])

    def try_load_from_cache(self, organization_id, resource_type, filters,
                            sort, cloud_type):
        result = []
        model = RES_MODEL_MAP[resource_type.name]
        discovery_infos_q = self.session.query(
            DiscoveryInfo, CloudAccount
        ).join(
            CloudAccount, and_(
                CloudAccount.id == DiscoveryInfo.cloud_account_id,
                CloudAccount.deleted.is_(False)
            )
        ).filter(
            CloudAccount.organization_id == organization_id,
            DiscoveryInfo.deleted.is_(False),
            DiscoveryInfo.resource_type == resource_type
        )
        if cloud_type:
            discovery_infos_q = discovery_infos_q.filter(
                CloudAccount.type == CloudTypes(cloud_type)
            )
        discovery_info_and_ca = discovery_infos_q.all()
        discovery_infos = []
        cloud_acc_map = {}
        for di, ca in discovery_info_and_ca:
            discovery_infos.append(di)
            cloud_acc_map[ca.id] = ca

        cached_resources_map = self.get_active_resources(
            discovery_infos, resource_type.value)
        for item in cached_resources_map.values():
            res_obj = model()
            for i in res_obj.fields():
                if item.get(i):
                    if i == 'meta':
                        for k, v in item[i].items():
                            setattr(res_obj, k, v)
                        continue
                    setattr(res_obj, i, item[i])
            result.append(res_obj)
        self._join_db_info(result, cached_resources_map, organization_id, cloud_acc_map)
        result = self.apply_filter(result, filters)
        self.apply_sort(result, sort)
        return result

    def get_clusters(self, resource_type, filters, sort):
        result = []
        query = [
            {'resource_type': resource_type},
            {'active': True},
            {'deleted_at': 0}
        ]
        cached_resources_map = self.get_resources(query)
        for item in cached_resources_map.values():
            res_obj = ca_model.CloudResource()
            for i in res_obj.fields():
                if item.get(i):
                    if i == 'meta':
                        continue
                    setattr(res_obj, i, item[i])
            setattr(res_obj, 'resource_id', item['_id'])
            result.append(res_obj)
        result = self.apply_filter(result, filters)
        self.apply_sort(result, sort)
        return result

    def get_cluster_type(self, cluster_type_id, org_id):
        if is_uuid(cluster_type_id):
            cluster_type = self.session.query(ClusterType).filter(
                ClusterType.organization_id == org_id,
                ClusterType.id == cluster_type_id,
                ClusterType.deleted.is_(False)
            ).one_or_none()
            if not cluster_type:
                raise WrongArgumentsException(Err.OE0467, [cluster_type_id])
            return cluster_type
        else:
            return None

    def list(self, organization_id, **kwargs):
        res_type = kwargs.get('type')
        cloud_type = kwargs.get('cloud_type')
        if cloud_type:
            try:
                CloudAdapter.get_adapter_type(cloud_type)
            except ValueError:
                raise WrongArgumentsException(Err.OE0436, [cloud_type])
        self._check_organization(organization_id)
        if not res_type:
            raise WrongArgumentsException(Err.OE0397, [])
        resource_type = res_type.lower()
        filters = self.try_load(kwargs.get('filters'), 'filters')
        sort = self.try_load(kwargs.get('sort'), 'sort')
        self.check_filters(filters)
        cluster_type = self.get_cluster_type(res_type, organization_id)
        if cluster_type:
            self.check_sort(cluster_type.name, sort, True)
            resources = self.get_clusters(cluster_type.name, filters, sort)
        else:
            if resource_type not in ResourceTypes.__members__:
                raise WrongArgumentsException(Err.OE0384, [res_type])
            resource_type = ResourceTypes[resource_type]
            self.check_sort(resource_type, sort)
            resources = self.try_load_from_cache(
                organization_id, resource_type, filters, sort, cloud_type)
        return {'from_cache': True,
                'data': [x.to_dict() for x in resources]}


class CloudResourceDiscoverAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CloudResourceDiscover
