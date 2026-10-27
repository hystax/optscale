"""migrate cloudaccount config from cryptocode to fernet

Revision ID: c1d4f7a92b08
Revises: 3f8a9c2b7d1e
Create Date: 2026-04-28

"""
import base64
import json
import logging
import os

import cryptocode
from alembic import op
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from sqlalchemy.sql import text

from optscale_client.config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = 'c1d4f7a92b08'
down_revision = '3f8a9c2b7d1e'
branch_labels = None
depends_on = None

LOG = logging.getLogger(__name__)

DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
FERNET_PREFIX = 'v2:'
FERNET_KDF_INFO = b'optscale-config-fernet-v1'
BATCH_SIZE = 500


def _etcd_salt():
    host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    port = int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT))
    return EtcdClient(host=host, port=port).encryption_salt()


def _build_fernet(master):
    if isinstance(master, str):
        master = master.encode('utf-8')
    derived = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=FERNET_KDF_INFO,
    ).derive(master)
    return Fernet(base64.urlsafe_b64encode(derived))


def _legacy_decode(salt, encoded):
    decrypted = cryptocode.decrypt(encoded, salt)
    if decrypted is False:
        raise ValueError('cryptocode.decrypt returned False (wrong salt?)')
    return json.loads(decrypted)


def _fernet_encode(fernet, config_dict):
    token = fernet.encrypt(json.dumps(config_dict).encode('utf-8')).decode('utf-8')
    return FERNET_PREFIX + token


def _iter_rows(conn):
    last_id = ''
    stmt = text(
        "SELECT id, config FROM cloudaccount "
        "WHERE config IS NOT NULL AND id > :last_id AND deleted_at = 0 "
        "ORDER BY id LIMIT :batch"
    )
    while True:
        rows = conn.execute(
            stmt, last_id=last_id, batch=BATCH_SIZE
        ).fetchall()
        if not rows:
            return
        yield rows
        last_id = rows[-1][0]


def upgrade():
    salt = _etcd_salt()
    fernet = _build_fernet(salt)
    LOG.warning(
        'migration salt: type=%s len=%s repr=%r',
        type(salt).__name__, len(salt), salt[:8] if salt else salt)

    conn = op.get_bind()
    update_stmt = text(
        "UPDATE cloudaccount SET config = :cfg WHERE id = :id"
    )
    migrated = skipped = failed = 0
    for rows in _iter_rows(conn):
        for row_id, cfg in rows:
            if not cfg or cfg.startswith(FERNET_PREFIX):
                skipped += 1
                continue
            try:
                plain = _legacy_decode(salt, cfg)
            except Exception:
                failed += 1
                continue
            new_cfg = _fernet_encode(fernet, plain)
            conn.execute(update_stmt, cfg=new_cfg, id=row_id)
            migrated += 1
    LOG.info(
        'cloudaccount config migration: migrated=%d skipped=%d failed=%d',
        migrated, skipped, failed)


def downgrade():
    salt = _etcd_salt()
    fernet = _build_fernet(salt)

    conn = op.get_bind()
    update_stmt = text(
        "UPDATE cloudaccount SET config = :cfg WHERE id = :id"
    )
    for rows in _iter_rows(conn):
        for row_id, cfg in rows:
            if not cfg or not cfg.startswith(FERNET_PREFIX):
                continue
            try:
                token = cfg[len(FERNET_PREFIX):].encode('utf-8')
                plain = json.loads(fernet.decrypt(token).decode('utf-8'))
            except InvalidToken:
                LOG.exception(
                    'Failed to decode v2 config for %s', row_id)
                continue
            legacy = cryptocode.encrypt(json.dumps(plain), salt)
            conn.execute(update_stmt, cfg=legacy, id=row_id)
