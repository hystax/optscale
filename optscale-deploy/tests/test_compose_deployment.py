# pyright: reportMissingImports=false
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from yaml.composer import ComposerError
from yaml.events import AliasEvent


DEPLOY_DIR = Path(__file__).resolve().parents[1]
COMPOSE_DIR = DEPLOY_DIR / "compose"
COMPOSE_FILES = (
    COMPOSE_DIR / "docker-compose.yml",
    COMPOSE_DIR / "docker-compose.unified.yml",
)
ENV_FILE = COMPOSE_DIR / ".env.example"
VALUES_FILE = DEPLOY_DIR / "optscale" / "values.yaml"
COMPONENTS_FILE = DEPLOY_DIR / "components.yaml"

FIRST_PARTY_IMAGE_PREFIX = "${COMPANY:-hystax}/"
EXTERNAL_IMAGE_PREFIXES = (
    "clickhouse/",
    "curlimages/",
    "minio/",
    "nginx:",
    "rabbitmq:",
    "thanosio/",
)

# Compose has an edge proxy where k8s has an Ingress resource instead.
COMPOSE_ONLY_SERVICES = {"edge"}

# These repositories are built by dedicated Dockerfiles, but are represented in
# Compose as upstream images or generated Helm resources rather than
# components.yaml entries.
FIRST_PARTY_REPOSITORY_EXCEPTIONS = {"optscale_app"}


class HelmValuesLoader(yaml.SafeLoader):
    """PyYAML rejects duplicate anchors that Helm's YAML parser accepts."""

    def compose_node(self, parent, index):
        if self.check_event(AliasEvent):
            event = self.get_event()
            anchor = event.anchor
            if anchor not in self.anchors:
                raise ComposerError(
                    None, None, f"found undefined alias {anchor!r}",
                    event.start_mark
                )
            return self.anchors[anchor]
        event = self.peek_event()
        anchor = event.anchor
        self.descend_resolver(parent, index)
        if self.check_event(yaml.events.ScalarEvent):
            node = self.compose_scalar_node(anchor)
        elif self.check_event(yaml.events.SequenceStartEvent):
            node = self.compose_sequence_node(anchor)
        elif self.check_event(yaml.events.MappingStartEvent):
            node = self.compose_mapping_node(anchor)
        self.ascend_resolver()
        return node


def load_yaml(path):
    with path.open() as f:
        return yaml.load(f, Loader=HelmValuesLoader)


def load_compose(path):
    data = load_yaml(path)
    assert "services" in data
    return data


def service_names(compose_file):
    return set(load_compose(compose_file)["services"])


@pytest.fixture(scope="module")
def values():
    return load_yaml(VALUES_FILE)


@pytest.fixture(scope="module")
def components():
    return set(load_yaml(COMPONENTS_FILE))


def value_name(values, key):
    return values[key]["name"]


def value_service_name(values, key):
    return values[key]["service"]["name"]


