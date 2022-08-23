import os.path
import re

import yaml
from apispec import APISpec, yaml_utils

import jira_bus_server.server as server

# Spec reference:
# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md

OPENAPI_SPEC = """
swagger: '2.0'
info:
    description: >
        Jira Bus API. Only optscale-specific APIs covered.\n\n
        Permission definitions: \n\n
        -   `CLUSTER_SECRET`: Private API, used inside the cluster by services
        with special secret key\n\n
        -   `TOKEN`: Valid OptScale token required.\n\n
        -   `ATLASSIAN`: Valid JWT token from Atlassian required.\n\n
        -   `ATLASSIAN_ASYMMETRIC`: Valid asymmetric JWT token from Atlassian
        required.\n\n
    title: Jira Bus API
    version: 1.0.0
securityDefinitions:
    token:
        in: header
        name: 'Authorization'
        type: apiKey
    secret:
        in: header
        name: 'Secret'
        type: apiKey
"""


def main():
    settings = yaml.safe_load(OPENAPI_SPEC)
    title = settings['info'].pop('title')
    spec_version = settings['info'].pop('version')
    openapi_version = settings.pop('swagger')
    spec = APISpec(
        title=title,
        version=spec_version,
        openapi_version=openapi_version,
        plugins=(),
        **settings
    )

    for urlspec in sorted(server.get_handlers({}),
                          key=lambda urlspec: urlspec[0]):
        path = re.sub(r"\(.*?<(.*?)>.*?\)", r"{\1}", urlspec[0])
        operations = {}
        for method_name in yaml_utils.PATH_KEYS:
            method = getattr(urlspec[1], method_name)
            operation_data = yaml_utils.load_yaml_from_docstring(method.__doc__)
            if operation_data:
                operations[method_name] = operation_data
        if len(operations) > 0:
            spec.path(path=path, operations=operations)
        else:
            print("Warning: docstrings for '" + urlspec[0] + "' are not found")

    # Api spec file
    with open(os.path.join(server.SWAGGER_PATH, "spec.yaml"), "w") as file:
        file.write(spec.to_yaml())


if __name__ == "__main__":
    main()
