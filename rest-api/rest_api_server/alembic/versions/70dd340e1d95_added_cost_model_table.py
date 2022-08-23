""""added_cost_model_table"

Revision ID: 70dd340e1d95
Revises: 3935dc2d97db
Create Date: 2021-08-08 15:46:31.693566

"""
import json
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update

# revision identifiers, used by Alembic.
revision = '70dd340e1d95'
down_revision = '3935dc2d97db'
branch_labels = None
depends_on = None

DEFAULT_K8S_MODEL = {
    'cpu_hourly_cost': 0.002,
    'memory_hourly_cost': 0.001
}
CA_TABLE = sa.table(
        'cloudaccount',
        sa.column('id', sa.String(36)),
        sa.column('organization_id', sa.String(36)),
        sa.column('config', sa.Text()),
        sa.column('cost_model_id', sa.String(36)),
        sa.column('type', sa.String(100)),
        sa.column('deleted_at', sa.Integer()),
    )
COST_MODEL_TABLE = sa.table(
    'cost_model',
    sa.column('id', sa.String(36)),
    sa.column('deleted_at', sa.Integer()),
    sa.column('created_at', sa.Integer()),
    sa.column('organization_id', sa.String(36)),
    sa.column('type', sa.String(36)),
    sa.column('value', sa.Text()),
)


def upgrade():
    op.create_table(
        'cost_model',
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('type', sa.Enum('CLOUD_ACCOUNT', 'RESOURCE'), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(
        'cloudaccount',
        sa.Column('cost_model_id', sa.String(36), nullable=True))
    op.create_foreign_key(
        'fk_cloudaccount_cost_model', 'cloudaccount',
        'cost_model', ['cost_model_id'], ['id'])

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_acc_stmt = select([
            CA_TABLE.c.id, CA_TABLE.c.config,
            CA_TABLE.c.organization_id, CA_TABLE.c.deleted_at
        ]).where(CA_TABLE.c.type == 'KUBERNETES_CNR')
        cloud_accs = session.execute(cloud_acc_stmt)

        cloud_acc_configs_map = {}
        cost_models = []
        now = int(datetime.utcnow().timestamp())
        for ca in cloud_accs:
            config = json.loads(ca['config'])
            cost_model = config.pop('cost_model', DEFAULT_K8S_MODEL)
            cost_models.append({
                'id': ca['id'],
                'organization_id': ca['organization_id'],
                'type': 'CLOUD_ACCOUNT',
                'value': json.dumps(cost_model),
                'deleted_at': ca['deleted_at'],
                'created_at': now
            })
            cloud_acc_configs_map[ca['id']] = json.dumps(config)
        for cost_model in cost_models:
            ins_stmt = insert(COST_MODEL_TABLE).values(**cost_model)
            session.execute(ins_stmt)
        for ca_id, config in cloud_acc_configs_map.items():
            update_stmt = update(CA_TABLE).values(
                config=config, cost_model_id=ca_id
            ).where(CA_TABLE.c.id == ca_id)
            session.execute(update_stmt)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_acc_stmt = select([
            CA_TABLE.c.id, CA_TABLE.c.config,
        ]).where(CA_TABLE.c.type == 'KUBERNETES_CNR')
        cloud_acc_config_map = {
            ca['id']: ca['config']
            for ca in session.execute(cloud_acc_stmt)
        }

        cost_model_stmt = select([
            COST_MODEL_TABLE.c.id, COST_MODEL_TABLE.c.value,
        ]).where(COST_MODEL_TABLE.c.type == 'CLOUD_ACCOUNT')
        cost_model_map = {
            cost_model['id']: cost_model['value']
            for cost_model in session.execute(cost_model_stmt)
        }
        for ca_id, config in cloud_acc_config_map.items():
            cost_model = cost_model_map.get(ca_id)
            if cost_model:
                cost_model = json.loads(cost_model)
            else:
                cost_model = DEFAULT_K8S_MODEL
            config = json.loads(config)
            config['cost_model'] = cost_model
            update_stmt = update(CA_TABLE).values(
                config=json.dumps(config)
            ).where(CA_TABLE.c.id == ca_id)
            session.execute(update_stmt)
        session.commit()
    finally:
        session.close()

    op.drop_constraint(
        'fk_cloudaccount_cost_model', 'cloudaccount', type_='foreignkey')
    op.drop_column('cloudaccount', 'cost_model_id')
    op.drop_table('cost_model')
