import logging
import math
from pymongo import UpdateOne
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from diworker.diworker.migrations.base import BaseMigration
"""
Update NaN values to 0 in raw expenses for AWS
"""
CHUNK_SIZE = 200
LOG = logging.getLogger(__name__)

EXPENSE_FIELDS = [
    'cost',
    'discount_bundled_discount',
    'discount_total_discount',
    'lineItem/NormalizationFactor',
    'lineItem/BlendedCost',
    'lineItem/NetUnblendedCost',
    'lineItem/UnblendedCost',
    'lineItem/UsageAmount',
    'reservation/EffectiveCost',
    'reservation/NetEffectiveCost',
    'reservation/TotalReservedNormalizedUnits',
    'reservation/TotalReservedUnits',
    'reservation/AmortizedUpfrontCostForUsage',
    'reservation/NetAmortizedUpfrontCostForUsage',
    'reservation/AmortizedUpfrontFeeForBillingPeriod',
    'reservation/NetAmortizedUpfrontFeeForBillingPeriod',
    'reservation/RecurringFeeForUsage',
    'reservation/NetRecurringFeeForUsage',
    'reservation/UnusedRecurringFee',
    'reservation/NetUnusedRecurringFee',
    'reservation/UpfrontValue',
    'reservation/NetUpfrontValue',
    'reservation/UnusedAmortizedUpfrontFeeForBillingPeriod',
    'reservation/NetUnusedAmortizedUpfrontFeeForBillingPeriod',
    'savingsPlan/AmortizedUpfrontCommitmentForBillingPeriod',
    'savingsPlan/NetAmortizedUpfrontCommitmentForBillingPeriod',
    'savingsPlan/RecurringCommitmentForBillingPeriod',
    'savingsPlan/NetRecurringCommitmentForBillingPeriod',
    'savingsPlan/SavingsPlanEffectiveCost',
    'savingsPlan/NetSavingsPlanEffectiveCost',
    'savingsPlan/SavingsPlanRate',
    'savingsPlan/TotalCommitmentToDate',
    'pricing/publicOnDemandCost',
]


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret())
        return self._rest_cl

    def get_cloud_accs(self):
        cloud_accounts_ids = set()
        _, organizations = self.rest_cl.organization_list({
            'with_connected_accounts': True, 'is_demo': False})
        for org in organizations['organizations']:
            _, accounts = self.rest_cl.cloud_account_list(
                org['id'], type='aws_cnr')
            for cloud_account in accounts['cloud_accounts']:
                if cloud_account['auto_import']:
                    cloud_accounts_ids.add(cloud_account['id'])
        return cloud_accounts_ids

    def upgrade(self):
        cloud_accs = self.get_cloud_accs()
        for i, cloud_acc_id in enumerate(cloud_accs):
            LOG.info('Starting processing for cloud account %s (%s/%s)' % (
                cloud_acc_id, i+1, len(cloud_accs)))
            raw_expenses = self.mongo_raw.find({
                'cloud_account_id': cloud_acc_id,
                'bill/BillingPeriodStartDate': {'$exists': True},
                '$or': [{x: math.nan} for x in EXPENSE_FIELDS]
            })
            chunk = []
            for expense in raw_expenses:
                fields = [x for x, v in expense.items()
                          if isinstance(v, float) and math.isnan(v)]
                chunk.append(UpdateOne(
                    filter={'_id': expense['_id']},
                    update={'$set': {f: 0 for f in fields}}
                ))
                if len(chunk) >= CHUNK_SIZE:
                    self.mongo_raw.bulk_write(chunk)
                    chunk = []
            if chunk:
                self.mongo_raw.bulk_write(chunk)

    def downgrade(self):
        pass
