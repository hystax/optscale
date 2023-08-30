import datetime
import uuid

from requests.exceptions import HTTPError
from requests.models import Response
from unittest.mock import patch, PropertyMock

from rest_api.rest_api_server.controllers.infrastructure.base import get_cost
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.tests.unittests.test_profiling_base import ArceeMock


def get_http_error(code):
    resp = Response()
    resp.status_code = code
    return HTTPError(response=resp)


class TestInfrastructureBase(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseProfilingTokenController.arcee_client',
              new_callable=PropertyMock,
              return_value=ArceeMock(self.mongo_client)).start()
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseProfilingTokenController.bulldozer_client',
              new_callable=PropertyMock,
              return_value=BulldozerMock(self.mongo_client)).start()
        patch('rest_api.rest_api_server.controllers.infrastructure.base.'
              'BaseInfraController.insider_client',
              new_callable=PropertyMock,
              return_value=InsiderMock()).start()
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseProfilingTokenController.get_secret').start()
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()

        _, org = self.client.organization_create({'name': "organization"})
        self.organization_id = org['id']
        auth_user = str(uuid.uuid4())
        _, employee = self.client.employee_create(
            self.organization_id, {'name': 'name1',
                                   'auth_user_id': auth_user})
        self.employee_id = employee['id']
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user).start()
        user = {
            'id': auth_user,
            'display_name': 'default',
            'email': 'email@email.com',
        }
        patch('rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler._get_user_info',
              return_value=user).start()
        config = {
            'name': 'creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, cloud_acc = self.create_cloud_account(
            self.organization_id, config, auth_user_id=auth_user)
        self.cloud_account_id = cloud_acc['id']

        self.valid_goal = {
            'target_value': 0.7,
            'tendency': 'more',
            'name': 'loss',
            'key': 'loss',
            'function': 'avg'
        }
        _, goal = self.client.goal_create(
            self.organization_id, self.valid_goal)
        self.valid_application = {
            'name': 'Test project',
            'key': 'test_project',
            'goals': [goal['id']]
        }
        _, app = self.client.application_create(
            self.organization_id, self.valid_application)
        self.application_id = app['id']
        self.valid_template = {
            'name': 'Test project template',
            'application_ids': [self.application_id],
            'cloud_account_ids': [self.cloud_account_id],
            'region_ids': ['us-east-1', 'us-west-1'],
            'instance_types': ['p4', 'p3', 'p2', 'm5'],
            'budget': 1234,
            'name_prefix': 'test_prefix',
            'tags': {
                'template': 'test'
            },
            'hyperparameters': {
                'Model URL': 'MODEL_URL',
                'Dataset URL': 'DATASET_URL',
                'Learning rate': 'LEARNING_RATE'
            },
        }
        self.valid_runset = {
            'application_id': self.application_id,
            'cloud_account_id': self.cloud_account_id,
            'region_id': 'us-east-1',
            'instance_type': 'm5',
            'name_prefix': 'test_prefix',
            'commands': 'echo hello world',
            'tags': {
                'template': 'test'
            },
            'hyperparameters': {
                'MODEL_URL': 'https://example.com/model/url',
                'DATASET_URL': 'https://example.com/dataset/url',
                'LEARNING_RATE': '1'
            },
            'destroy_conditions': {
                "max_budget": self.valid_template['budget'],
                "reached_goals": True,
                "max_duration": 123456
            },
            'open_ingress': False,
            'spot_settings': {
                'tries': 3
            }
        }

    def _gen_executor(self, token, **kwargs):
        executor_id = kwargs.pop('_id', None)
        if not executor_id:
            executor_id = str(uuid.uuid4())
        executor = {
            '_id': str(uuid.uuid4()),
            'platform_type': 'aws',
            'instance_id': 'i-%s' % executor_id[:5],
            'account_id': executor_id[:5],
            'local_ip': '172.31.24.6',
            'public_ip': '3.123.31.120',
            'instance_lc': 'OnDemand',
            'instance_type': 't2.large',
            'instance_region': 'eu-central-1',
            'availability_zone': 'eu-central-1a',
            'token': token,
        }
        if kwargs:
            executor.update(kwargs)
        return executor

    def _gen_run(self, token, application_id, runset_id, executor_ids, **kwargs):
        run = {
            '_id': str(uuid.uuid4()),
            'application_id': application_id,
            'runset_id': runset_id,
            'start': 1665523835,
            'finish': 1665527774,
            'state': 2,
            'number': 1,
            'tags': {'key': 'value', 'project': 'regression'},
            'data': {'step': 2000, 'loss': 0.153899},
            'token': token,
            'name': 'awesome %s' % str(uuid.uuid4()),
            'imports': ["tf", "torch"]
        }
        if executor_ids:
            run['executors'] = executor_ids
        if kwargs:
            run.update(kwargs)
        return run

    def _create_run(self, organization_id, application_id, runset_id,
                    executor_ids=None, **kwargs):
        _, resp = self.client.profiling_token_get(organization_id)
        profiling_token = resp['token']
        if executor_ids:
            for executor_id in executor_ids:
                self.mongo_client.arcee.executors.insert_one(
                    self._gen_executor(profiling_token, instance_id=executor_id))
        run = self._gen_run(
            profiling_token, application_id, runset_id, executor_ids, **kwargs)
        self.mongo_client.arcee.runs.insert_one(run)
        return run


