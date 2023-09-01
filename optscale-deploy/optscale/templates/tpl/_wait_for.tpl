{{- define "wait_mariadb" -}}
- name: wait-mariadb
  image: "{{ .Values.mariadb.image.repository }}:{{ .Values.mariadb.image.tag }}"
  imagePullPolicy: Never
  env:
  - name: MYSQL_ROOT_PASSWORD
    valueFrom:
      secretKeyRef:
        name: mariadb-secret
        key: password
  command: ['sh', '-c', 'until mysql --connect-timeout=2 -h {{ .Values.mariadb.service.name }}.default.svc.cluster.local -p$MYSQL_ROOT_PASSWORD -e "SELECT 1"; do sleep 2; done']
{{- end -}}

{{- define "wait_for_service" -}}
- name: "wait-{{ .service.name }}"
  image: "busybox:1.30.0"
  imagePullPolicy: IfNotPresent
  command: ['sh', '-c', 'until nc -z {{ .service.name }}.default.svc.cluster.local {{ .service.externalPort }} -w 2; do sleep 2; done']
{{- end -}}

{{- define "wait_for_thanos_service" -}}
- name: "wait-{{ .service.name }}"
  image: "busybox:1.30.0"
  imagePullPolicy: IfNotPresent
  command: ['sh', '-c', 'until nc -z {{ .service.name }}.default.svc.cluster.local {{ .service.httpExternalPort }} -w 2; do sleep 2; done']
{{- end -}}

{{- define "wait_for_elk" -}}
- name: "wait-elk"
  image: "busybox:1.30.0"
  imagePullPolicy: IfNotPresent
{{- if .Values.ha }}
  command: ['sh', '-c', 'until nc -z elasticsearch.default.svc.cluster.local {{ .Values.elastic_cluster.service.port }} -w 2; do sleep 2; done && until nc -z logstash.default.svc.cluster.local {{ .Values.logstash.service.tcp_port }} -w 2; do sleep 2; done']
{{- else }}
  command: ['sh', '-c', 'until nc -z elk.default.svc.cluster.local {{ .Values.elk.service.elastic_port }} -w 2; do sleep 2; done && until nc -z elk.default.svc.cluster.local {{ .Values.elk.service.logstash_tcp_port }} -w 2; do sleep 2; done']
{{- end }}
{{- end -}}
