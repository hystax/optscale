import logging

from collections import defaultdict
from sqlalchemy import and_, exists

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Organization
from rest_api.rest_api_server.controllers.base import BaseController, MongoMixin

from tools.optscale_exceptions.common_exc import NotFoundException


LOG = logging.getLogger(__name__)


class BaseArchivedRecommendations(BaseController, MongoMixin):
    FILTER_PROPERTY_MAP = {
        'type': 'module'
    }

    def _check_organization(self, organization_id):
        org_exists = self.session.query(
            exists().where(and_(
                Organization.id == organization_id,
                Organization.deleted.is_(False)
            ))
        ).scalar()
        if not org_exists:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])

    @staticmethod
    def _get_pipeline_filter_key(filter_key):
        return BaseArchivedRecommendations.FILTER_PROPERTY_MAP.get(
            filter_key, filter_key)

    def _get_pipeline_filter(self, organization_id, **params):
        start_date = params.pop('start_date')
        end_date = params.pop('end_date')
        res = [
            {'organization_id': organization_id},
            {'archived_at': {'$lt': end_date, '$gte': start_date}},
        ]
        for k, v in params.items():
            res.append({self._get_pipeline_filter_key(k): {'$in': v}})
        return res

    def _build_pipeline(self, match_filter, **params):
        raise NotImplementedError

    def _get_data(self, organization_id, **params):
        raise NotImplementedError

    @staticmethod
    def _fill_limit(response, **params):
        if params.get('limit'):
            response['limit'] = params['limit']
        return response

    def _fill_response(self, data, **params):
        raise NotImplementedError

    def get(self, organization_id, **params):
        self._check_organization(organization_id)
        data = self._get_data(organization_id, **params.copy())
        res = self._fill_response(data, **params)
        return res


class BreakdownArchivedRecommendationsController(BaseArchivedRecommendations):
    def _build_pipeline(self, match_filter, limit=None):
        res = [
            {'$match': {'$and': match_filter}},
            {'$group': {
                '_id': {
                    'module': '$module',
                    'archived_at': '$archived_at',
                    'reason': '$reason'
                },
                'count': {'$sum': 1}
            }},
            {'$project': {
                '_id': 0,
                'module': '$_id.module',
                'archived_at': '$_id.archived_at',
                'reason': '$_id.reason',
                'count': 1
            }},
            {'$sort': {'archived_at': -1}},
        ]
        if limit:
            res.append({'$limit': limit})
        return res

    def _get_data(self, organization_id, **params):
        limit = params.pop('limit', None)
        match_filter = self._get_pipeline_filter(
            organization_id, **params)
        pipeline = self._build_pipeline(match_filter, limit=limit)
        return list(self.archived_recommendations_collection.aggregate(
            pipeline))

    def _fill_response(self, data, **params):
        result = {
            'start_date': params.get('start_date'),
            'end_date': params.get('end_date'),
            'breakdown': data
        }
        return self._fill_limit(result, **params)


class ArchivedRecommendationsDetailsController(BaseArchivedRecommendations):
    def _get_pipeline_filter(self, organization_id, **params):
        start_date = params.pop('start_date')
        end_date = params.pop('end_date')
        res = [
            {'organization_id': organization_id}
        ]
        if start_date:
            res.append({'archived_at': {'$gte': start_date}})
        if end_date:
            res.append({'archived_at': {'$lte': end_date}})
        for k, v in params.items():
            if v is not None:
                res.append({self._get_pipeline_filter_key(k): v})
        return res

    def _build_pipeline(self, match_filter, limit=None, start_from=0):
        if limit is None:
            limit = '$count'
        res = [
            {'$match': {'$and': match_filter}},
            {'$project': {
                '_id': 0,
            }},
            {'$group': {
                '_id': None,
                'items': {'$push': '$$ROOT'},
                'count': {'$sum': 1}
            }},
            {"$project": {
                '_id': 0,
                "items": {"$slice": ['$items', start_from, limit]},
                'count': 1
            }},
        ]
        return res

    def _get_data(self, organization_id, **params):
        limit = params.pop('limit', None)
        start_from = params.pop('start_from')
        match_filter = self._get_pipeline_filter(organization_id, **params)
        pipeline = self._build_pipeline(
            match_filter, limit=limit, start_from=start_from)
        return list(self.archived_recommendations_collection.aggregate(
            pipeline))

    def _fill_response(self, data, **params):
        result = {
            'count': 0,
            'items': []
        }
        # typically data has [0, 1] objects
        for val in data:
            for k in result.keys():
                result[k] = val[k]
        return self._fill_limit(result, **params)


class ArchivedRecommendationsCountController(BaseArchivedRecommendations):
    def _fill_response(self, data, **params):
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        precision = params.get('precision')
        breakdown = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        count = 0
        for val in data:
            val_id = val['_id']
            archived_at = val_id['archived_at']
            # align to lower bound
            point = start_date + (archived_at - start_date) // precision * precision
            count += val['count']
            breakdown[point][val_id['module']][val_id['reason']] += val['count']
        for point in range(start_date, end_date, precision):
            breakdown[point].update({})
        return {
            'start_date': start_date,
            'end_date': end_date,
            'count': count,
            'breakdown': breakdown
        }

    def _get_data(self, organization_id, **params):
        match_filter = self._get_pipeline_filter(
            organization_id, **params)
        pipeline = self._build_pipeline(match_filter)
        return self.archived_recommendations_collection.aggregate(
            pipeline)

    def get(self, organization_id, **params):
        self._check_organization(organization_id)
        precision = params.pop('precision')
        data = self._get_data(organization_id, **params.copy())
        res = self._fill_response(data, precision=precision, **params)
        return res

    def _build_pipeline(self, match_filter, **params):
        res = [
            {'$match': {'$and': match_filter}},
            {'$group': {
                '_id': {
                    'archived_at': '$archived_at',
                    'module': '$module',
                    'reason': '$reason'
                },
                'count': {'$sum': 1}
            }},
        ]
        return res


class BreakdownArchivedRecommendationsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return BreakdownArchivedRecommendationsController


class ArchivedRecommendationsDetailsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ArchivedRecommendationsDetailsController


class ArchivedRecommendationsCountAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ArchivedRecommendationsCountController
