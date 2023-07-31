from rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api_server.tests.unittests.test_infrastructure_base import BulldozerMock
from rest_api_server.tests.unittests.test_profiling_base import ArceeMock
from rest_api_server.models.db_factory import DBFactory, DBType
from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.models import ProfilingToken
from unittest.mock import patch, PropertyMock


class TestInfraProfilingTokensApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api_server.controllers.base.'
              'BaseProfilingTokenController.arcee_client',
              new_callable=PropertyMock,
              return_value=ArceeMock(self.mongo_client)).start()
        patch('rest_api_server.controllers.base.'
              'BaseProfilingTokenController.bulldozer_client',
              new_callable=PropertyMock,
              return_value=BulldozerMock(self.mongo_client)).start()
        _, self.org = self.client.organization_create({'name': "organization"})

    @staticmethod
    def _get_db_profiling_tokens(org_id):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        tokens = session.query(ProfilingToken).filter(
            ProfilingToken.organization_id == org_id,
            ProfilingToken.deleted.is_(False)
        ).all()
        return tokens

    def test_get(self):
        tokens = self._get_db_profiling_tokens(self.org['id'])
        self.assertEqual(len(tokens), 0)
        # create on get
        code, _ = self.client.profiling_token_get(self.org['id'])
        self.assertEqual(code, 200)
        tokens = self._get_db_profiling_tokens(self.org['id'])
        token = tokens[0]
        code, res = self.client.profiling_token_by_infrastructure_token_get(
            token.infrastructure_token)
        self.assertEqual(code, 200)
        self.assertEqual(token.token, res.get('token'))

    def test_create_on_another_api(self):
        tokens = self._get_db_profiling_tokens(self.org['id'])
        self.assertEqual(len(tokens), 0)
        self.client.application_list(self.org['id'])
        tokens = self._get_db_profiling_tokens(self.org['id'])
        self.assertEqual(len(tokens), 1)
        token = tokens[0]
        code, res = self.client.profiling_token_by_infrastructure_token_get(
            token.infrastructure_token)
        self.assertEqual(code, 200)
        self.assertEqual(token.token, res.get('token'))

    def test_error_on_create(self):
        tokens = self._get_db_profiling_tokens(self.org['id'])
        self.assertEqual(len(tokens), 0)
        with patch('rest_api_server.controllers.base.'
                   'BaseProfilingTokenController.'
                   '_create_bulldozer_token',
                   side_effect=Exception('Bulldozer error')):
            code, resp = self.client.profiling_token_get(self.org['id'])
            self.assertEqual(code, 500)
            tokens = self._get_db_profiling_tokens(self.org['id'])
            self.assertEqual(len(tokens), 0)
        self.test_get()
