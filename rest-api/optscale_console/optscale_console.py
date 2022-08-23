#!/usr/bin/env python

import json

import requests
import yaml
import sys
import inspect
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from rest_api_client.client_v2 import Client as RestClient
from auth_client.client_v2 import Client as AuthClient
from report_client.client_v2 import Client as KeeperClient
from herald_client.client_v2 import Client as HeraldClient


class OptscaleConsole:
    def __init__(self, config_path='optscale_console.cfg'):
        with open(config_path, 'r') as config_file:
            self.config = json.load(config_file)
            dc_url = self.config["dc"]
            if dc_url == '':
                print('enter your dc url to config')
                sys.exit(1)
            auth_url = self.config["auth_url"]
            rest_url = self.config["rest_url"]
            if auth_url == '':
                auth_url = dc_url
            if rest_url == '':
                rest_url = dc_url
            email = self.config["email"]
            if email == '':
                print('enter your user to config')
                sys.exit(1)
            password = self.config["password"]
            if password == '':
                print('enter your password to config')
                sys.exit(1)
            token = self.config.get("token", '')
            secret = self.config.get("secret", '')

        self.clients = {
            'REST': RestClient(url=rest_url, token=token, secret=secret),
            'AUTH': AuthClient(url=auth_url, token=token),
            'KEEPER': KeeperClient(url=rest_url, token=token, secret=secret),
            'HERALD': HeraldClient(url=rest_url, token=token, secret=secret)
        }

        # Disable cert verification
        for client in self.clients.values():
            client._http_provider.session.verify = False

        self.methods = {
            key: dict() for key in self.clients
        }

        self.config_path = config_path

        for key in self.methods:
            self._load_methods(self.methods[key], self.clients[key])

    def _refresh_token(self):
        code, token = self.clients['AUTH'].token_get(
            self.config["email"], self.config["password"])
        token = token['token']

        for client in self.clients.values():
            client.token = token
        # save token in config file
        with open(self.config_path, 'w') as config_file:
            self.config["token"] = token
            json.dump(self.config, config_file, indent=4, sort_keys=True)

    def _is_method(self, client, field):
        attr = getattr(client, field)
        if not callable(attr):
            return False
        if field.startswith('_'):
            return False
        splitted = field.split('_')
        if len(splitted) < 2:
            return False
        method = splitted[-1]
        if method == 'url':
            return False
        return True

    @staticmethod
    def _parse_method(client, func):
        splitted = func.split('_')
        method = splitted[-1]
        entity = '_'.join(splitted[:-1])
        # entity, method = splitted
        func = getattr(client, func)
        sig = inspect.signature(func)
        args = list()
        kwargs = dict()
        for param in sig.parameters.values():
            if param.default == inspect.Parameter.empty:
                args.append(param.name)
            else:
                kwargs[param.name] = param.default
        # args = sig.parameters.keys()
        # args = func.__code__.co_varnames[1:]
        return entity, method, args, kwargs

    def _load_methods(self, methods, client):
        for field in dir(client):
            if self._is_method(client, field):
                entity, method, args, kwargs = self._parse_method(client, field)
                method_desc = {
                    "method": method,
                    "args": args,
                    "kwargs": kwargs,
                }
                if entity in methods:
                    methods[entity].append(method_desc)
                else:
                    methods[entity] = [method_desc]

    def _plans_to_yaml(self, response):
        if isinstance(response, dict):
            if 'plan' in response:
                response['plan'] = json.loads(response['plan'])
            if 'meta' in response and response['meta']:
                response['meta'] = json.loads(response['meta'])
            if len(response) == 1:
                for element in response.values():
                    self._plans_to_yaml(element)
        elif isinstance(response, list):
            for element in response:
                self._plans_to_yaml(element)

    @staticmethod
    def _on_error(exception):
        print(exception)
        sys.exit(1)

    def login(self, email, password):
        self.config["email"] = email
        self.config["password"] = password
        self._refresh_token()

    def get_client_type(self, entity):
        for client_type, methods in self.methods.items():
            if entity in methods:
                return client_type

    def get_client(self, entity):
        return self.clients[self.get_client_type(entity)]

    def get_methods(self, entity):
        return self.methods[self.get_client_type(entity)][entity]

    def call_method(self, entity, method, *args, **kwargs):
        rest_method = "%s_%s" % (entity, method)
        client = self.get_client(entity)
        try:
            code, response = getattr(
                client, rest_method)(*args, **kwargs)
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                self._refresh_token()
                try:
                    code, response = getattr(
                        client, rest_method)(*args, **kwargs)
                except Exception as e:
                    self._on_error(e)
            else:
                self._on_error(e)
        except Exception as e:
            self._on_error(e)
        if isinstance(response, str):
            return response
        else:
            self._plans_to_yaml(response)
            return yaml.dump(response, default_flow_style=False)

    def _print_entity_methods(self, entity):
        print(entity)
        for method_desc in self.get_methods(entity):
            print('\t', method_desc["method"])
            print('\t\t', ' '.join(method_desc["args"]))
            print('\t\t', ' '.join(
                "%s=%s" % (k, v) for k, v in method_desc["kwargs"].items()
            ))

    def list_entities(self):
        result = []
        for methods in self.methods.values():
            result.extend(methods.keys())
        return result

    def list_commands(self, entity=None):
        if entity:
            self._print_entity_methods(entity)
        else:
            for entity in self.list_entities():
                self._print_entity_methods(entity)


def yaml2js(input):
    loaded = yaml.load(input)
    return json.dumps(loaded)


def yaml2dict(input):
    loaded = yaml.load(input)
    return loaded


def parse_value(value):
    if value.startswith('yamltojson'):
        value = value[len('yamltojson'):]
        value = yaml2js(value)
        return value
    if value.startswith('yamltodict'):
        value = value[len('yamltodict'):]
        value = yaml2dict(value)
        return value
    try:
        # try to send ints, floats, booleans as their types instead of strings
        if isinstance(value, str):
            return json.loads(value)
    except json.decoder.JSONDecodeError:
        pass
    return value


def parse_args():
    params = sys.argv[1:]
    entity = params[0]
    method = params[1]
    params = params[2:]
    args = list()
    kwargs = dict()
    for param in params:
        if '=' in param:
            key, value = param.split('=')
            value = parse_value(value)
            kwargs[key] = value
        else:
            param = parse_value(param)
            args.append(param)
    return entity, method, args, kwargs


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    console = OptscaleConsole('optscale_console.cfg')

    if len(sys.argv) == 1:
        console.list_commands()
        return
    elif len(sys.argv) == 2:
        console.list_commands(sys.argv[1])
        return

    if sys.argv[1] == "login":
        _, _, email, password = sys.argv
        return console.login(email, password)

    entity, method, args, kwargs = parse_args()
    result = console.call_method(entity, method, *args, **kwargs)
    print(result)


if __name__ == "__main__":
    main()
