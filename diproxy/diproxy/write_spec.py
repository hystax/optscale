import os.path
import re
import yaml
from apispec import APISpec, yaml_utils

import diproxy.diproxy.main as server

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# Spec reference:
# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md

OPENAPI_SPEC = """
swagger: '2.0'
info:
    description: >
        Diproxy API. Uses Kubernetes datasource username and password for
        authorization\n\n
    title: Diproxy API
    version: 1.0.0
securityDefinitions:
    basicAuth:
        type: basic
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

    for urlspec in server.get_handlers(dict()):
        path = re.sub(r"\(.*?<(.*?)>.*?\)", r"{\1}", urlspec[0])
        operations = dict()
        for method_name in yaml_utils.PATH_KEYS:
            method = getattr(urlspec[1], method_name)
            operation_data = yaml_utils.load_yaml_from_docstring(
                method.__doc__)
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
