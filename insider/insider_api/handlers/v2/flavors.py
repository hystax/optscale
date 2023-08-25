import json
import logging
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  UnauthorizedException,
                                                  NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError

from insider.insider_api.controllers.flavor import FlavorAsyncController
from insider.insider_api.exceptions import Err
from insider.insider_api.handlers.v2.base import SecretHandler
from insider.insider_api.utils import ModelEncoder

LOG = logging.getLogger(__name__)


class FlavorsHandler(SecretHandler):
    def _get_controller_class(self):
        return FlavorAsyncController

    @staticmethod
    def validate_parameters(params):
        required_params = [('cloud_type', str),
                           ('resource_type', str),
                           ('family_specs', dict),
                           ('mode', str)]

        optional_params = [('os_type', str),
                           ('preinstalled', str),
                           ('meter_id', str),
                           ('currency', str),
                           ('cloud_account_id', str)]

        mode_params = {
            'current': [],
            'search_relevant': [('cpu', int)],
            'search_no_relevant': [('cpu', int)]
        }

        family_specs_params = {
            'aws_cnr': {
                'instance': [('source_flavor_id', str)],
            },
            'azure_cnr': {
                'instance': [('source_flavor_id', str)],
            },
            'alibaba_cnr':  {
                'instance': [('source_flavor_id', str)],
                'rds_instance': [('zone_id', str), ('category', str),
                                 ('engine', str), ('engine_version', str),
                                 ('storage_type', str),
                                 ('source_flavor_id', str)]
            },
            'gcp_cnr': {
                'instance': [('source_flavor_id', str)],
            },
            'nebius': {
                'instance': [('source_flavor_id', str),
                             ('cpu_fraction', int),
                             ('ram', int)],
                'rds_instance': [('source_flavor_id', str),
                                 ('category', int),
                                 ('platform_name', int)],
            },
        }

        cloud_required_params = {
            'aws_cnr': [('region', str)],
            'azure_cnr': [('region', str)],
            'alibaba_cnr': [('region', str)],
            'gcp_cnr': [('region', str)]
        }

        if not isinstance(params, dict):
            raise OptHTTPError(400, Err.OI0004, [])

        cloud_type = params.get('cloud_type')
        mode = params.get('mode')
        required_params.extend(mode_params.get(mode, []))
        required_params.extend(cloud_required_params.get(cloud_type, []))
        missing_required = [
            p for p, _ in required_params if params.get(p) is None
        ]
        if missing_required:
            message = ', '.join(missing_required)
            raise OptHTTPError(400, Err.OI0011, [message])

        all_params = required_params + optional_params
        for param, param_type in all_params:
            value = params.get(param)
            if value is not None and not isinstance(value, param_type):
                raise OptHTTPError(400, Err.OI0008, [param])

        if mode not in mode_params:
            raise OptHTTPError(400, Err.OI0008, ['mode'])

        if cloud_type not in family_specs_params:
            raise OptHTTPError(400, Err.OI0010, [cloud_type])

        meter_id = params.get('meter_id')
        if meter_id and cloud_type != 'azure_cnr':
            raise OptHTTPError(400, Err.OI0016, [cloud_type, 'meter_id'])

        preinstalled = params.get('preinstalled')
        if preinstalled and cloud_type != 'aws_cnr':
            raise OptHTTPError(400, Err.OI0016, [cloud_type, 'preinstalled'])

        resource_type = params.get('resource_type')
        if resource_type not in family_specs_params[cloud_type]:
            raise OptHTTPError(400, Err.OI0013, [resource_type, cloud_type])

        missing_family_params = [
            p for p, _ in family_specs_params[cloud_type][resource_type]
            if params['family_specs'].get(p) is None
        ]
        if missing_family_params:
            message = ', '.join(f'family_specs.{p}'
                                for p in missing_family_params)
            raise OptHTTPError(400, Err.OI0011, [message])

        unexpected_params = params['family_specs'].copy()
        for p, _ in family_specs_params[cloud_type][resource_type]:
            unexpected_params.pop(p, None)
        if unexpected_params:
            message = ', '.join(f'family_specs.{p}'
                                for p in unexpected_params.keys())
            raise OptHTTPError(400, Err.OI0014, [message])

    async def post(self, **kwargs):
        """
        ---
        tags: [flavors]
        summary: Returns suitable flavor
        description: |
            Returns suitable flavor
            Required permission: cluster secret
        parameters:
        -   in: body
            name: body
            description: Flavor search parameters
            required: true
            schema:
                type: object
                required: [cloud_type, resource_type, cpu, family_specs]
                properties:
                    cloud_type: {type: string,
                        description: "cloud type (aws_cnr, azure_cnr,
                        alibaba_cnr, gcp_cnr, nebius)"}
                    cloud_account_id: {type: string,
                        description: "id of cloud account to use credentials from,
                        if not set service credentials are used"}
                    resource_type: {type: string,
                        description: "resource type (instance, rds_instance)"}
                    region: {type: string,
                        description: "region name (not required for 'nebius')"}
                    family_specs: {type: object,
                        description: "flavor family specifications, contents
                        may be different for different clouds and resource
                        types. For `instance` resource type, try setting
                        `source_flavor_id` key with source flavor ID value"}
                    mode: {type: string,
                        description: "search mode (current,
                        search_relevant, search_no_relevant)"}
                    os_type: {type: string, enum: [Linux, Windows],
                       description: "The price for the flavor is calculated
                       for this os (AWS only), default - Linux"}
                    preinstalled: {type: string,
                       enum: [NA, SQL Web, SQL Std, SQL Ent],
                       description: "The price for flavor takes into account
                       this pre-installed software, default - NA (AWS only)"}
                    cpu: {type: integer,
                        description: "number of cpu in desired flavor
                        (for `search_*` modes)"}
                    meter_id: {type: string,
                        description: "Pricing meter id (Azure only)"}
                    currency: {type: string,
                        description: "Flavor price currency"}
        responses:
            200:
                description: suitable flavor info
                schema:
                    type: object
                    example:
                        cpu: 4
                        ram: 8192
                        flavor: t4.medium
                        price: 0.05
            400:
                description: |
                    Wrong arguments:
                    - OI0008: Invalid cloud_type / pricing_id
                    - OI0010: Cloud is not supported
                    - OI0011: Required argument is not provided
                    - OI0012: Region is not available
                    - OI0013: Resource type is not supported for cloud
                    - OI0016: Cloud does not support parameter
            404:
                description: |
                    Not Found:
                    - OI0009: Discovery not found
            401:
                description: |
                    Unauthorized:
                    - OI0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OI0005: Bad secret
                    - OI0017: Unexpected response from cloud
        security:
        - secret: []
        """
        self.check_cluster_secret()
        params = self._request_body()
        LOG.info('Received flavor search parameters: %s', params)
        self.validate_parameters(params)
        try:
            res = await self.controller.find_flavor(**params)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.set_status(200)
        self.write(json.dumps(res, cls=ModelEncoder))
