""""cloud_validation_fields"

Revision ID: 7611a658f311
Revises: 315419fe1685
Create Date: 2019-10-21 11:17:23.180091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '7611a658f311'
down_revision = '315419fe1685'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cloud', sa.Column('state_description', sa.TEXT(), nullable=False,
                                     default='Validation not started'))
    op.add_column('cloud', sa.Column(
        'validation_state', sa.Enum('NOT_VALIDATED', 'VALIDATED', 'VALIDATING', 'ERROR'),
        nullable=False, default='NOT_VALIDATED'))

    cloud_table = sa.table(
        "cloud",
        sa.column('managed', sa.BOOLEAN),
        sa.column('validation_state', sa.Enum('NOT_VALIDATED', 'VALIDATED', 'VALIDATING', 'ERROR')),
        sa.column('state_description', sa.TEXT)
    )
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        # setting managed True for all existing clouds,
        # because missed it in prev migration
        session.execute(sa.update(cloud_table).values(
            managed=True, validation_state='VALIDATED',
            state_description='Cloud validation completed successfully!'))
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('cloud', 'validation_state')
    op.drop_column('cloud', 'state_description')
