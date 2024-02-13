from mongomock_motor import AsyncMongoMockClient
from optscale_client.aconfig_cl.aconfig_cl import AConfigCl


DB_MOCK = AsyncMongoMockClient()['arcee']


class AConfigClMock(AConfigCl):

    async def arcee_params(self):
        return 'name', 'password', '127.0.0.1', 80, 'arcee'

    async def cluster_secret(self):
        return 'secret'
