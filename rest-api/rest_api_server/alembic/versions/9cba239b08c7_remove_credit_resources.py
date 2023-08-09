""""remove_credit_resources"

Revision ID: 9cba239b08c7
Revises: db6f2740ff70
Create Date: 2022-11-22 11:10:44.476859

"""
import os
import logging
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from pymongo import MongoClient
from sqlalchemy import Integer, select, String, and_

# revision identifiers, used by Alembic.
revision = '9cba239b08c7'
down_revision = 'db6f2740ff70'
branch_labels = None
depends_on = None


LOG = logging.getLogger(__name__)


def get_mongo_client():
    mongo_conn_string = "mongodb://localhost:27017/humalect-local-main"
    return MongoClient(mongo_conn_string)


def get_cloud_account_ids():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_t = table('organization',
                      column('id', String(36)),
                      column('deleted_at', Integer()),
                      column('is_demo', Integer()))
        c_acc_t = table('cloudaccount',
                        column('id', String(36)),
                        column('deleted_at', Integer()),
                        column('organization_id', String(36)),
                        column('type', String(36)))
        cmd = select([c_acc_t.c.id]).where(
            and_(c_acc_t.c.organization_id.in_(
                    select([org_t.c.id]).where(
                        and_(org_t.c.deleted_at == 0,
                             org_t.c.is_demo.is_(False)))),
                 c_acc_t.c.type == 'AWS_CNR',
                 c_acc_t.c.deleted_at == 0))
        cloud_accounts = session.execute(cmd)
    finally:
        session.close()
    return cloud_accounts


def upgrade():
    mongo_cl = get_mongo_client()
    cloud_accounts = list(get_cloud_account_ids())
    for i, cloud_account in enumerate(cloud_accounts):
        LOG.info('Started deleting resources for '
                 'cloud account {0} ({1}/{2})'.format(
                     cloud_account['id'], i + 1, len(cloud_accounts)))
        cloud_resources = mongo_cl.restapi.raw_expenses.aggregate([
            {'$match': {
                'cloud_account_id': cloud_account['id'],
                'lineItem/LineItemType': 'Credit'}},
            {'$project': {'lineItem/LineItemDescription': 1, '_id': 0}}])
        cloud_resource_ids = set(x['lineItem/LineItemDescription']
                                 for x in cloud_resources)
        mongo_cl.restapi.resources.delete_many({
            'cloud_account_id': cloud_account['id'],
            'cloud_resource_id': {'$in': list(cloud_resource_ids)}
        })


def downgrade():
    pass
