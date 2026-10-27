# Unified OptScale application image.
# Build context: repository root.
#
#   docker build -f docker_images/optscale_app/Dockerfile -t optscale_app:local .
#
# At runtime, set OPTSCALE_MODE to select which service to start (see entrypoint.sh).

# ── Stage 1: Build ngui ──────────────────────────────────────────────
FROM node:22.16.0-alpine3.21 AS ngui-builder

RUN npm install -g pnpm@10.33.0
ENV NODE_ENV=production

WORKDIR /build
COPY ngui/ .
RUN pnpm install --frozen-lockfile --ignore-scripts
RUN pnpm run -r build
RUN pnpm deploy --filter=server --prod ./prod/server && \
    ./prod/server/scripts/prune_node_modules.sh
RUN rm -rf ./ui/node_modules

# ── Stage 2: Build jira_ui ───────────────────────────────────────────
FROM node:18.14.2-alpine3.16 AS jira-ui-builder

ENV NODE_ENV=production
WORKDIR /build/ui
COPY jira_ui/ui/package*.json ./
RUN npm ci --ignore-scripts --legacy-peer-deps
COPY jira_ui/ui/ ./
RUN npm run build && rm -rf node_modules

WORKDIR /build/server
COPY jira_ui/server/package*.json ./
RUN npm ci --ignore-scripts
COPY jira_ui/server/ ./
RUN ./scripts/prune_node_modules.sh

# ── Stage 3: Runtime ─────────────────────────────────────────────────
FROM python:3.12.11-slim

LABEL org.opencontainers.image.authors="Hystax"

# uv (Python project manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Node.js runtime (for ngui + jira_ui servers)
COPY --from=node:22.16.0-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:22.16.0-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

# System packages — union of per-service Dockerfiles
RUN apt-get update && apt-get install -y --no-install-recommends \
        libsodium-dev \
        sendmail \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Directories expected by specific services
RUN mkdir -p /src/archive

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

# ── Copy source tree (shared libs first, then services) ──────────────
COPY tools/ tools/
COPY optscale_client/ optscale_client/

COPY rest_api/ rest_api/
COPY auth/ auth/
COPY keeper/ keeper/
COPY herald/ herald/
COPY katara/ katara/
COPY insider/ insider/
COPY slacker/ slacker/
COPY jira_bus/ jira_bus/
COPY metroculus/ metroculus/
COPY diproxy/ diproxy/
COPY subspector/ subspector/
COPY diworker/ diworker/
COPY bumiworker/ bumiworker/
COPY bumischeduler/ bumischeduler/
COPY trapper/ trapper/
COPY risp/ risp/
COPY gemini/ gemini/
COPY bi_exporter/ bi_exporter/

COPY docker_images/configurator/ docker_images/configurator/
COPY docker_images/resource_discovery/ docker_images/resource_discovery/
COPY docker_images/resource_observer/ docker_images/resource_observer/
COPY docker_images/resource_violations/ docker_images/resource_violations/
COPY docker_images/booking_observer/ docker_images/booking_observer/
COPY docker_images/calendar_observer/ docker_images/calendar_observer/
COPY docker_images/organization_violations/ docker_images/organization_violations/
COPY docker_images/power_schedule/ docker_images/power_schedule/
COPY docker_images/live_demo_generator/ docker_images/live_demo_generator/
COPY docker_images/webhook_executor/ docker_images/webhook_executor/
COPY docker_images/herald_executor/ docker_images/herald_executor/
COPY docker_images/slacker_executor/ docker_images/slacker_executor/
COPY docker_images/keeper_executor/ docker_images/keeper_executor/
COPY docker_images/bi_scheduler/ docker_images/bi_scheduler/
COPY docker_images/cleanmongodb/ docker_images/cleanmongodb/
COPY docker_images/cleaninfluxdb/ docker_images/cleaninfluxdb/
COPY docker_images/layout_cleaner/ docker_images/layout_cleaner/
COPY docker_images/demo_org_cleanup/ docker_images/demo_org_cleanup/
COPY docker_images/failed_imports_dataset_generator/ docker_images/failed_imports_dataset_generator/
COPY docker_images/users_dataset_generator/ docker_images/users_dataset_generator/
COPY docker_images/subsyncer/ docker_images/subsyncer/
COPY docker_images/bailiff/ docker_images/bailiff/

