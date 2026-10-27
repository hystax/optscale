# OptScale Docker Compose Quickstart (Try Mode)

Spin up a near-full OptScale instance on a single machine for evaluation and development.
This deployment is **not intended for production** — use the [Ansible/Kubernetes path](../../README.md#getting-started) for that.

## Prerequisites

| Requirement | Minimum |
|---|---|
| Docker Engine | 24+ |
| Docker Compose | v2.20+ (ships with Docker Desktop) |
| CPU | 8 cores |
| RAM | 16 GB (32 GB recommended) |
| Disk | 40 GB free |

## Quick start

```bash
cd optscale-deploy/compose

# 1. Create your environment file
cp .env.example .env
# Edit .env if you want to change passwords or the image version.

# 2. Pull images sequentially (avoids Docker Hub rate limits)
./pull.sh

# 3. Start OptScale
docker compose up -d

# 4. Wait for the configurator to finish bootstrapping (typically 1-2 minutes)
docker compose logs -f configurator

# 5. Once configurator exits successfully, all services will start.
#    Open http://localhost in your browser.
```

> **Docker Hub rate limits:** The stack has 60+ services. Running `docker compose up -d`
> directly pulls many images in parallel and can hit Docker Hub's anonymous/free-tier
> pull limits. Use `./pull.sh` beforehand to pull images one at a time. If you have a
> Docker Hub account, `docker login` first — authenticated users get higher limits.

## How it works

The Compose stack mirrors the Kubernetes Helm chart in three layers:

1. **Data plane** — etcd, MariaDB, MongoDB, RabbitMQ, Redis, InfluxDB, ClickHouse, MinIO.
2. **Metrics / storage** — Thanos receive, store gateway, and query (backed by MinIO).
3. **Application** — all API services exposed by the Kubernetes Ingress (auth, restapi, keeper, herald, katara, insider, slacker, metroculus, jira-bus, jira-ui, diproxy, subspector, ngui) plus background workers, executors, and schedulers.
4. **Cron-style schedulers** — loop-wrapped equivalents of every Kubernetes CronJob (resource-discovery, resource-observer, resource-violations, booking-observer, calendar-observer, organization-violations, power-schedule, live-demo-generator, report-import, cleanmongodb, cleaninfluxdb, layout-cleaner, demo-org-cleanup, dataset generators, bi-scheduler, gemini-scheduler, insider-scheduler, metroculus-scheduler, trapper-scheduler, risp-scheduler).

An **nginx** container acts as the edge proxy, reproducing the path-based routing from the Helm Ingress template (`/auth` → auth, `/restapi` → restapi, `/report` → keeper, etc.).

A **configurator** one-shot container seeds etcd, creates MariaDB databases, sets up RabbitMQ queues, and provisions MinIO buckets — the same bootstrap the Helm `pre-configurator` Job performs.

## Configuration

All credentials and the image version are set in `.env`. The file `config.yml` holds the etcd bootstrap values (equivalent to the rendered Helm `_config.tpl`). If you change passwords in `.env`, update the matching values in `config.yml` as well.

The `thanos_conf.yaml` file configures the Thanos object-store connection to MinIO. Update its credentials if you change the MinIO keys.

## Stopping and cleaning up

```bash
# Stop all containers (data volumes are preserved)
docker compose down

# Stop and remove all data volumes (full reset)
docker compose down -v
```

## What is excluded

The following components from the production Helm chart are intentionally omitted to keep resource usage manageable:

- **ELK stack** (Elasticsearch, Logstash, Kibana, Filebeat) — same as running `runkube.py` without `--with-elk`.
- **OpenTelemetry / Tempo** — disabled to reduce moving parts.
- **Grafana** — monitoring dashboards are not required for evaluation.
- **Thanos compactor / web** — not required for the try-mode metrics path.
- **Stripe-gated services** (subsyncer, bailiff) — only relevant when `stripe.enabled` is `true`.

## Cron-style schedulers

Kubernetes CronJobs have no direct equivalent in Docker Compose. Each scheduler runs as a long-lived container with a `while true; do …; sleep N; done` loop, approximating the original cron cadence:

| Service | Interval | Origin K8s schedule |
|---|---|---|
| resource-discovery-scheduler | 5 min | `*/5 * * * *` |
| resource-observer-scheduler | 5 min | `*/5 * * * *` |
| resource-violations-scheduler | 5 min | `*/5 * * * *` |
| booking-observer-scheduler | 1 min | `*/1 * * * *` |
| calendar-observer-scheduler | 1 h | `0 * * * *` |
| organization-violations-scheduler | 5 min | `*/5 * * * *` |
| power-schedule-scheduler | 5 min | `*/5 * * * *` |
| live-demo-generator-scheduler | 1 h | `0 * * * *` |
| report-import-scheduler-{0,1,6,24} | 15 min / 1 h / 6 h / 24 h | varies |
| trapper-scheduler | 1 h | `45 */1 * * *` |
| risp-scheduler | 1 h | `45 */1 * * *` |
| insider-scheduler | 24 h | `0 0 * * *` |
| metroculus-scheduler | 30 min | `*/30 * * * *` |
| gemini-scheduler | 5 min | `*/5 * * * *` |
| bi-scheduler | 5 min | `*/5 * * * *` |
| bumischeduler | built-in | (image has its own loop) |
| cleanmongodb | 3 min | `*/3 * * * *` |
| cleaninfluxdb | weekly | `@weekly` |
| layout-cleaner | 24 h | `0 3 * * *` |
| demo-org-cleanup | 24 h | `0 0 * * *` |
| failed-imports-dataset-generator | 24 h | `0 0 * * *` |
| users-dataset-generator | 24 h | `0 0 * * *` |

## Unified image mode

The default `docker-compose.yml` pulls a separate image for each OptScale service (~40 application images). For environments where this is impractical (Docker Hub rate limits, air-gapped registries, or simply faster deploys), an alternative compose file runs every first-party service from a single `optscale_app` image.

Data-plane images (etcd, MariaDB, Mongo, Redis, InfluxDB) are built locally by `build-unified.sh`. Upstream images (RabbitMQ, ClickHouse, MinIO, Thanos, nginx, curl) are still pulled separately.

### Building the unified image

```bash
cd optscale-deploy/compose

# Build from the repository root (takes a while on first run).
# Defaults match COMPANY and OPTSCALE_VERSION from .env.
./build-unified.sh              # -> hystax/optscale_app:latest, hystax/mongo:latest, etc.
./build-unified.sh latest       # -> hystax/optscale_app:latest, etc.
./build-unified.sh v1.0 hystax  # -> hystax/optscale_app:v1.0, etc.
```

### Running with the unified image

```bash
# Make sure .env exists (same file as the default stack)
cp .env.example .env

# Start the unified stack
docker compose -f docker-compose.unified.yml up -d
```

Each service container sets `OPTSCALE_MODE` to select which process runs inside the shared image. For scheduler services that need a `while true; sleep N` loop, the compose file passes the loop as `command:` args, which the entrypoint executes directly.

### When to use which

| | Default (`docker-compose.yml`) | Unified (`docker-compose.unified.yml`) |
|---|---|---|
| **Image pulls** | ~40 app images + data plane | 1 app image + data plane |
| **Build time** | Fast per-service rebuilds | Single long build |
| **Image size** | Small per image | One large image (~2-4 GB) |
| **Best for** | Development, CI per-service | Evaluation, air-gapped, quickstart |

## Troubleshooting

**Configurator fails or restarts**: check that all datastore containers are healthy first (`docker compose ps`). The configurator retries automatically, but persistent failures usually indicate a MariaDB or RabbitMQ connectivity issue.

**Services report etcd connection errors**: the configurator must finish before app services can start. If you see these errors, wait for `docker compose logs configurator` to show `Configuration completed.`

**Port 80 is already in use**: change `EDGE_PORT` in `.env` to another port (e.g. `8080`), then access OptScale at `http://localhost:8080`.
