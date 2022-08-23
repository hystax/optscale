import json
import logging

from optscale_exceptions.common_exc import WrongArgumentsException
from sqlalchemy.exc import IntegrityError

from jira_bus_server.controllers.base import (BaseController,
                                              BaseAsyncControllerWrapper)
from jira_bus_server.exceptions import Err
from jira_bus_server.models.models import (AppInstallation)

LOG = logging.getLogger(__name__)


class AppLifecycleController(BaseController):
    def installed(self, payload):
        try:
            client_key = payload.pop('clientKey')
            shared_secret = payload.pop('sharedSecret')
        except KeyError:
            raise WrongArgumentsException(Err.OJ0013, [])

        app_installation = self._get_app_installation_by_client_key(
            client_key, raise_not_found=False) or AppInstallation()
        app_installation.client_key = client_key
        app_installation.shared_secret = shared_secret
        app_installation.extra_payload = json.dumps(payload)

        self.session.add(app_installation)
        try:
            self.session.commit()
        except IntegrityError as exc:
            LOG.exception('Unable to save installation data: %s', exc)
            raise


class AppLifecycleAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AppLifecycleController
