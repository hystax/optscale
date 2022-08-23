""""report_import_fields"

Revision ID: 7ea7a125a3f4
Revises: 436019c61530
Create Date: 2020-03-20 13:50:56.149984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '7ea7a125a3f4'
down_revision = '2b485ea622cf'
branch_labels = None
depends_on = None


def upgrade():
    c_auto_import = sa.Column('auto_import', sa.Boolean(),
                              nullable=False, default=True)
    c_import_period = sa.Column('import_period', sa.Integer(),
                                nullable=False, default=24)
    c_last_import_at = sa.Column('last_import_at', sa.Integer(),
                                 nullable=False, default=0)
    op.add_column('cloudcredentials', c_auto_import)
    op.add_column('cloudcredentials', c_import_period)
    op.add_column('cloudcredentials', c_last_import_at)
    creds_table = sa.table(
        'cloudcredentials', c_auto_import, c_import_period, c_last_import_at)
    bind = op.get_bind()
    session = Session(bind=bind)
    enable_update = sa.update(creds_table).values(
        auto_import=False,
        import_period=24,
        last_import_at=0
    )
    try:
        session.execute(enable_update)
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('cloudcredentials', 'last_import_at')
    op.drop_column('cloudcredentials', 'import_period')
    op.drop_column('cloudcredentials', 'auto_import')
