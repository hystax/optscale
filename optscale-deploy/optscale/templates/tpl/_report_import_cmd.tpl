{{- define "report_import_schedule_cmd" -}}
set -x

curl -X POST -f -H "Secret: $CLUSTER_SECRET" -d '{"period": '"$PERIOD"'}' \
  http://{{ .Values.rest_api.service.name }}:{{ .Values.rest_api.service.externalPort }}/rest_api/v2/schedule_imports
{{- end -}}
