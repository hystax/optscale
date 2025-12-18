{{/*
Generate full image reference with registry, repository, and tag
Usage: {{ include "image.ref" (dict "registry" .Values.docker_registry "repository" $config.image.repository "tag" $config.image.tag "dockerTag" .Values.docker_tag) }}
*/}}
{{- define "image.ref" -}}
{{- $tag := .tag -}}
{{- if .dockerTag -}}
{{- $tag = .dockerTag -}}
{{- end -}}
{{- if .registry -}}
{{ .registry }}/{{ .repository }}:{{ $tag }}
{{- else -}}
{{ .repository }}:{{ $tag }}
{{- end -}}
{{- end -}}

