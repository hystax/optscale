from optscale_client.aconfig_cl.aetcd2 import ClientV2


class AConfigCl(ClientV2):
    """
    Async Config client
    """

    async def read_branch(self, key, recursive=False):
        """
        TODO: implement recursive read
        Reads branch
        :param key:
        :param recursive:
        :return:
        """
        result = dict()
        a = await self.get(key)
        # TODO: check usage
        for node in a["node"]["nodes"]:
            k = node['key'].split(key)[-1].split('/')[-1]
            v = node.get('value')
            result[k] = v
        return result

    async def arcee_params(self):
        """
        Returns
        :return:
        """
        branch = await self.read_branch("/mongo")
        return (branch['user'], branch['pass'], branch['host'],
                branch['port'], 'arcee')

    async def bulldozer_params(self):
        """
        Returns
        :return:
        """
        branch = await self.read_branch("/mongo")
        return (branch['user'], branch['pass'], branch['host'],
                branch['port'], 'bulldozer')

    async def cluster_secret(self):
        return await self.get_value("/secret/cluster")