def k8s_equivalent_names(values):
    names = {
        "auth": {value_service_name(values, "auth")},
        "bi-exporter": {value_name(values, "bi_exporter")},
        "bi-scheduler": {value_name(values, "bi_scheduler")},
        "booking-observer-worker": {
            f"{value_name(values, 'booking_observer')}-worker"
        },
        "booking-observer-scheduler": {
            f"{value_name(values, 'booking_observer')}-scheduler"
        },
        "bumischeduler": {value_name(values, "bumischeduler")},
        "bumiworker": {value_name(values, "bumiworker")},
        "calendar-observer-worker": {
            f"{value_name(values, 'calendar_observer')}-worker"
        },
        "calendar-observer-scheduler": {
            f"{value_name(values, 'calendar_observer')}-scheduler"
        },
        "clickhouse": {value_service_name(values, "clickhouse")},
        "cleaninfluxdb": {value_name(values, "cleaninfluxdb")},
        "cleanmongodb": {value_name(values, "cleanmongodb")},
        "configurator": {"pre-configurator"},
        "demo-org-cleanup": {value_name(values, "demo_org_cleanup")},
        "diproxy": {value_service_name(values, "diproxy")},
        "diworker": {value_name(values, "diworker")},
        "diworker-raw": {value_name(values, "diworker_raw")},
        "diworker-clean": {value_name(values, "diworker_clean")},
        "etcd-client": {value_service_name(values, "etcd")},
        "failed-imports-dataset-generator": {
            value_name(values, "failed_imports_dataset_generator")
        },
        "gemini-data-worker": {value_name(values, "gemini_data_worker")},
        "gemini-scheduler": {value_name(values, "gemini_scheduler")},
        "gemini-worker": {value_name(values, "gemini_worker")},
        "herald-api": {
            f"{value_name(values, 'herald')}{values['herald']['api']['role']}",
            value_service_name(values, "herald"),
        },
        "herald-engine": {
            f"{value_name(values, 'herald')}"
            f"{values['herald']['engine']['role']}"
        },
        "herald-executor": {value_name(values, "herald_executor")},
        "influxdb": {value_service_name(values, "influxdb")},
        "insider-api": {value_service_name(values, "insider_api")},
        "insider-scheduler": {value_name(values, "insider_scheduler")},
        "insider-worker": {value_name(values, "insider_worker")},
        "jira-bus": {value_service_name(values, "jira_bus")},
        "jira-ui": {value_service_name(values, "jira_ui")},
        "katara": {
            f"{value_name(values, 'katara_service')}"
            f"{values['katara_service']['api']['role']}",
            value_service_name(values, "katara_service"),
        },
        "katara-worker": {value_name(values, "katara_worker")},
        "keeper": {value_service_name(values, "keeper")},
        "keeper-executor": {value_name(values, "keeper_executor")},
        "layout-cleaner": {value_name(values, "layout_cleaner")},
        "live-demo-generator-worker": {
            f"{value_name(values, 'live_demo_generator')}-worker"
        },
        "live-demo-generator-scheduler": {
            f"{value_name(values, 'live_demo_generator')}-scheduler"
        },
        "mariadb": {value_service_name(values, "mariadb")},
        "metroculusapi": {value_service_name(values, "metroculus_api")},
        "metroculus-scheduler": {value_name(values, "metroculus_scheduler")},
        "metroculus-worker": {value_name(values, "metroculus_worker")},
        "minio": {value_service_name(values, "minio")},
        "mongo": {value_service_name(values, "mongo")},
        "ngui": {value_service_name(values, "ngui")},
        "organization-violations-worker": {
            f"{value_name(values, 'organization_violations')}-worker"
        },
        "organization-violations-scheduler": {
            f"{value_name(values, 'organization_violations')}-scheduler"
        },
        "power-schedule-worker": {
            f"{value_name(values, 'power_schedule')}-worker"
        },
        "power-schedule-scheduler": {
            f"{value_name(values, 'power_schedule')}-scheduler"
        },
        "rabbitmq": {value_service_name(values, "rabbitmq")},
        "redis": {value_service_name(values, "redis")},
        "report-import-scheduler-0": {
            f"{value_name(values, 'report_import_scheduler')}-0"
        },
        "report-import-scheduler-1": {
            f"{value_name(values, 'report_import_scheduler')}-1"
        },
        "report-import-scheduler-6": {
            f"{value_name(values, 'report_import_scheduler')}-6"
        },
        "report-import-scheduler-24": {
            f"{value_name(values, 'report_import_scheduler')}-24"
        },
        "resource-discovery-worker": {
            f"{value_name(values, 'resource_discovery')}-worker"
        },
        "resource-discovery-scheduler": {
            f"{value_name(values, 'resource_discovery')}-scheduler"
        },
        "resource-observer-worker": {
            f"{value_name(values, 'resource_observer')}-worker"
        },
        "resource-observer-scheduler": {
            f"{value_name(values, 'resource_observer')}-scheduler"
        },
        "resource-violations-worker": {
            f"{value_name(values, 'resource_violations')}-worker"
        },
        "resource-violations-scheduler": {
            f"{value_name(values, 'resource_violations')}-scheduler"
        },
        "restapi": {value_service_name(values, "rest_api")},
        "risp-scheduler": {value_name(values, "risp_scheduler")},
        "risp-worker": {value_name(values, "risp_worker")},
        "slacker": {value_service_name(values, "slacker")},
        "slacker-executor": {value_name(values, "slacker_executor")},
        "subspector": {value_service_name(values, "subspector")},
        "thanos-query": {value_service_name(values, "thanos_query")},
        "thanos-receive": {value_service_name(values, "thanos_receive")},
        "thanos-storegateway": {
            value_service_name(values, "thanos_storegateway")
        },
        "trapper-scheduler": {value_name(values, "trapper_scheduler")},
        "trapper-worker": {value_name(values, "trapper_worker")},
        "users-dataset-generator": {
            value_name(values, "users_dataset_generator")
        },
        "webhook-executor": {value_name(values, "webhook_executor")},
    }
    return names


