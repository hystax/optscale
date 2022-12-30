{{- define "mariadb.cnf" -}}
[mysqld]
innodb_file_format = BARRACUDA
innodb_large_prefix	= 1
innodb_file_per_table = 1
wait_timeout = 28800
explicit_defaults_for_timestamp = 1
{{- end }}
