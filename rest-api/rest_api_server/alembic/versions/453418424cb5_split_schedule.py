""""split_schedule"

Revision ID: 453418424cb5
Revises: d83e608e20b3
Create Date: 2017-05-02 08:47:07.910451

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String, insert
from sqlalchemy import select, String, join, update, delete

# revision identifiers, used by Alembic.
revision = '453418424cb5'
down_revision = 'ad8407118b8a'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    op.create_table('devicestate',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('update_time', sa.Integer(), nullable=False),
    sa.Column('state', sa.Enum('discovered', 'scheduled', 'running', 'idle', 'cancel', 'error', name='hbstate'), nullable=False),
    sa.Column('last_error', sa.Integer(), nullable=True),
    sa.Column('idle_until', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    try:
        schedule_table = table('schedule',
                                column('id', String(36)),
                                column('update_time', Integer),
                                column('state', String(15)),
                                column('last_error', Integer),
                                column('idle_until', Integer))
        devicestate_table = table('devicestate',
                                column('id', String(36)),
                                column('update_time', Integer),
                                column('state', String(15)),
                                column('last_error', Integer),
                                column('idle_until', Integer))
        stmt = select([schedule_table])
        for device_state in session.execute(stmt):
            ins_stmt = insert(devicestate_table).values(
                id=device_state['id'],
                state=device_state['state'],
                update_time=device_state['update_time'],
                last_error=device_state['last_error'],
                idle_until=device_state['idle_until'])
            session.execute(ins_stmt)
        session.commit()
    finally:
        session.close()
    op.drop_column('schedule', 'update_time')
    op.drop_column('schedule', 'last_error')
    op.drop_column('schedule', 'deleted')
    op.drop_column('schedule', 'state')
    op.drop_column('schedule', 'idle_until')

    op.add_column('schedule', sa.Column('owner_id', sa.String(length=36), nullable=True))
    try:
        schedule_table = table('schedule',
                               column('id', Integer),
                               column('owner_id', String(36)))
        upd_stmt = update(schedule_table).values(owner_id=schedule_table.c.id)
        session.execute(upd_stmt)
        session.commit()
    finally:
        session.close()

    op.drop_column('schedule', 'id')
    # hard to do it without raw sql
    op.execute("ALTER TABLE schedule ADD COLUMN id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT")

    schedule_table = table('schedule',
                           column('owner_id', String(36)),
                           column('target_rpo', Integer))
    try:
        ins_stmt = insert(schedule_table).values(
            owner_id=None,
            target_rpo=3600)
        session.execute(ins_stmt)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    schedule_table = table('schedule',
                           column('owner_id', String(36)),
                           column('target_rpo', Integer))
    try:
        del_stmt = delete(schedule_table)
        session.execute(del_stmt)
        session.commit()
    finally:
        session.close()

    op.add_column('schedule', sa.Column('state', mysql.ENUM('scheduled', 'running', 'idle', 'cancel', 'error', collation='utf8mb4_unicode_ci'), nullable=False))
    op.add_column('schedule', sa.Column('deleted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('schedule', sa.Column('last_error', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('schedule', sa.Column('update_time', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.add_column('schedule', sa.Column('idle_until', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    devicestate_table = table('devicestate',
                              column('id', String(36)),
                              column('update_time', Integer),
                              column('state', String(15)),
                              column('last_error', Integer),
                              column('idle_until', Integer))
    schedule_table = table('schedule',
                           column('owner_id', String(36)),
                           column('target_rpo', Integer),
                           column('idle_until', Integer),
                           column('update_time', Integer),
                           column('state', String(15)),
                           column('last_error', Integer),
                           column('deleted', Integer))
    try:
        stmt = select([devicestate_table])
        device_states = session.execute(stmt)
        schedules = []
        for state in device_states:
            schedule = {
                'deleted': 0,
                'owner_id': state['id'],
                'target_rpo': 3600,
                'idle_until': state['idle_until'],
                'update_time': state['update_time'],
                'state': state['state'],
                'last_error': state['last_error'],

            }
            schedules.append(schedule)
        op.bulk_insert(schedule_table, schedules)
        session.commit()
    finally:
        session.close()

    op.drop_column('schedule', 'id')
    op.add_column('schedule', sa.Column('id', sa.String(length=36), nullable=False))
    try:
        schedule_table = table('schedule',
                               column('id', String(36)),
                               column('owner_id', String(36)))
        upd_stmt = update(schedule_table).values(id=schedule_table.c.owner_id)
        session.execute(upd_stmt)
        session.commit()
    finally:
        session.close()
    op.drop_column('schedule', 'owner_id')
    op.drop_table('devicestate')