# ── Install uv-managed project dependencies ──────────────────────────
RUN uv --project rest_api sync --locked --no-dev && \
    uv --project auth sync --locked --no-dev && \
    uv --project keeper sync --locked --no-dev && \
    uv --project herald sync --locked --no-dev && \
    uv --project katara/katara_service sync --locked --no-dev && \
    uv --project katara/katara_worker sync --locked --no-dev && \
    uv --project insider/insider_api sync --locked --no-dev && \
    uv --project insider/insider_worker sync --locked --no-dev && \
    uv --project insider/insider_scheduler sync --locked --no-dev && \
    uv --project slacker sync --locked --no-dev && \
    uv --project jira_bus sync --locked --no-dev && \
    uv --project metroculus/metroculus_api sync --locked --no-dev && \
    uv --project metroculus/metroculus_worker sync --locked --no-dev && \
    uv --project metroculus/metroculus_scheduler sync --locked --no-dev && \
    uv --project diproxy sync --locked --no-dev && \
    uv --project subspector sync --locked --no-dev && \
    uv --project diworker sync --locked --no-dev && \
    uv --project bumiworker sync --locked --no-dev && \
    uv --project bumischeduler sync --locked --no-dev && \
    uv --project trapper/trapper_worker sync --locked --no-dev && \
    uv --project trapper/trapper_scheduler sync --locked --no-dev && \
    uv --project risp/risp_worker sync --locked --no-dev && \
    uv --project risp/risp_scheduler sync --locked --no-dev && \
    uv --project gemini/gemini_worker sync --locked --no-dev && \
    uv --project gemini/gemini_data_worker sync --locked --no-dev && \
    uv --project gemini/gemini_scheduler sync --locked --no-dev && \
    uv --project bi_exporter sync --locked --no-dev

# Build-time code generation
RUN uv --project rest_api run python -u rest_api/rest_api_server/write_spec.py && \
    uv --project auth run python -u auth/auth_server/write_spec.py && \
    uv --project slacker run python -u slacker/slacker_server/write_spec.py

# ── Install uv-managed dependencies (docker_images/* services) ───────
RUN uv --project docker_images/configurator sync --locked --no-dev && \
    uv --project docker_images/resource_discovery sync --locked --no-dev && \
    uv --project docker_images/resource_observer sync --locked --no-dev && \
    uv --project docker_images/resource_violations sync --locked --no-dev && \
    uv --project docker_images/booking_observer sync --locked --no-dev && \
    uv --project docker_images/calendar_observer sync --locked --no-dev && \
    uv --project docker_images/organization_violations sync --locked --no-dev && \
    uv --project docker_images/power_schedule sync --locked --no-dev && \
    uv --project docker_images/live_demo_generator sync --locked --no-dev && \
    uv --project docker_images/webhook_executor sync --locked --no-dev && \
    uv --project docker_images/herald_executor sync --locked --no-dev && \
    uv --project docker_images/slacker_executor sync --locked --no-dev && \
    uv --project docker_images/keeper_executor sync --locked --no-dev && \
    uv --project docker_images/bi_scheduler sync --locked --no-dev && \
    uv --project docker_images/cleanmongodb sync --locked --no-dev && \
    uv --project docker_images/cleaninfluxdb sync --locked --no-dev && \
    uv --project docker_images/layout_cleaner sync --locked --no-dev && \
    uv --project docker_images/demo_org_cleanup sync --locked --no-dev && \
    uv --project docker_images/failed_imports_dataset_generator sync --locked --no-dev && \
    uv --project docker_images/users_dataset_generator sync --locked --no-dev && \
    uv --project docker_images/subsyncer sync --locked --no-dev && \
    uv --project docker_images/bailiff sync --locked --no-dev

# ── Copy Node.js frontend build artifacts ────────────────────────────
COPY --from=ngui-builder /build/prod/server/dist     /opt/ngui/server/dist
COPY --from=ngui-builder /build/prod/server/node_modules /opt/ngui/server/node_modules
COPY --from=ngui-builder /build/ui/build             /opt/ngui/ui/build
COPY --from=ngui-builder /build/prepare-and-run.sh   /opt/ngui/prepare-and-run.sh

COPY --from=jira-ui-builder /build/ui/    /opt/jira_ui/ui/
COPY --from=jira-ui-builder /build/server /opt/jira_ui/server

# ── Entrypoint ───────────────────────────────────────────────────────
COPY docker_images/optscale_app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
