from diworker.diworker.migrations.base import BaseMigration

"""
Drop mongo expenses collection
"""

expenses_indexes = {
    'unique_index': (['resource_id', 'date', 'cloud_account_id'], True),
    'PoolId': (['pool_id'], False),
    'CloudResourceId': (['cloud_resource_id'], False),
    'CloudAccountId': (['cloud_account_id'], False),
    'Date': (['date'], False),
    'ResourceId': (['resource_id'], False),
    'BudgetId': (['budget_id'], False),
    'OwnerId': (['owner_id'], False),
    'Region': (['region'], False),
    'ResourceType': (['resource_type'], False),
    'ServiceName': (['service_name'], False)
}
expenses_group_month_resource_indexes = {
    'PoolDate': (['pool_id', 'date'], False),
    'CloudAccountPool': (['pool_id', 'cloud_account_id'], False),
    'ResourceID': (['resource_id'], False),
    'ResourceDate': (['resource_id', 'date'], True),
    'BudgetDate': (['budget_id', 'date'], False),
    'CloudAccountDate': (['cloud_account_id', 'date'], False),
    'CloudAccountBudget': (['cloud_account_id', 'budget_id'], False),
}
expenses_group_month_ca_indexes = {
    'CloudAccountDate': (['cloud_account_id', 'date'], True),
}


class Migration(BaseMigration):
    @property
    def expenses(self):
        return self.db.expenses

    @property
    def expenses_group_month_resource(self):
        return self.db.expenses_group_month_resource

    @property
    def expenses_group_month_ca(self):
        return self.db.expenses_group_month_ca

    def upgrade(self):
        self.expenses.drop()
        self.expenses_group_month_resource.drop()
        self.expenses_group_month_ca.drop()

    def downgrade(self):
        for mongo_collection, index_map in [
            (self.expenses, expenses_indexes),
            (self.expenses_group_month_resource,
             expenses_group_month_resource_indexes),
            (self.expenses_group_month_ca, expenses_group_month_ca_indexes)
        ]:
            for index_name, index_set in index_map.items():
                field_list, unique = index_set
                mongo_collection.create_index(
                    [(f, 1) for f in field_list],
                    name=index_name,
                    unique=unique
                )
