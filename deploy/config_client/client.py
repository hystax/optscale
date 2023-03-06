import os

import etcd
import logging
import subprocess
from retrying import retry

LOG = logging.getLogger(__name__)
ETCD_CODE_INTERNAL_ERROR = 300
CERTIFICATE_FOLDER = '/usr/local/share/ca-certificates/'
DEFAULT_RETRY_ARGS = dict(stop_max_attempt_number=300, wait_fixed=1000)
OBSERVE_TIMEOUT = 2 * 60 * 60


class RetriableException(Exception):
    pass


class ConcurrencyException(RetriableException):
    pass


class CounterOverflowException(Exception):
    pass


def _should_retry(exception):
    if isinstance(exception, (etcd.EtcdConnectionFailed, RetriableException)):
        return True
    if isinstance(exception, etcd.EtcdException):
        # internal error. appears on etcd service restart
        if exception.payload["errorCode"] == ETCD_CODE_INTERNAL_ERROR:
            return True
    return False


def _retry_not_exist(exception):
    return isinstance(exception, etcd.EtcdKeyNotFound)


class Client(etcd.Client):
    """ Acura config client """

    @retry(**DEFAULT_RETRY_ARGS, retry_on_exception=_should_retry)
    def api_execute(self, *args, **kwargs):
        return super().api_execute(*args, **kwargs)

    def read_branch(self, branch):
        """
        Read etcd branch and return content of it as a dict

        branch
            /parent/child1
            /parent/child2/grandchild
            /parent/child3
            /parent2

        will be returned as
            {
                'parent':
                    {
                        'child1': value,
                        'child2': {'grandchild': value}
                        'child3': value,
                    },
                'parent2': value,
            }
        :param branch:
        :return:
        """
        keys = self.read(branch, recursive=True)
        res_dict = {}
        for node in keys.children:
            parts = node.key.replace(branch, '', 1).lstrip('/').split('/')
            dict_node = res_dict
            for part in parts[:-1]:
                if part not in dict_node:
                    dict_node[part] = {}
                dict_node = dict_node[part]
            if node.dir:
                dict_node[parts[-1]] = {}
            else:
                dict_node[parts[-1]] = node.value
        LOG.debug("read %s from branch %s", res_dict, branch)
        return res_dict

    def read_list(self, branch):
        """
        list - branch of objects
            /smth/0000001
            /smth/0000004
        created by write(append=true)
        :return: list of objects
        """
        etcd_result = self.read(branch, recursive=True)
        return [child.value for child in etcd_result.children]

    def write_branch(self, branch, structure, overwrite_lists=False):
        """
        Recursive writing

        :param overwrite_lists: lists will be recreated before writing
        :param branch: etcd key name
        :param structure: dict, list or value
        """

        for key, value in structure.items():
            full_key = os.path.join(branch, key)
            if isinstance(value, dict):
                self.write_branch(branch=full_key, structure=value)
            elif isinstance(value, list):
                if overwrite_lists:
                    try:
                        self.delete(full_key, recursive=True)
                    except etcd.EtcdKeyNotFound:
                        pass
                for val in value:
                    self.write(key=full_key, value=val, append=True)
            else:
                LOG.debug("%s = %s", full_key, value)
                self.write(key=full_key, value=value)

    def update_structure(self, base_key, structure, remove_keys=False,
                         always_update=None):
        if always_update is None:
            always_update = []
        keys = self.read(base_key, recursive=False)
        children = [r.key.split('/')[-1] for r in keys.children]
        added = set(structure.keys()) - set(children)
        if remove_keys:
            removed = set(children) - set(structure.keys())
            for key in removed:
                full_key = os.path.join(base_key, key)
                LOG.info('removing %s key', full_key)
                self.delete(full_key, recursive=True)

        for key, value in structure.items():
            full_key = os.path.join(base_key, key)
            if isinstance(value, dict):
                if key in added or full_key in always_update:
                    LOG.info('writing branch %s', full_key)
                    self.write_branch(full_key, value)
                else:
                    self.update_structure(full_key, value, remove_keys=True,
                                          always_update=always_update)
            elif isinstance(value, list):
                pass
            else:
                if key in added or full_key in always_update:
                    LOG.info('added key %s', full_key)
                    self.write(key=full_key, value=value)

    def rest_db_params(self):
        """
        Get tuple with access args for my-db (restapi db)
        :return: ('username', 'password', 'host ip', 'db name')
        """
        params = self.read_branch('/restdb')
        return (params['user'], params['password'], params['host'],
                params['db'])

    def auth_db_params(self):
        """
        Get tuple with access args for auth db
        :return: ('username', 'password', 'host ip', 'db name')
        """
        params = self.read_branch('/authdb')
        return (params['user'], params['password'], params['host'],
                params['db'])

    def herald_db_params(self):
        """
        Get tuple with access args for herald db
        :return: ('username', 'password', 'host ip', 'db name')
        """
        params = self.read_branch('/heralddb')
        return (params['user'], params['password'], params['host'],
                params['db'])

    def katara_db_params(self):
        """
        Get tuple with access args for katara db
        :return: ('username', 'password', 'host ip', 'db name')
        """
        params = self.read_branch('/kataradb')
        return (params['user'], params['password'], params['host'],
                params['db'])

    def slacker_db_params(self):
        """
        Get tuple with access args for slacker db
        :return: ('username', 'password', 'host ip', 'db name')
        """
        params = self.read_branch('/slackerdb')
        return (params['user'], params['password'], params['host'],
                params['db'])

    def jira_bus_db_params(self):
        """
        Get tuple with access args for jira bus db
        :return: ('username', 'password', 'host ip', 'db name')
        """
        params = self.read_branch('/jirabusdb')
        return (params['user'], params['password'], params['host'],
                params['db'])

    def _get_url_from_branch(self, branch):
        """
        Generate service url from branch
            /snapman/host
            /snapman/port
        :param branch: service name
        :return: 'http://{host}:{port}'
        """
        return "http://{host}:{port}".format(**self.read_branch(branch))

    def restapi_url(self):
        """
        Url for restapi client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/restapi')

    def auth_url(self):
        """
        Url for auth client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/auth')

    def herald_url(self):
        """
        Url for herald client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/herald')

    def keeper_url(self):
        """
        Url for keeper client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/keeper')

    def arcee_url(self):
        """
        Url for arcee client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/arcee')

    def katara_url(self):
        """
        Url for katara client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/katara')

    def insider_url(self):
        """
        Url for insider client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/insider')

    def slacker_url(self):
        """
        Url for slacker client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/slacker')

    def jira_bus_url(self):
        """
        Url for jira bus client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/jira_bus')

    def storages(self):
        """
        Get list of mountpoint templates
        :return:
        """
        return self.read_list('/storages')

    @retry(**DEFAULT_RETRY_ARGS, retry_on_exception=_retry_not_exist)
    def wait_until_exist(self, key):
        """
        Retry EtcdKeyNotFound until key created
        :param key: key
        """
        self.read(key)

    def wait_configured(self):
        """
        Wait until cluster configured
        """
        LOG.info('Waiting until cluster initialization completed')
        self.wait_until_exist('/configured')

    def install_certificates(self):
        """
        takes all certificates from /certificates branch
        adds them to /usr/local/share/ca-certificates/ folder
        runs update-ca-certificates
        """
        try:
            certificates = self.read_branch('/certificates')
        except KeyError:
            return
        for cert_name, cert in certificates.items():
            with open(os.path.join(CERTIFICATE_FOLDER,
                                   '{0}.crt'.format(cert_name)), 'w') as f_cert:
                f_cert.write(cert)
        subprocess.run(['update-ca-certificates'], check=True)

    def cluster_secret(self):
        return self.get("/secret/cluster").value

    def agent_secret(self):
        return self.get("/secret/agent").value

    @retry(**DEFAULT_RETRY_ARGS, retry_on_exception=_should_retry)
    def increase_and_return(self, key, max_value=50000):
        """
        Increase counter value safely and return result
        Raises CounterOverflowException if counter exceeded
        :param max_value: max counter value. None for infinity
        :param key: key
        :return: new counter
        """
        try:
            counter = self.read(key)
            counter.value = int(counter.value) + 1
            if (max_value is not None) and (counter.value > max_value):
                LOG.error("Counter %s overflow! value: %s", key, counter.value)
                raise CounterOverflowException(key)
            self.update(counter)
            return int(counter.value)
        except ValueError:
            LOG.warning("Detected external change of %s key, retrying", key)
            raise ConcurrencyException(key)

    def get_new_cow_port(self):
        """
        Locks etcd, finds first port not in use, acquires it
        port key has 10s ttl for fatcow to start refreshing it
        :return: key name for acquired port, port value
        """
        port_branch = '/fatcow_ports'
        with etcd.Lock(self, 'fatcow_ports'):
            ports = sorted([int(x) for x in self.read_list(port_branch)])
            port_value = ports[-1] + 1
            for i, port in enumerate(ports):
                try:
                    if ports[i + 1] - ports[i] > 1:
                        port_value = ports[i] + 1
                        break
                except IndexError:
                    break
            return self.write(
                key=port_branch, value=port_value, append=True, ttl=180)

    def mongo_params(self):
        """
        Get tuple with access args for mongo db (report service)
        :return: ('user', 'pass', 'host', 'port', 'database')
        """
        params = self.read_branch('/mongo')
        return (params['user'], params['pass'], params['host'],
                params['port'], params['database'])

    def rabbit_params(self):
        """
        Get tuple with access args for rabbitmq
        :return: ('user', 'pass', 'host', 'port')
        """
        params = self.read_branch('/rabbit')
        return params['user'], params['pass'], params['host'], params['port']

    def events_queue(self):
        return self.get("/events_queue").value

    def tell_everybody_that_i_am_ready(self):
        open('/tmp/i_am_ready', 'w').close()

    def get_flag(self, flag_path, default_value=False):
        """
        Returns binary etcd key as boolean value
        """
        try:
            return bool(int(self.read(flag_path).value))
        except etcd.EtcdKeyNotFound:
            return default_value

    def public_ip(self):
        """
        Gets public ip of the cluster
        :return:
        """
        return self.get("/public_ip").value

    def katara_scheduler_timeout(self):
        """
        Gets katara periodic timeout in seconds
        """
        return int(self.get("/katara_scheduler_timeout").value)

    def optscale_email_recipient(self):
        """
        Gets optscale recipient for service emails
        :return:
        """
        result = self.read_branch("/optscale_service_emails")
        return result['recipient'] if result['enabled'] == 'True' else None

    def optscale_error_email_recipient(self):
        """
        Gets optscale recipient for service emails
        :return:
        """
        result = self.read_branch("/optscale_error_emails")
        return result['recipient'] if result['enabled'] == 'True' else (
            self.optscale_email_recipient())

    def google_calendar_service_key(self):
        """
        Gets Google calendar service account key
        :return:
        """
        return self.read_branch("/google_calendar_service/access_key")

    def google_calendar_service_enabled(self):
        """
        Gets Google calendar service support status
        :return:
        """
        return self.get("/google_calendar_service/enabled").value

    def metrics_influx_params(self):
        """
        Get tuple with access args for influx db
        :return: ('host', 'port', 'user', 'pass', 'database')
        """
        params = self.read_branch('/influxdb')
        return (params['host'], params['port'], params['user'],
                params['pass'], params['database'])

    def metroculus_url(self):
        """
        Url for metroculus client
        :return: 'http://<cluster_ip>:80'
        """
        return self._get_url_from_branch('/metroculus')

    def clickhouse_params(self):
        """
        Get tuple with access args for clickhouse db
        :return: ('username', 'password', 'host ip', 'db name')
        """
        params = self.read_branch('/clickhouse')
        return (params['user'], params['password'], params['host'],
                params['db'])

    def zoho_params(self):
        """
        Get tuple with args for registered app for OAuth2.0
        :return: ('email', 'client id', 'client secret', 'refresh token', 'redirect uri')
        """
        params = self.read_branch("/zohocrm")
        return (params['regapp_email'], params['regapp_client_id'], params['regapp_client_secret'],
                params['regapp_refresh_token'], params['regapp_redirect_uri'])

    def resource_discovery_params(self):
        """
        Get tuple with settings for resource discovery
        :return: ('discover_size', 'timeout', 'writing_timeout', 'observe_timeout')
        """
        try:
            params = self.read_branch('/resource_discovery_settings')
        except etcd.EtcdKeyNotFound:
            return None, None, None, OBSERVE_TIMEOUT
        try:
            discover_size = int(params['discover_size'])
        except (KeyError, ValueError):
            discover_size = None
        try:
            timeout = int(params['timeout'])
        except (KeyError, ValueError):
            timeout = None
        try:
            writing_timeout = int(params['writing_timeout'])
        except (KeyError, ValueError):
            writing_timeout = None
        try:
            observe_timeout = int(params['observe_timeout'])
        except (KeyError, ValueError):
            observe_timeout = OBSERVE_TIMEOUT
        return discover_size, timeout, writing_timeout, observe_timeout

    def domains_blacklist(self, blacklist_key='registration'):
        """
        Get list of email domains from /domains_blacklists/{blacklist_key} branch
        :param blacklist_key: blacklist etcd key name
        :return: list
        """
        blacklist_branch = 'domains_blacklists'
        return self.read_list("/{0}/{1}".format(blacklist_branch,
                                                blacklist_key))

    def thanos_remote_write_url(self):
        """
        Url to send prometheus metrics
        :return: 'http://<cluster_ip>:<port>/<path>'
        """
        return "http://{host}:{port}/{path}".format(
            **self.read_branch('/thanos_receive'))

    def thanos_query_url(self):
        """
        Url to get prometheus metrics
        :return: 'http://<cluster_ip>:<port>'
        """
        return self._get_url_from_branch('/thanos_query')
