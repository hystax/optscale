{{- define "php.ini" -}}
[opcache]
zend_extension=opcache.so
opcache.enable=0
{{- end }}
