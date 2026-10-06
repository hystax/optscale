from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional

from zcrmsdk.src.com.zoho.crm.api.dc import USDataCenter, DataCenter


LOG = logging.getLogger(__name__)


@dataclass(eq=False)
class RegisteredApp:
    email: str
    client_id: str
    client_secret: str
    ref_token: str
    env: DataCenter.Environment
    redirect_uri: str

    @staticmethod
    def get_from_config(config_client) -> Optional[RegisteredApp]:
        try:
            (
                email,
                client_id,
                client_secret,
                ref_token,
                redirect_uri,
            ) = config_client.zoho_params()
        except Exception as e:
            LOG.error("Zoho: Couldn't get etcd params for zoho client: %s",
                      str(e))
            return None
        return RegisteredApp(
            email=email,
            client_id=client_id,
            client_secret=client_secret,
            ref_token=ref_token,
            env=USDataCenter.PRODUCTION(),
            redirect_uri=redirect_uri,
        )
