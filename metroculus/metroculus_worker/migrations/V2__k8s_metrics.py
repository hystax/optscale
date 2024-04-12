from metroculus.metroculus_worker.migrations.base import MigrationBase


class Migration(MigrationBase):
    def upgrade(self):
        query = """CREATE TABLE k8s_metrics (
                     cloud_account_id String,
                     resource_id String,
                     date DateTime,
                     pod_cpu_average_usage Float32,
                     pod_memory_average_usage Float32,
                     pod_cpu_provision Float32,
                     pod_cpu_requests Float32,
                     pod_memory_provision Float32,
                     pod_memory_requests Float32,
                     namespace_cpu_provision_used Float32,
                     namespace_memory_provision_used Float32,
                     namespace_quota_cpu_provision_hard Float32,
                     namespace_quota_memory_provision_hard Float32,
                     namespace_quota_cpu_provision_medium Float32,
                     namespace_quota_memory_provision_medium Float32,
                     namespace_quota_cpu_provision_low Float32,
                     namespace_quota_memory_provision_low Float32,
                     namespace_cpu_requests_used Float32,
                     namespace_memory_requests_used Float32,
                     namespace_quota_cpu_requests_hard Float32,
                     namespace_quota_memory_requests_hard Float32,
                     namespace_quota_cpu_requests_medium Float32,
                     namespace_quota_memory_requests_medium Float32,
                     namespace_quota_cpu_requests_low Float32,
                     namespace_quota_memory_requests_low Float32)
                   ENGINE = MergeTree
                   PARTITION BY cloud_account_id
                   ORDER BY (cloud_account_id, resource_id, date)"""
        self.clickhouse_client.execute(query)
