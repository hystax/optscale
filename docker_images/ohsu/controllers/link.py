import logging
import os.path
import socket
import subprocess
import time
from datetime import datetime
from docker_images.ohsu.controllers.base import BaseController
from docker_images.ohsu.controllers.base_async import BaseAsyncControllerWrapper
from docker_images.ohsu.exceptions import Err
from tools.optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from requests.exceptions import HTTPError


LOG = logging.getLogger(__name__)

BASE_SHS_CONF = 'spark-defaults.conf'
MINIO_BASE_PATH = 's3a://spark-logs'
SPARK_DAEMON_CMD = '/opt/spark/sbin/spark-daemon.sh'
SHS_CLASS = 'org.apache.spark.deploy.history.HistoryServer'
SHS_CONF_DIR = '/opt/spark/conf/'
SHS_LOG_DIR = '/opt/spark/logs/'
SHS_PID_FILE_PATH = '/tmp/spark--org.apache.spark.deploy.history.HistoryServer-{}.pid'
SHS_LOG_FILE = 'spark--org.apache.spark.deploy.history.HistoryServer-{0}-{1}.out'
SHS_START_TIMEOUT = 30


class SHSStartException(Exception):
    pass


class SHSLinkController(BaseController):
    @staticmethod
    def _get_default_conf():
        with open(SHS_CONF_DIR + BASE_SHS_CONF, 'r') as f:
            data = f.read()
        return data

    def _create_or_get_conf_file_path(self, organization_id):
        """Gets or creates configuration file to start history server.
        Configuration file consist of base configuration and a folder where
        spark logs will be saved"""
        conf_data = self._get_default_conf()
        spark_logs_folder = f'{MINIO_BASE_PATH}/{organization_id}/'
        conf_data += f'\nspark.history.fs.logDirectory    {spark_logs_folder}'
        filepath = SHS_CONF_DIR + organization_id
        if not os.path.exists(filepath):
            with open(filepath, 'a+') as f:
                f.write(conf_data)
        return filepath

    @staticmethod
    def _remove_file(filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
        LOG.info(f'SHS config {filepath} was removed')

    @staticmethod
    def _get_shs_port(organization_id):
        hostname = socket.gethostname()
        log_file_path = SHS_LOG_DIR + SHS_LOG_FILE.format(
            organization_id, hostname)
        LOG.info(log_file_path)
        port_str = "Successfully started service 'HistoryServerUI' on port "

        # spark history server needs some time to start and save logs
        start_ts = int(datetime.utcnow().timestamp())
        while int(datetime.utcnow().timestamp()) < (
                start_ts + SHS_START_TIMEOUT):
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as f:
                    data = f.read()
                start_index = data.find(port_str)
                if start_index != -1:
                    LOG.info(data)
                    start_index += len(port_str)
                    end_index = data.find('.', start_index)
                    port = int(data[start_index:end_index])
                    break
                else:
                    time.sleep(1)
            else:
                time.sleep(1)
        else:
            raise SHSStartException('Timeout waiting for SHS port')
        return port

    @staticmethod
    def _start_history_server(config_file_path, organization_id):
        LOG.info('Starting SHS')
        try:
            result = subprocess.Popen([
                SPARK_DAEMON_CMD, 'start', SHS_CLASS, organization_id,
                '--properties-file', f'{config_file_path}'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = result.communicate()
            LOG.debug(f'Output: {output}')
            LOG.debug(f'Error: {error}')
            if error:
                raise SHSStartException(
                    f'Error staring history server: {error}')
        except subprocess.CalledProcessError as exc:
            output = exc.output.decode()
            raise SHSStartException(
                f'Error staring history server: {output}')

    @staticmethod
    def _shs_pid(organization_id):
        """Gets history server pid from pid file"""
        pid_file = SHS_PID_FILE_PATH.format(organization_id)
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                pid = f.read()
            return int(pid)
        return None

    def _get_app_link(self, app_id, organization_id):
        public_ip = self.config.public_ip()
        shs_port = self._get_shs_port(organization_id)
        if not shs_port:
            raise Exception('Spark History Server port not found')
        link = f'http://{public_ip}:{shs_port}/history/{app_id}/jobs'
        LOG.info(f'link: {link}')
        return {'link': link}

    def _check_organization(self, organization_id):
        rest_cl = RestClient(self.config.public_ip(),
                             secret=self.config.cluster_secret(),
                             verify=False)
        try:
            rest_cl.organization_get(organization_id)
        except HTTPError:
            raise NotFoundException(Err.OHE0004, ['organization_id'])

    def get(self, organization_id, **body):
        app_id = body.get('app_id')
        if not app_id:
            raise WrongArgumentsException(Err.OHE0005, ['app_id'])
        self._check_organization(organization_id)
        conf_file = self._create_or_get_conf_file_path(organization_id)
        if not self._shs_pid(organization_id):
            self._start_history_server(conf_file, organization_id)
        return self._get_app_link(app_id, organization_id)

    def delete(self, organization_id):
        self._check_organization(organization_id)
        pid = self._shs_pid(organization_id)
        if pid:
            result = subprocess.Popen([
                SPARK_DAEMON_CMD, 'stop', SHS_CLASS, organization_id],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = result.communicate()
            LOG.debug(f'Output: {output}')
            LOG.debug(f'Error: {error}')

            shs_config = SHS_CONF_DIR + organization_id
            self._remove_file(shs_config)

            hostname = socket.gethostname()
            shs_log = SHS_LOG_DIR + SHS_LOG_FILE.format(
                organization_id, hostname)
            self._remove_file(shs_log)
        else:
            LOG.warning(f'SHS process for organization {organization_id} is '
                        f'already dead')


class SHSLinkAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return SHSLinkController
