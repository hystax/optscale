{{/* Build an OptScale image reference from overlay-configured registry and tag. */}}
{{- define "image.ref" -}}
{{- $tag := default .tag .dockerTag -}}
{{- if .registry -}}
{{ printf "%s/%s:%s" .registry .repository $tag }}
{{- else -}}
{{ printf "%s:%s" .repository $tag }}
{{- end -}}
{{- end -}}

{{/* Render configured private-registry credentials in a pod spec. */}}
{{- define "image.pullSecrets" -}}
{{- with .Values.imagePullSecrets }}
imagePullSecrets:
{{ toYaml . }}
{{- end -}}
{{- end -}}
