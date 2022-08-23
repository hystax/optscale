import logging
import os

from optscale_exceptions.common_exc import NotFoundException
from rest_api_server.controllers.base import BaseController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from rest_api_server.models.models import CloudAccount

LOG = logging.getLogger(__name__)
SCRIPT_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                'recommendation_cleanup_scripts')


class CleanupScriptController(BaseController):
    def _get_model_type(self):
        return CloudAccount

    def get_script(self, cloud_account_id, module_name):
        ca = self.get(cloud_account_id)
        if ca is None:
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, cloud_account_id])
        try:
            script_path = '{}/{}/{}.sh'.format(SCRIPT_BASE_PATH,
                                               ca.type.value, module_name)
            with open(script_path, 'r') as f_script:
                data = f_script.read()
                script_user_dict = {
                    '###CLOUD_ACCOUNT_ID###': cloud_account_id,
                    '###CLOUD_ACCOUNT_NAME###': ca.name,
                    '###CLOUD_ACCOUNT_ACCOUNT_ID###': ca.account_id,
                    '###CLOUD_ACCOUNT_TYPE###': 'subscription_id' if ca.type.value == 'azure_cnr' else 'account_id'
                }
                for replacement_key, replacement_value in script_user_dict.items():
                    data = data.replace(replacement_key, str(replacement_value))
                return data
        except FileNotFoundError:
            raise NotFoundException(
                Err.OE0002, ['Module', module_name])


class CleanupScriptAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CleanupScriptController
