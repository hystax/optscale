CREATE TABLE average_metrics (
    cloud_account_id String,
    resource_id String,
    date DateTime,
    metric Enum8('cpu' = 1, 'ram' = 2, 'disk_read_io' = 3, 'disk_write_io' = 4, 'network_in_io' = 5, 'network_out_io' = 6),
    value Float32)
ENGINE = MergeTree
PARTITION BY cloud_account_id
ORDER BY (cloud_account_id, resource_id, date)