class InsiderMock:
    FLAVOR_TO_PRICE_MAP = {
        'm5.2xlarge': 0.273,
        'm5.xlarge': 0.224,
        'm5.large': 0.175,
    }
    TYPE_TO_SIZE_MAP = {
        'm5': ('m5.2xlarge', 'm5.xlarge', 'm5.large')
    }

    @staticmethod
    def _raise_http_error(code):
        raise get_http_error(code)

    def get_family_prices(
            self, cloud_type, instance_family, region, os_type=None,
            currency=None):
        sizes = self.TYPE_TO_SIZE_MAP[instance_family]
        if not sizes:
            self._raise_http_error(400)
        prices = []
        for size in sizes:
            price = self.FLAVOR_TO_PRICE_MAP.get(size)
            if not price:
                continue
            prices.append({
                'price': price,
                'region': region,
                'instance_family': instance_family,
                'instance_type': size,
                'operating_system': os_type,
                'price_unit': '1 hour',
                'currency': 'USD',
                'cpu': 4,
                'ram': 1740,
                'gpu': None
            })
        return 200, {'prices': prices}


class BulldozerMock:
    def __init__(self, mongo_cl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.infra_templates = mongo_cl.bulldozer.templates
        self.infra_runsets = mongo_cl.bulldozer.runsets
        self.infra_runners = mongo_cl.bulldozer.runners
        self._token = None
        self._runset_number = 1

    @staticmethod
    def _raise_http_error(code):
        resp = Response()
        resp.status_code = code
        raise HTTPError(response=resp)

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    def token_create(self, token):
        return 200, {}

    def template_create(self, name, application_ids, cloud_account_ids,
                        region_ids, instance_types, budget, name_prefix,
                        tags, hyperparameters):
        b = {
            "name": name,
            "application_ids": application_ids,
            "cloud_account_ids": cloud_account_ids,
            "region_ids": region_ids,
            "instance_types": instance_types,
            "budget": budget,
            "name_prefix": name_prefix,
            "tags": tags,
            "hyperparameters": hyperparameters,
            '_id': str(uuid.uuid4()),
            'token': self.token
        }
        inserted = self.infra_templates.insert_one(b)
        template = list(self.infra_templates.find(
            {'_id': inserted.inserted_id}))[0]
        return 201, template

    def templates_list(self):
        templates = list(self.infra_templates.find(
            {'token': self.token}))
        return 200, templates

    def template_get(self, id_):
        templates = list(self.infra_templates.find(
            {'token': self.token, '_id': id_}))
        if not templates:
            self._raise_http_error(404)
        return 200, templates[0]

    def template_update(
            self, id_, name=None, application_ids=None, cloud_account_ids=None,
            region_ids=None, instance_types=None, budget=None,
            name_prefix=None, tags=None, hyperparameters=None):
        b = dict()
        if name is not None:
            b.update({"name": name})
        if application_ids is not None:
            b.update({"application_ids": application_ids})
        if cloud_account_ids is not None:
            b.update({"cloud_account_ids": cloud_account_ids})
        if region_ids is not None:
            b.update({"region_ids": region_ids})
        if instance_types is not None:
            b.update({"instance_types": instance_types})
        if budget is not None:
            b.update({"budget": budget})
        if name_prefix is not None:
            b.update({"name_prefix": name_prefix})
        if tags is not None:
            b.update({"tags": tags})
        if hyperparameters is not None:
            b.update({"hyperparameters": hyperparameters})
        self.infra_templates.update_one(
            filter={
                '_id': id_,
                'token': self.token
            },
            update={'$set': b}
        )
        return 200, self.template_get(id_)[1]

    def template_delete(self, id_):
        runsets = list(self.infra_runsets.find(
            {'token': self.token, 'template_id': id_}))
        if runsets:
            self._raise_http_error(409)
        res = self.infra_templates.delete_one(
            {'token': self.token, '_id': id_})
        if res.deleted_count == 0:
            self._raise_http_error(404)
        return 204, None

    def runset_create(self, template_id, application_id, cloud_account_id,
                      region_id, instance_type, name_prefix, owner_id,
                      hyperparameters, tags, destroy_conditions, commands,
                      open_ingress=False, spot_settings=None):
        now = int(datetime.datetime.utcnow().timestamp())
        b = {
            "template_id": template_id,
            "application_id": application_id,
            "cloud_account_id": cloud_account_id,
            "region_id": region_id,
            "instance_type": instance_type,
            "owner_id": owner_id,
            "name_prefix": name_prefix,
            "tags": tags,
            "hyperparameters": hyperparameters,
            "destroy_conditions": destroy_conditions,
            '_id': str(uuid.uuid4()),
            'token': self.token,
            'commands': commands,
            'created_at': now - 120,
            'started_at': now - 100,
            'destroyed_at': now,
            'deleted_at': 0,
            'name': 'some name %s' % now,
            'number': self._runset_number,
            'spot_settings': spot_settings,
            'open_ingress': open_ingress
        }
        inserted = self.infra_runsets.insert_one(b)
        self._runset_number += 1
        runset = list(self.infra_runsets.find(
            {'_id': inserted.inserted_id}))[0]
        return 201, runset

    def runset_update(self, runset_id, state):
        b = dict()
        if state is not None:
            b.update({"state": state})
        self.infra_runsets.update_one(
            filter={
                '_id': runset_id,
                'token': self.token
            },
            update={'$set': b}
        )
        return 200, self.runset_get(runset_id)[1]

    def runset_get(self, id_):
        runsets = list(self.infra_runsets.find(
            {'token': self.token, '_id': id_}))
        if not runsets:
            self._raise_http_error(404)
        return 200, runsets[0]

    def runset_list(self, template_id):
        runsets = list(self.infra_runsets.find(
            {'token': self.token, 'template_id': template_id}))
        return 200, runsets

    def __generate_runners(self, runset_ids):
        now = int(datetime.datetime.utcnow().timestamp())
        runsets = list(self.infra_runsets.find({'_id': {'$in': runset_ids}}))
        # TODO: (am) complex runs generation based on runset hyperparameters
        inserted_ids = []
        for runset in runsets:
            duration = 100
            price = InsiderMock.FLAVOR_TO_PRICE_MAP[runset['instance_type']]
            b = {
                '_id': str(uuid.uuid4()),
                "runset_id": runset['_id'],
                "return_code": 0,
                "error_reason": None,
                "state": 8,  # destroyed
                "instance_id": 'i-9323123124',
                "instance_name": 'test_instance',
                "cloud_account_id": runset['cloud_account_id'],
                "token": self.token,
                "created_at": now - 120,
                "started_at": now - duration,
                "cost": get_cost(price, 100),
                'destroyed_at': now,
                'region_id': runset['region_id'],
                'instance_type': runset['instance_type']
            }
            inserted = self.infra_runners.insert_one(b)
            inserted_ids.append(inserted.inserted_id)
        runners = list(self.infra_runners.find(
            {'_id': {'$in': inserted_ids}}))
        return runners

    def runners_list(self, runset_id):
        # runners are generated by bulldozer worker.
        # So creating here something to return
        runners = list(self.infra_runners.find(
            {'token': self.token, 'runset_id': runset_id}))
        if not runners:
            runners = self.__generate_runners([runset_id])
        return 200, runners

    def runners_bulk_get(self, runset_ids):
        runners = list(self.infra_runners.find(
            {'token': self.token, 'runset_id': {'$in': runset_ids}}))
        if not runners:
            runners = self.__generate_runners(runset_ids)
        return 200, runners
