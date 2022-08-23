""""added_role_scope"

Revision ID: 19a8c2c4383b
Revises: f66517c5263b
Create Date: 2017-05-16 16:54:54.476648

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, update, Boolean, String


# revision identifiers, used by Alembic.
revision = '19a8c2c4383b'
down_revision = 'f66517c5263b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('role', sa.Column('lvl_id', sa.Integer(), nullable=False))
    op.add_column('role', sa.Column('scope_id', sa.String(length=36),
                                    nullable=True))
    op.drop_index('ix_role_name', table_name='role')
    op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=False)
    op.add_column('user', sa.Column('display_name', sa.String(length=64),
                                    nullable=False))

    bind = op.get_bind()
    session = Session(bind=bind)

    role_table = table('role',
                       column('lvl_id', Integer),
                       column('type_id', Integer))
    user_table = table('user',
                       column('is_active', Boolean),
                       column('name', String(256)),
                       column('display_name', String(64)))
    update_stmt = update(role_table).values(lvl_id=role_table.c.type_id)
    update_display_name = update(user_table).values(
        display_name=user_table.c.name)
    try:
        session.execute(update_stmt)
        session.execute(update_display_name)
        session.commit()
    finally:
        session.close()

    op.create_foreign_key('role_ibfk_lvl_2', 'role', 'type', ['lvl_id'],
                          ['id'])
    op.add_column('type', sa.Column('assignable', sa.Boolean(),
                                    nullable=False))
    op.add_column('user', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('role', sa.Column('is_active', sa.Boolean(), nullable=False))
    type_table = table('type',
                       column('assignable', Boolean),
                       column('name', String(24)))
    role_table = table('role',
                       column('is_active', Boolean))
    update_user_table = update(user_table).values(is_active=1)
    update_role_table = update(role_table).values(is_active=1)
    update_assignable_types = update(type_table).values(
        assignable=1).where(type_table.c.name.in_(['partner', 'customer']))
    try:
        session.execute(update_assignable_types)
        session.execute(update_user_table)
        session.execute(update_role_table)
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('user', 'is_active')
    op.drop_column('role', 'is_active')
    op.drop_column('user', 'display_name')
    op.drop_column('type', 'assignable')
    op.drop_constraint('role_ibfk_lvl_2', 'role', type_='foreignkey')
    op.drop_index(op.f('ix_role_name'), table_name='role')
    op.create_index('ix_role_name', 'role', ['name'], unique=False)
    op.drop_column('role', 'scope_id')
    op.drop_column('role', 'lvl_id')
