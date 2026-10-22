"""Azure credential factory + cloud-account config extraction.

All Azure SDK calls in bumiworker use the track-2
`azure.identity.ClientSecretCredential`. The legacy track-1
`msrestazure.ServicePrincipalCredentials` is incompatible with modern
`azure-mgmt-*` SDKs, which require the TokenCredential `get_token`
protocol; calling e.g. `storage_accounts.list` with a track-1 cred
raises `'ServicePrincipalCredentials' object has no attribute
'get_token'`.

Note: a pre-existing OptScale `cloud_adapter` upstream bug constructs
SPNs as track-1 `ServicePrincipalCredentials` and passes them to
track-2 SDKs — same root cause, but UPSTREAM scope. Tracked separately
(see `.claude/refs/AZURE_OVERLAY.md`); out of scope for this module.
"""
import logging

LOG = logging.getLogger(__name__)


def make_credentials(tenant, client_id, secret):
    from azure.identity import ClientSecretCredential
    return ClientSecretCredential(
        tenant_id=tenant,
        client_id=client_id,
        client_secret=secret,
    )


def build_parent_account_map(cloud_accounts):
    """Map azure_tenant cloud account id -> config dict.

    Used so an azure_cnr child can fall back to its parent tenant's
    {tenant, client_id, secret} when the child's own config doesn't carry
    those (the common case where the SPN lives on the tenant connector).
    """
    parents = {}
    for ca in cloud_accounts:
        if ca.get('type') == 'azure_tenant':
            parents[ca['id']] = ca.get('config', {}) or {}
    return parents


def extract_cloud_account_creds(cloud_account, parent_account_map):
    """Return {subscription_id, tenant, client_id, secret} or None.

    Mirrors the overlay's `_get_azure_creds()` selection: the child's
    `config.subscription_id` is required; SPN tuple is taken from the
    parent azure_tenant config when present, otherwise from the child's
    own config. Returns None when any required key is absent.
    """
    cfg = cloud_account.get('config', {}) or {}
    sub_id = cfg.get('subscription_id')
    if not sub_id:
        return None
    parent_id = cloud_account.get('parent_id') or ''
    parent_cfg = parent_account_map.get(parent_id, {}) or {}
    creds = parent_cfg if parent_cfg else cfg
    if not all(k in creds for k in ('tenant', 'client_id', 'secret')):
        return None
    return {
        'subscription_id': sub_id,
        'tenant': creds['tenant'],
        'client_id': creds['client_id'],
        'secret': creds['secret'],
    }
