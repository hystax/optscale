{{- define "ready_probe" -}}
readinessProbe:
  tcpSocket:
    port: {{ .service.internalPort }}
    initialDelaySeconds: 5
    periodSeconds: 10
{{- end -}}
