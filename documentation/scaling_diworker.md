# Scaling Billing Report Processing Workers

Billing report processing is split into three sequential stages. Each stage runs as a separate deployment and consumes its own RabbitMQ queue, so the stages are scaled independently.

```
REST API -> report-imports -> diworker (orchestrator) -> diworker-raw -> diworker-clean
```

---

## Workers Overview

| Deployment | Queue | Role |
|---|---|---|
| `diworker` | `report-imports` | Validates the task, deduplicates, selects changed report files for file-based clouds, routes the import to the raw queue (or straight to the clean queue when no files changed) |
| `diworker-raw` | `report-raw` | Imports raw expenses to MongoDB: one report file per task for file-based clouds, the whole import in one task for the others |
| `diworker-clean` | `report-clean` | Generates clean expenses in ClickHouse, finalises the import |

---

## Scaling Dimensions

`diworker-raw` and `diworker-clean` have two knobs each. The orchestrator has none: it always runs as one replica with one thread.

### 1. Pod replicas (`replicaCount`)

Controls how many pods run in parallel. Each pod has its own thread pool and RabbitMQ consumer. Increasing replicas distributes queue load across pods.

Set in `optscale-deploy/optscale/values.yaml` (all three are `1` by default; the values below are an example):

```yaml
diworker:
  replicaCount: 1       # orchestrator — keep at 1

diworker_raw:
  replicaCount: 3       # example: scale up when report-raw queue depth is high

diworker_clean:
  replicaCount: 2       # example: scale up when report-clean queue depth is high
```

### 2. Worker threads per pod (`max_report_imports_workers`)

Controls the `ThreadPoolExecutor` thread count (and the RabbitMQ prefetch count) inside each pod. It is one setting for both raw and clean pods: it cannot be set for one of them only.

In Kubernetes it is set via `import_reports.max_workers` in `values.yaml` and written to etcd as `max_report_imports_workers` in the `diworker` branch:

```yaml
import_reports:
  max_workers: 10   # value in values.yaml; applies to raw and clean pods
```

In Docker Compose it is set as `diworker.max_report_imports_workers` in `optscale-deploy/compose/config.yml` (also `10`).

If the setting is missing in etcd, the workers fall back to `DEFAULT_MAX_WORKERS = 4` (`diworker/diworker/worker_base.py`).

The orchestrator (`diworker`) ignores this setting — it always uses a pool of 1.

**Total concurrency** of a stage = `replicaCount × max_workers`

---

## Worker-Specific Characteristics

### `diworker` — Orchestrator

- Fixed pool of **1 thread**; cannot be changed.
- Work is lightweight: validates the task, checks for another active import of the cloud account, and for file-based imports lists the report files in the cloud storage and selects the changed ones (no file download). Then it publishes one message: to `report-raw`, or to `report-clean` when no files changed.
- **Do not scale horizontally.** Multiple orchestrator pods would race to process the same `report-imports` message and could create duplicate raw tasks before the deduplication check completes.
- One replica is sufficient in all normal production scenarios.

### `diworker-raw` — Raw Worker

- **Network- and I/O-bound**: downloads report files (CSV/Parquet) from cloud storage or reads expenses from cloud APIs, parses them, writes raw expenses to MongoDB.
- One message is one report file for file-based imports and the whole import otherwise. Tasks of different imports run in parallel; the files of one import are processed one after another.
- Per-tenant concurrency is capped by `max_tenant_import_workers` (default `1`): child accounts of one linked-account root are imported one at a time **within a pod**. The limit is an in-process semaphore, so with N raw pods up to N × `max_tenant_import_workers` imports of one root may run at once. The setting is not exposed in `values.yaml`; it is read from the `diworker` settings in etcd and defaults to `1`.
- When the `report-raw` queue depth grows and stays elevated:
  - if the raw pods have spare CPU, memory and network bandwidth, add threads (`max_workers`);
  - if the raw pods are saturated, add replicas.

```yaml
diworker_raw:
  replicaCount: 4       # example: more pods when existing pods are saturated
```

Keep `max_workers` low if report files are large: every thread holds one file on disk and parses it. Remember that `max_workers` also changes the thread count of the clean pods.

### `diworker-clean` — Clean Worker

- **CPU- and database-bound**: generates clean expense records, writes to ClickHouse, saves file states to MongoDB.
- One message per import: it is published after the last raw task of the import (or by the orchestrator when no files changed) and finalises the whole import. Clean tasks of different imports are independent.
- Scale up replicas when:
  - The `report-clean` queue grows but ClickHouse write throughput is not already saturated.
  - ClickHouse CPU/memory headroom is available — adding clean pods without headroom will just cause query timeouts.

```yaml
diworker_clean:
  replicaCount: 2       # example
```

---

## Recommended Starting Points

| Load | `diworker` replicas | `diworker-raw` replicas | `diworker-clean` replicas | `max_workers` |
|---|---|---|---|---|
| Small (< 10 cloud accounts) | 1 | 1 | 1 | 4 |
| Medium (10–50 accounts) | 1 | 2 | 2 | 6 |
| Large (50+ accounts) | 1 | 4–6 | 2–3 | 8–10 |

Monitor the `report-raw` and `report-clean` queue depths in RabbitMQ management UI to determine when to scale.

---

## Applying Changes

### Replica count

**Kubernetes — immediate (temporary):**

```bash
kubectl scale deployment diworker-raw --replicas=4
kubectl scale deployment diworker-clean --replicas=2
```

The change takes effect immediately but is lost on the next deployment update because Helm resets replicas to the configured value.

**Kubernetes — persistent:**

Set `replicaCount` in your overlay file (or in `values.yaml`) and update the deployment with `runkube.py` from the `optscale-deploy` directory, using the same overlays the cluster was deployed with:

```bash
./runkube.py --with-elk -o overlay/user_template.yml -- <deployment name> <version>
```

**Docker Compose:**

```bash
docker compose up -d --scale diworker-raw=4 --scale diworker-clean=2
```

### Thread pool size (`max_report_imports_workers`)

This value is stored in etcd under the `diworker` config branch and read by each worker at startup.

**Kubernetes:** it is set via `import_reports.max_workers` (in your overlay file or in `values.yaml`) and written to etcd by the configurator job. To change it, update the value and redeploy with `runkube.py` as shown above: it deletes the `/configured` etcd key and the old jobs, so the configurator runs again and rewrites etcd (unless `skip_config_update` is `true`). A bare `helm upgrade` deletes neither the key nor the old configurator job, so the configurator may not run again and the new value may not reach etcd. All worker pods must be restarted to pick up the new value.

**Docker Compose:** it is set as `diworker.max_report_imports_workers` in `optscale-deploy/compose/config.yml`, which the configurator writes to etcd. Change it there and recreate the containers (`docker compose up -d --force-recreate`); the workers must be restarted to pick up the new value.
