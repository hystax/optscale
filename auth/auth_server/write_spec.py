import yaml
import os.path
import re
import json
import auth.auth_server.server as server
from apispec import APISpec, utils
from tornado.template import Template

# Spec reference:
# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md

OPENAPI_SPEC = """
swagger: '2.0'
info:
    description: >
        OptScale Auth API. Call `POST` `/auth/v2/tokens` with `{"email": "<email>",
        "password": "<password>"}` body to receive an authorization token and
        use `Bearer <token>` string in `Authorization` header to authorize.
    title: Auth
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
    settings = yaml.load(OPENAPI_SPEC)
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
    spec_advanced = APISpec(
        title=title,
        version=spec_version,
        openapi_version=openapi_version,
        plugins=(),
        **settings
    )

    for urlspec in server.get_handlers(dict()):
        path = re.sub(r"\(.*?<(.*?)>.*?\)", r"{\1}", urlspec[0])
        operations = dict()
        operations_advanced = dict()
        for method_name in utils.PATH_KEYS:
            method = getattr(urlspec[1], method_name)
            operation_data = utils.load_yaml_from_docstring(method.__doc__)
            if operation_data:
                hidden = operation_data.pop('x-hidden', False)
                if not hidden:
                    operations[method_name] = operation_data
                operations_advanced[method_name] = operation_data
        if len(operations) > 0:
            spec.add_path(path=path, operations=operations)
        if len(operations_advanced) > 0:
            spec_advanced.add_path(path=path, operations=operations_advanced)
        else:
            print("Warning: docstrings for '" + urlspec[0] + "' are not found")

    # Api spec files
    with open(os.path.join(server.SWAGGER_PATH, "spec.yaml"), "w") as file:
        file.write(spec.to_yaml())
    with open(os.path.join(server.SWAGGER_PATH, "spec_advanced.yaml"), "w") as file:
        file.write(spec_advanced.to_yaml())


if __name__ == "__main__":
    main()
