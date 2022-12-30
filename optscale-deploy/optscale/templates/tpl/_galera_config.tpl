{{- define "galera.cnf" -}}
[galera]
user = mysql
bind-address = 0.0.0.0
default_storage_engine = InnoDB
binlog_format = ROW
innodb_autoinc_lock_mode = 2
innodb_flush_log_at_trx_commit = 0
query_cache_size = 0
query_cache_type = 0
# MariaDB Galera settings
wsrep_on=ON
wsrep_provider=/usr/lib/galera/libgalera_smm.so
wsrep_sst_method=rsync
# Cluster settings (automatically updated)
wsrep_cluster_address=gcomm://
wsrep_cluster_name=galera
wsrep_node_address=127.0.0.1
wsrep_sync_wait = 1
{{- end }}
