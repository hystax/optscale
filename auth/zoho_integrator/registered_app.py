# Registered OAuth app params
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional


from zcrmsdk.src.com.zoho.crm.api.dc import USDataCenter, DataCenter
from optscale_client.config_client.client import Client as ConfigClient
from etcd import EtcdKeyError


ETCD_EMAIL_KEY = "regapp_email"
ETCD_CLIENT_ID_KEY = "regapp_client_id"
ETCD_CLIENT_SECRET_KEY = "regapp_client_secret"
ETCD_REFRESH_TOKEN_KEY = "regapp_refresh_token"
ETCD_REDIRECT_URI_KEY = "regapp_redirect_uri"

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
    def get_from_etcd(config_client: ConfigClient) -> Optional[RegisteredApp]:
        try:
            (
                email,
                client_id,
                client_secret,
                ref_token,
                redirect_uri,
            ) = config_client.zoho_params()
        except EtcdKeyError:
            LOG.error(f"Couldn't get etcd params for zoho client")
            return None
        return RegisteredApp(
            email=email,
            client_id=client_id,
            client_secret=client_secret,
            ref_token=ref_token,
            env=USDataCenter.PRODUCTION(),
            redirect_uri=redirect_uri,
        )
