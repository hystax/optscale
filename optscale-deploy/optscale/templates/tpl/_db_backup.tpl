{{- define "backup.sh" -}}
set -e

BACKUP_PATH=/backup

echo "Dumping the buffer pool..."
mysql -h {{ .name }} -p$MYSQL_ROOT_PASSWORD -e "set global innodb_buffer_pool_dump_now = ON;"

echo "Dumping all databases..."
mysqldump -A -h {{ .name }} -p$MYSQL_ROOT_PASSWORD | gzip -c - >"$BACKUP_PATH/optscale_db_$(date +%s).sql.gz"

echo "Loading the buffer pool back..."
mysql -h {{ .name }} -p$MYSQL_ROOT_PASSWORD -e "set global innodb_buffer_pool_load_now = ON;"

ls -1 $BACKUP_PATH/* | sort | head -n -$KEEP_COUNT | xargs -d '\n' rm -f -v --

echo "Finished!"
{{- end -}}
