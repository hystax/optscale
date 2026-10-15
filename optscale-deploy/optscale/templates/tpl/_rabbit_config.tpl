{{- define "rabbitmq.conf" -}}
## RabbitMQ configuration

## Clustering
cluster_formation.peer_discovery_backend  = rabbit_peer_discovery_k8s
cluster_formation.k8s.host = kubernetes.default.svc.{{ .Values.clusterDomain }}
cluster_formation.k8s.address_type = hostname
cluster_formation.node_cleanup.interval = 10
cluster_formation.node_cleanup.only_log_warning = true
cluster_partition_handling = autoheal

# Use top-level key for 4.x
load_definitions = /etc/definitions/definitions.json

## Memory-based Flow Control threshold
vm_memory_high_watermark.absolute = {{ .Values.rabbitmq.memory_limit }}MB

## Delivery acknowledgement timeout
consumer_timeout = {{ .Values.rabbitmq.consumer_timeout_ms | int64 }}

## Explicitly deny deprecated features
deprecated_features.permit.queue_master_locator = false
## disabling metrics_collection will break a tab in the UI
##deprecated_features.permit.management_metrics_collection = false
deprecated_features.permit.global_qos = false
deprecated_features.permit.ram_node_type = false
deprecated_features.permit.transient_nonexcl_queues = false
deprecated_features.permit.amqp_filter_set_bug = false
deprecated_features.permit.amqp_address_v1 = false

{{- end }}


{{- define "rabbit-plugins" -}}
[
  rabbitmq_shovel,
  rabbitmq_shovel_management,
  rabbitmq_federation,
  rabbitmq_federation_management,
  rabbitmq_consistent_hash_exchange,
  rabbitmq_management,
  rabbitmq_peer_discovery_k8s
].
{{- end }}

{{- define "definitions.json" -}}
{
  "vhosts": [
    { "name": "/" }
  ],
  "users": [
    {
      "name": "{{ .Values.rabbitmq.credentials.username }}",
      "password": "{{ .Values.rabbitmq.credentials.password }}",
      "tags": ["administrator"]
    }
  ],
  "permissions": [
    { "user": "{{ .Values.rabbitmq.credentials.username }}", "vhost": "/", "configure": ".*", "write": ".*", "read": ".*" }
  ],
  "policies": [
    {{- if .Values.rabbitmq.enableClassicMirroring }}
    { "name": "ha-all",
      "vhost": "/",
      "pattern": "^(?!amq\\.).*",
      "apply-to": "classic_queues",
      "definition": { "ha-mode": "all", "ha-sync-mode": "automatic", "ha-sync-batch-size": 1 },
      "priority": 0
    }
    {{- else if .Values.rabbitmq.enableQuorumDefaults }}
    { "name": "qq-runtime-defaults",
      "vhost": "/",
      "pattern": "^(?!amq\\.).*",
      "apply-to": "quorum_queues",
      "definition": {
        "delivery-limit": {{ default 100 .Values.rabbitmq.quorum.deliveryLimit }}{{- if .Values.rabbitmq.quorum.deadLetterExchange }}, "dead-letter-exchange": "{{ .Values.rabbitmq.quorum.deadLetterExchange }}"{{- end }}{{- if .Values.rabbitmq.quorum.maxLength }}, "max-length": {{ .Values.rabbitmq.quorum.maxLength }}{{- end }}
      },
      "priority": 0
    }
    {{- end }}
  ]
}
{{- end }}
