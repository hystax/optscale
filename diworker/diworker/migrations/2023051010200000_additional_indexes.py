import logging
from pymongo import IndexModel
from diworker.migrations.base import BaseMigration
"""
Indexes for archived_recommendations, checklists, property_history, resources,
webhook_observer, webhook_logs collections
"""

LOG = logging.getLogger(__name__)

CHUNK_SIZE = 200
COLLECTION_INDEXES = {
    'archived_recommendations': [
        {
            'name': 'OrgArchivedAtModule',
            'fields': ['organization_id', 'archived_at', 'module']
        }],
    'checklists': [
        {
                'name': 'OrgCreatedAtIndex',
                'fields': ['organization_id', 'created_at']
        },
        {
                'name': 'ModuleIndex',
                'fields': ['module']
        }],
    'property_history': [
        {
            'name': 'ResourceID',
            'fields': ['resource_id']
        },
        {
            'name': 'Time',
            'fields': ['time']
        }],
    'resources': [
        {
            'name': 'CloudAccountID',
            'fields': ['cloud_account_id']
        },
        {
            'name': 'EmlpoyeeID',
            'fields': ['employee_id']
        },
        {
            'name': 'CloudResourceID',
            'fields': ['cloud_resource_id']
        },
        {
            'name': 'PoolID',
            'fields': ['pool_id'],
        },
        {
            'name': 'CloudResourceActive',
            'fields': ['active']
        },
        {
            'name': 'CloudAccIdResTypeActiveIndex',
            'fields': ['cloud_account_id', 'resource_type', 'active'],
        },
        {
            'name': 'ClusterId',
            'fields': ['cluster_id']
        },
        {
            'name': 'ClusterTypeId',
            'fields': ['cluster_type_id'],
        },
        {
            'name': 'Name',
            'fields': ['name'],
        },
        {
            'name': 'ResourceConstraintViolated',
            'fields': ['constraint_violated'],
        },
        {
            'name': 'ShareableResource',
            'fields': ['shareable'],
        },
        {
            'name': 'organization_id_1',
            'fields': ['organization_id'],
            'partialFilterExpression': {
                'organization_id': {'$exists': True}
            }
        },
        {
            'name': 'cloud_account_id_1_active_1',
            'fields': ['cloud_account_id', 'active'],
        },
        {
            'name': 'cloud_account_id_1_constraint_violated_1',
            'fields': ['cloud_account_id', 'constraint_violated'],
            'partialFilterExpression': {
                "constraint_violated": True
            }
        },
    ],
    'webhook_observer': [
        {
            'name': 'OrganizationID',
            'fields': ['organization_id']
        }],
    'webhook_logs': [
        {
            'name': 'OrganizationID',
            'fields': ['organization_id']
        },
        {
            'name': 'WebhookID',
            'fields': ['webhook_id']
        }
    ]}


class Migration(BaseMigration):

    def collection(self, collection_name):
        return self.db[collection_name]

    @staticmethod
    def get_indexes(collection):
        return [x['name'] for x in collection.list_indexes()]

    @staticmethod
    def get_index_model(index_name, index_info):
        body = {
            'name': index_name,
            'background': True
        }
        if 'partialFilterExpression' in index_info:
            body['partialFilterExpression'] = index_info['partialFilterExpression']
        LOG.info('Create index %s - %s' % (index_name, index_info))
        return IndexModel([(f, 1) for f in index_info['fields']], **body)

    def upgrade(self):
        for coll_name, data in COLLECTION_INDEXES.items():
            collection = self.collection(coll_name)
            indexes_to_create = []
            existing_indexes = self.get_indexes(collection)
            for index_data in data:
                index_name = index_data['name']
                if index_name not in existing_indexes:
                    LOG.info('Will create index %s' % index_name)
                    index = self.get_index_model(index_name, index_data)
                    indexes_to_create.append(index)
            if indexes_to_create:
                collection.create_indexes(indexes_to_create)

    def downgrade(self):
        for coll_name, data in COLLECTION_INDEXES.items():
            collection = self.collection(coll_name)
            existing_indexes = self.get_indexes(collection)
            for index in data:
                index_name = index['name']
                if index_name in existing_indexes:
                    LOG.info('Dropping index %s' % index_name)
                    collection.drop_index(name=index_name)
