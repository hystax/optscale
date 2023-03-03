from aiohttp import client


class ClientV2:
    """
    ETCD async client for v2 API
    """

    def __init__(self, host: str = 'localhost', port: int = 2379):
        """
        TODO: user, pass, auth, headers
        :param host:
        :param port:
        """
        self.host = host
        self.port = port
        self.v = 'v2'

    @property
    def uri(self) -> str:
        return 'http://{host}:{port}'.format(
            host=self.host, port=self.port)

    def _k_uri(self, key) -> str:
        return '/'.join((self.uri, self.v, 'keys', key))

    async def get(self, key) -> dict:
        """
        Gets branch
        :param key:
        :return:
        """
        async with client.ClientSession(raise_for_status=True) as session:
            async with session.get(self._k_uri(key)) as response:
                return await response.json()

    async def get_value(self, key) -> str:
        node = await self.get(key)
        return node.get('node', {}).get('value')
