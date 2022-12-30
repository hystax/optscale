{{- define "report_import_schedule_cmd" -}}
set -x

curl -X POST -f -H "Secret: $CLUSTER_SECRET" -d '{"period": '"$PERIOD"'}' \
  http://{{ .Values.restapi.service.name }}:{{ .Values.restapi.service.externalPort }}/restapi/v2/schedule_imports
{{- end -}}