@pytest.mark.parametrize("compose_file", COMPOSE_FILES, ids=lambda p: p.name)
def test_compose_file_is_valid_yaml(compose_file):
    load_compose(compose_file)


@pytest.mark.parametrize("compose_file", COMPOSE_FILES, ids=lambda p: p.name)
def test_docker_compose_config_is_valid(compose_file):
    if not shutil.which("docker"):
        pytest.skip("docker executable is not available")

    env = os.environ.copy()
    env.setdefault("DOCKER_BUILDKIT", "1")
    command = (
        "docker",
        "compose",
        "--env-file",
        str(ENV_FILE),
        "-f",
        str(compose_file),
        "config",
        "--quiet",
    )
    result = subprocess.run(
        command,
        cwd=COMPOSE_DIR,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_compose_variants_define_same_services_and_volumes():
    per_image = load_compose(COMPOSE_FILES[0])
    unified = load_compose(COMPOSE_FILES[1])

    assert set(unified["services"]) == set(per_image["services"])
    assert set(unified["volumes"]) == set(per_image["volumes"])


@pytest.mark.parametrize("compose_file", COMPOSE_FILES, ids=lambda p: p.name)
def test_first_party_compose_images_are_buildable_components(
    compose_file, components
):
    missing_components = {}
    for service, config in load_compose(compose_file)["services"].items():
        image = config.get("image", "")
        if image.startswith(EXTERNAL_IMAGE_PREFIXES):
            continue
        if not image.startswith(FIRST_PARTY_IMAGE_PREFIX):
            continue

        repository = image.removeprefix(FIRST_PARTY_IMAGE_PREFIX).split(
            ":", 1
        )[0]
        if repository not in components | FIRST_PARTY_REPOSITORY_EXCEPTIONS:
            missing_components[service] = repository

    assert missing_components == {}


@pytest.mark.parametrize("compose_file", COMPOSE_FILES, ids=lambda p: p.name)
def test_compose_services_have_k8s_equivalents(compose_file, values):
    compose_services = service_names(compose_file)
    equivalents = k8s_equivalent_names(values)

    unmapped_services = (
        compose_services - COMPOSE_ONLY_SERVICES - set(equivalents)
    )
    assert unmapped_services == set()

    empty_equivalents = {
        service: names
        for service, names in equivalents.items()
        if service in compose_services and not all(names)
    }
    assert empty_equivalents == {}

    stale_equivalents = set(equivalents) - compose_services
    assert stale_equivalents == set()


def test_report_import_compose_schedulers_match_k8s_periods(values):
    expected = {
        f"report-import-scheduler-{period}"
        for period in values["report_import_schedules"]
    }
    for compose_file in COMPOSE_FILES:
        actual = {
            service
            for service in service_names(compose_file)
            if service.startswith("report-import-scheduler-")
        }
        assert actual == expected
