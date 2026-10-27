#!/bin/sh
set -e

# If arguments are passed, exec them directly (passthrough mode).
# This allows compose services to override CMD for scheduler loops, etc.
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

OPTSCALE_MODE="${OPTSCALE_MODE:-}"
if [ -z "$OPTSCALE_MODE" ]; then
    echo "ERROR: OPTSCALE_MODE is not set and no command arguments provided." >&2
    echo "Set OPTSCALE_MODE or pass a command as arguments." >&2
    exit 1
fi

case "$OPTSCALE_MODE" in

    # ── API services ──────────────────────────────────────────────────
    restapi)
        exec uv --project rest_api run python -u rest_api/rest_api_server/server.py ;;
    auth)
        exec uv --project auth run python -u auth/auth_server/server.py ;;
    keeper)
        exec uv run --project keeper python -u keeper/report_server/server.py ;;
    herald)
        exec uv run --project herald python -u herald/run.py ;;
    katara)
        exec uv run --project katara/katara_service python -u katara/katara_service/main.py ;;
    insider-api)
        exec uv run --project insider/insider_api python -u insider/insider_api/server.py ;;
    slacker)
        exec uv run --project slacker python slacker/slacker_server/server.py ;;
    jira-bus)
        exec uv run --project jira_bus python jira_bus/jira_bus_server/server.py ;;
    metroculusapi)
        exec uv run --project metroculus/metroculus_api python -u metroculus/metroculus_api/server.py ;;
    diproxy)
        exec uv run --project diproxy python -u diproxy/diproxy/main.py ;;
    subspector)
        exec uv run --project subspector uvicorn subspector.subspector_server.server:make_app \
            --factory --host 0.0.0.0 --port 8800 ;;

    # ── Workers (uv-managed) ─────────────────────────────────────────
    diworker)
        exec uv run --project diworker python -u diworker/diworker/main.py ;;
    diworker-raw)
        exec uv run --project diworker python -u diworker/diworker/raw_worker.py ;;
    diworker-clean)
        exec uv run --project diworker python -u diworker/diworker/clean_worker.py ;;
    katara-worker)
        exec uv run --project katara/katara_worker python -u katara/katara_worker/main.py ;;
    insider-worker)
        exec uv run --project insider/insider_worker python -u insider/insider_worker/main.py ;;
    metroculus-worker)
        exec uv run --project metroculus/metroculus_worker python -u metroculus/metroculus_worker/main.py ;;
    bumiworker)
        exec uv run --project bumiworker python -u bumiworker/bumiworker/main.py ;;
    trapper-worker)
        exec uv run --project trapper/trapper_worker python -u trapper/trapper_worker/main.py ;;
    risp-worker)
        exec uv run --project risp/risp_worker python -u risp/risp_worker/worker.py ;;
    gemini-worker)
        exec uv run --project gemini/gemini_worker python -u gemini/gemini_worker/main.py ;;
    gemini-data-worker)
        exec uv run --project gemini/gemini_data_worker python -u gemini/gemini_data_worker/main.py ;;
    bi-exporter)
        exec uv run --project bi_exporter python -u bi_exporter/bumblebi/exporter/main.py ;;

    # ── Schedulers (uv-managed) ──────────────────────────────────────
    bumischeduler)
        exec uv run --project bumischeduler python -u bumischeduler/bumischeduler/main.py ;;
    trapper-scheduler)
        exec uv run --project trapper/trapper_scheduler python -u trapper/trapper_scheduler/main.py ;;
    risp-scheduler)
        exec uv run --project risp/risp_scheduler python -u risp/risp_scheduler/scheduler.py ;;
    insider-scheduler)
        exec uv run --project insider/insider_scheduler python -u insider/insider_scheduler/main.py ;;
    metroculus-scheduler)
        exec uv run --project metroculus/metroculus_scheduler python -u metroculus/metroculus_scheduler/main.py ;;
    gemini-scheduler)
        exec uv run --project gemini/gemini_scheduler python -u gemini/gemini_scheduler/main.py ;;

    # ── Configurator ─────────────────────────────────────────────────
    configurator)
        exec python docker_images/configurator/configurator.py /config/config ;;

    # ── Executors (pip-managed) ──────────────────────────────────────
    webhook-executor)
        exec python3 docker_images/webhook_executor/worker.py ;;
    herald-executor)
        exec python3 docker_images/herald_executor/worker.py ;;
    slacker-executor)
        exec python3 docker_images/slacker_executor/worker.py ;;
    keeper-executor)
        exec python3 docker_images/keeper_executor/worker.py ;;

    # ── Workers (pip-managed docker_images) ──────────────────────────
    resource-discovery-worker)
        exec python3 docker_images/resource_discovery/worker.py ;;
    resource-observer-worker)
        exec python3 docker_images/resource_observer/worker.py ;;
    resource-violations-worker)
        exec python3 docker_images/resource_violations/worker.py ;;
    booking-observer-worker)
        exec python3 docker_images/booking_observer/worker.py ;;
    calendar-observer-worker)
        exec python3 docker_images/calendar_observer/worker.py ;;
    organization-violations-worker)
        exec python3 docker_images/organization_violations/worker.py ;;
    power-schedule-worker)
        exec python3 docker_images/power_schedule/worker.py ;;
    live-demo-generator-worker)
        exec python3 docker_images/live_demo_generator/worker.py ;;

    # ── Schedulers (pip-managed docker_images) ───────────────────────
    resource-discovery-scheduler)
        exec python3 docker_images/resource_discovery/scheduler.py ;;
    resource-observer-scheduler)
        exec python3 docker_images/resource_observer/scheduler.py ;;
    resource-violations-scheduler)
        exec python3 docker_images/resource_violations/scheduler.py ;;
    booking-observer-scheduler)
        exec python3 docker_images/booking_observer/scheduler.py ;;
    calendar-observer-scheduler)
        exec python3 docker_images/calendar_observer/scheduler.py ;;
    organization-violations-scheduler)
        exec python3 docker_images/organization_violations/scheduler.py ;;
    power-schedule-scheduler)
        exec python3 docker_images/power_schedule/scheduler.py ;;
    live-demo-generator-scheduler)
        exec python3 docker_images/live_demo_generator/scheduler.py ;;
    bi-scheduler)
        exec python3 docker_images/bi_scheduler/scheduler.py ;;

    # ── Maintenance jobs (pip-managed) ───────────────────────────────
    cleanmongodb)
        exec python docker_images/cleanmongodb/clean-mongo-db.py ;;
    cleaninfluxdb)
        exec python docker_images/cleaninfluxdb/clean-influx-db.py ;;
    layout-cleaner)
        exec python3 docker_images/layout_cleaner/worker.py ;;
    demo-org-cleanup)
        exec python3 docker_images/demo_org_cleanup/cleanup.py ;;
    failed-imports-dataset-generator)
        exec python docker_images/failed_imports_dataset_generator/failed_imports_dataset_generator.py ;;
    users-dataset-generator)
        exec python3 docker_images/users_dataset_generator/users_dataset_generator.py ;;

    # ── Node.js frontends ────────────────────────────────────────────
    ngui)
        NGUI_DIR="/opt/ngui"
        {
            echo "window.optscale = window.optscale || {};"
            env | grep '^VITE' 2>/dev/null | while IFS='=' read -r key val; do
                echo "window.optscale.${key}='${val}';"
            done || true
        } > "${NGUI_DIR}/ui/build/config.js"
        timestamp=$(date +%s)
        sed -i "s/\${buildVersion}/${timestamp}/" "${NGUI_DIR}/ui/build/index.html"
        cd "${NGUI_DIR}/server/dist"
        exec node server.js
        ;;
    jira-ui)
        cd /opt/jira_ui/server
        exec npm start
        ;;

    *)
        echo "ERROR: Unknown OPTSCALE_MODE='${OPTSCALE_MODE}'" >&2
        echo "Run with --help or check docker_images/optscale_app/entrypoint.sh for valid modes." >&2
        exit 1
        ;;
esac
