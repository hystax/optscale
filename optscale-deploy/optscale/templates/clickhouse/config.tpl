{{- define "ch-config.xml" -}}
<?xml version="1.0"?>
<yandex>
    <logger>
        <level>warning</level>
        <console>1</console>
        <log>/var/log/clickhouse-server/clickhouse-server.log</log>
        <errorlog>/var/log/clickhouse-server/clickhouse-server.err.log</errorlog>
    </logger>
    <user_directories>
        <users_xml>
            <path>/etc/clickhouse-server/users.xml</path>
        </users_xml>
    </user_directories>
        <user_files_path>/var/lib/clickhouse/user_files/</user_files_path>
    <format_schema_path>/var/lib/clickhouse/format_schemas/</format_schema_path>
    <http_port>{{ .Values.clickhouse.service.httpPort }}</http_port>
    <tcp_port>{{ .Values.clickhouse.service.externalPort }}</tcp_port>
    <listen_host>0.0.0.0</listen_host>
    <max_connections>4096</max_connections>
    <keep_alive_timeout>3</keep_alive_timeout>
    <max_concurrent_queries>100</max_concurrent_queries>
    <uncompressed_cache_size>8589934592</uncompressed_cache_size>
    <mark_cache_size>5368709120</mark_cache_size>
    <path>/var/lib/clickhouse/</path>
    <tmp_path>/var/lib/clickhouse/tmp/</tmp_path>
    <default_profile>default</default_profile>
    <default_database>{{ .Values.clickhouse.db.name }}</default_database>
    <zookeeper incl="zookeeper-servers" optional="true" />
    <macros incl="macros" optional="true" />
    <builtin_dictionaries_reload_interval>3600</builtin_dictionaries_reload_interval>
    <max_session_timeout>3600</max_session_timeout>
    <default_session_timeout>60</default_session_timeout>
    <query_log replace="1">
        <database>system</database>
        <table>query_log</table>
        <engine>Engine = MergeTree PARTITION BY event_date ORDER BY event_time TTL event_date + interval 5 day</engine>
        <flush_interval_milliseconds>7500</flush_interval_milliseconds>
    </query_log>
    <dictionaries_config>*_dictionary.xml</dictionaries_config>
    <resharding>
        <task_queue_path>/clickhouse/task_queue</task_queue_path>
    </resharding>
    <distributed_ddl>
        <path>/clickhouse/task_queue/ddl</path>
    </distributed_ddl>
</yandex>
{{- end -}}
