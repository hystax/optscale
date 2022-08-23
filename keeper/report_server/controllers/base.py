from auth_client.client_v2 import Client as AuthClient
from requests import HTTPError
from mongoengine.errors import ValidationError
from optscale_exceptions.common_exc import (UnauthorizedException,
                                            WrongArgumentsException)

from report_server.exceptions import Err


class BaseController(object):

    def __init__(self, mongo_client, config, rabbit_client):
        self.mongo_client = mongo_client
        self._config = config
        self.rabbit_client = rabbit_client
        self.auth_client = AuthClient(url=config.auth_url())

    @staticmethod
    def _list(action_resources, entity, action):
        return list(map(lambda x: x[1],
                        filter(lambda x: x[0] == entity,
                               action_resources[action])))

    def get_resources(self, token, action):
        """
        get permitted resources list from Auth
        :param token:
        :param action:
        :return:
        """
        self.auth_client.token = token
        try:
            _, action_resources = self.auth_client.action_resources_get(
                [action])
            organizations = self._list(action_resources, 'organization', action)
        except HTTPError as exc:
            if exc.response.status_code == 401:
                raise UnauthorizedException(Err.OK0003, [])
            raise
        return organizations

    @staticmethod
    def raise_from_validation_error(exc):
        """
        Raise an OptScale exception from mongo validation error
        :type exc: ValidationError
        """
        def flatten_dict(nested_dict, sep='.', prefix=''):
            flat_dict = {}
            for k, v in nested_dict.items():
                new_key = '{}{}{}'.format(prefix, sep, k) if prefix else str(k)
                if isinstance(v, dict):
                    flat_dict.update(flatten_dict(v, sep, new_key))
                else:
                    flat_dict[new_key] = v
            return flat_dict

        errors_dict = flatten_dict(exc.to_dict())
        error_str = ', '.join(
            ('{} ({})'.format(k, v) for k, v in errors_dict.items()))
        raise WrongArgumentsException(
            Err.OK0044, [error_str])
