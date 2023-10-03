{{- define "config.yml" -}}
skip_config_update: {{ .Values.skip_config_update }}
drop_tasks_db: {{ .Values.drop_tasks_db }}
databases:
  {{- range .Values.databases }}
  - {{ . | quote }}
  {{- end}}
# initial key-value pairs for etcd
# structure
#
#   branch:
#     key: value
#
# became /branch/key = value in etcd
# lists are handled with append=true, so
#
# list:
#   - value
#
# will look like
# /list/0000000022 = value
etcd:
  public_ip: {{ .Values.public_ip }}
  storage_ip: {{ .Values.storage_ip }}
  encryption_key: {{ .Values.encryption_key }}
  release: {{ .Values.release }}
  katara_scheduler_timeout: {{ .Values.katara_scheduler_timeout }}
  bumi_scheduler_timeout: {{ .Values.bumi_scheduler_timeout }}
  bumi_worker:
    max_retries: {{ .Values.bumi_worker.max_retries }}
    wait_timeout: {{ .Values.bumi_worker.wait_timeout }}
    task_timeout: {{ .Values.bumi_worker.task_timeout }}
    run_period: {{ .Values.bumi_worker.run_period }}
  optscale_service_emails:
    recipient: {{ .Values.optscale_service_emails.recipient }}
    enabled: {{ .Values.optscale_service_emails.enabled }}
  optscale_error_emails:
    recipient: {{ .Values.optscale_error_emails.recipient }}
    enabled: {{ .Values.optscale_error_emails.enabled }}
  bulldozer_worker:
    max_retries: {{ .Values.bulldozer_worker.config.max_retries }}
    wait_timeout: {{ .Values.bulldozer_worker.config.wait_timeout }}
    task_timeout: {{ .Values.bulldozer_worker.config.task_timeout }}
    run_period: {{ .Values.bulldozer_worker.config.run_period }}
  google_calendar_service:
    enabled: {{ .Values.google_calendar_service.enabled }}
    access_key:
    {{- range $key, $value := .Values.google_calendar_service.access_key }}
        {{ $key }}: {{ $value | quote }}
    {{- end }}
  domains_blacklists:
    new_employee_email: {{ .Values.domains_blacklists.new_employee_email }}
    registration: {{ .Values.domains_blacklists.registration }}
    failed_import_email: {{ .Values.domains_blacklists.failed_import_email }}
  secret:
    cluster: {{ .Values.secrets.cluster }}
    agent: {{ .Values.secrets.agent }}
  images_source:
    host: {{ .Values.docker_registry }}
    tag: {{ .Values.docker_tag }}
  restapi:
    invite_expiration_days: {{ .Values.invite_expiration_days }}
    host: {{ .Values.rest_api.service.name }}
    port: {{ .Values.rest_api.service.externalPort }}
    demo:
      multiplier: {{ .Values.demo.multiplier }}
  auth:
    host: {{ .Values.auth.service.name }}
    port: {{ .Values.auth.service.externalPort }}
  katara:
    host: {{ .Values.katara_service.service.name }}
    port: {{ .Values.katara_service.service.externalPort }}
  herald:
    host: {{ .Values.herald.service.name }}
    port: {{ .Values.herald.service.externalPort }}
  keeper:
    host: {{ .Values.keeper.service.name }}
    port: {{ .Values.keeper.service.externalPort }}
  insider:
    host: {{ .Values.insider_api.service.name }}
    port: {{ .Values.insider_api.service.externalPort }}
  slacker:
    host: {{ .Values.slacker.service.name }}
    port: {{ .Values.slacker.service.externalPort }}
  jirabus:
    host: {{ .Values.jira_bus.service.name }}
    port: {{ .Values.jira_bus.service.externalPort }}
  arcee:
    host: {{ .Values.arcee.service.name }}
    port: {{ .Values.arcee.service.externalPort }}
  bulldozer_api:
    host: {{ .Values.bulldozer_api.service.name }}
    port: {{ .Values.bulldozer_api.service.externalPort }}
  metroculus:
    host: {{ .Values.metroculus_api.service.name }}
    port: {{ .Values.metroculus_api.service.externalPort }}
  thanos_query:
    host: {{ .Values.thanos_query.service.name }}
    port: {{ .Values.thanos_query.service.httpExternalPort }}
  thanos_receive:
    host: {{ .Values.thanos_receive.service.name }}
    port: {{ .Values.thanos_receive.service.remoteWriteExternalPort }}
    path: {{ .Values.thanos_receive.remoteWritePath }}
  authdb:
    host: {{ .Values.mariadb.service.name }}
    user: {{ .Values.mariadb.credentials.username }}
    password: {{ .Values.mariadb.credentials.password }}
    db: auth-db
  heralddb:
    host: {{ .Values.mariadb.service.name }}
    user: {{ .Values.mariadb.credentials.username }}
    password: {{ .Values.mariadb.credentials.password }}
    db: herald
  restdb:
    host: {{ .Values.mariadb.service.name }}
    user: {{ .Values.mariadb.credentials.username }}
    password: {{ .Values.mariadb.credentials.password }}
    db: my-db
    port: {{ .Values.mariadb.service.externalPort }}
  kataradb:
    host: {{ .Values.mariadb.service.name }}
    user: {{ .Values.mariadb.credentials.username }}
    password: {{ .Values.mariadb.credentials.password }}
    db: katara
  slackerdb:
    host: {{ .Values.mariadb.service.name }}
    user: {{ .Values.mariadb.credentials.username }}
    password: {{ .Values.mariadb.credentials.password }}
    db: slacker
    port: {{ .Values.mariadb.service.externalPort }}
  jirabusdb:
    host: {{ .Values.mariadb.service.name }}
    user: {{ .Values.mariadb.credentials.username }}
    password: {{ .Values.mariadb.credentials.password }}
    db: jira-bus
    port: {{ .Values.mariadb.service.externalPort }}
  mongo:
    host: {{ .Values.mongo.service.host }}
    port: {{ .Values.mongo.service.externalPort }}
    user: {{ .Values.mongo.credentials.username }}
    pass: {{ .Values.mongo.credentials.password }}
    database: keeper
  influxdb:
    host: {{ .Values.influxdb.service.name }}
    port: {{ .Values.influxdb.service.externalPort }}
    user:
    pass:
    database: metrics
  rabbit:
    user: {{ .Values.rabbitmq.credentials.username }}
    pass: {{ .Values.rabbitmq.credentials.password }}
    host: {{ .Values.rabbitmq.service.name }}
    port: {{ .Values.rabbitmq.service.externalPort }}
  minio:
    host: {{ .Values.minio.service.name }}
    port: {{ .Values.minio.service.externalPort }}
    access: {{ .Values.minio.credentials.access }}
    secret: {{ .Values.minio.credentials.secret }}
  clickhouse:
    host: {{ .Values.clickhouse.service.host }}
    port: {{ .Values.clickhouse.service.externalPort }}
    user: {{ .Values.clickhouse.db.user }}
    password: {{ .Values.clickhouse.db.password }}
    db: {{ .Values.clickhouse.db.name }}
  cleanmongodb:
    chunk_size: {{ .Values.cleanmongodb.chunk_size }}
    rows_limit: {{ .Values.cleanmongodb.rows_limit }}
  encryption_salt: {{ .Values.encryption_salt }}
  encryption_salt_auth: {{ .Values.encryption_salt_auth }}
{{ if .Values.zohocrm.regapp }}
  zohocrm:
    regapp_email: {{ .Values.zohocrm.regapp.email }}
    regapp_client_id: {{ .Values.zohocrm.regapp.client_id }}
    regapp_client_secret: {{ .Values.zohocrm.regapp.client_secret }}
    regapp_refresh_token: {{ .Values.zohocrm.regapp.refresh_token }}
    regapp_redirect_uri: {{ .Values.zohocrm.regapp.redirect_uri }}
{{ end }}
  certificates:
    {{- range $key, $val := .Values.certificates }}
    {{ $key }}: {{ $val | quote }}
    {{- end}}
{{ if .Values.logstash_host }}
  logstash_host: {{ .Values.logstash_host }}
{{ end }}
  logstash_port: {{ .Values.logstash_port }}
  events_queue: {{ .Values.events_queue }}
  resources_discovery_cache_time: {{ .Values.resources_discovery_cache_time }}
  overlay_list: {{ .Values.overlay_list }}
  token_expiration: {{ .Values.token_expiration }}
  users_dataset_generator:
    enable: {{ .Values.users_dataset_generator.enable }}
    bucket: {{ .Values.users_dataset_generator.bucket }}
    s3_path: {{ .Values.users_dataset_generator.s3_path }}
    filename: {{ .Values.users_dataset_generator.filename }}
    aws_access_key_id: {{ .Values.users_dataset_generator.aws_access_key_id }}
    aws_secret_access_key: {{ .Values.users_dataset_generator.aws_secret_access_key }}
  service_credentials:
{{ toYaml .Values.service_credentials | indent 4 }}
  optscale_meter_enabled: {{ .Values.optscale_meter_enabled }}
{{ if .Values.fake_cad_config }}
  fake_cad:
    config:
{{ toYaml .Values.fake_cad_config | indent 6 }}
{{ end }}
  smtp:
    server: {{ .Values.smtp.server }}
    email: {{ .Values.smtp.email }}
    port: {{ .Values.smtp.port }}
    password: {{ .Values.smtp.password }}
  resource_discovery_settings:
    discover_size: {{ .Values.resource_discovery_settings.discover_size }}
    timeout: {{ .Values.resource_discovery_settings.timeout }}
    writing_timeout: {{ .Values.resource_discovery_settings.writing_timeout }}
    observe_timeout: {{ .Values.resource_discovery_settings.observe_timeout }}
  bi_settings:
    exporter_run_period: {{ .Values.bi_settings.exporter_run_period }}
    encryption_key: {{ .Values.bi_settings.encryption_key }}
    task_wait_timeout: {{ .Values.bi_settings.task_wait_timeout }}
  failed_imports_dataset_generator:
    enable: {{ .Values.failed_imports_dataset_generator.enable }}
    bucket: {{ .Values.failed_imports_dataset_generator.bucket }}
    s3_path: {{ .Values.failed_imports_dataset_generator.s3_path }}
    filename: {{ .Values.failed_imports_dataset_generator.filename }}
    aws_access_key_id: {{ .Values.failed_imports_dataset_generator.aws_access_key_id }}
    aws_secret_access_key: {{ .Values.failed_imports_dataset_generator.aws_secret_access_key }}
{{- end }}
