"""Create Water Intake Tracker tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = '20260715_0001_water_intake_tracker'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'WaterGoals',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('userId', sa.String(36), nullable=False),
        sa.Column('dailyGoal', sa.Numeric(12, 2), nullable=False),
        sa.Column('preferredUnit', sa.String(2), server_default='ml', nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('userId', name='uq_water_goals_user_id'),
    )
    op.create_index('ix_water_goals_user_id', 'WaterGoals', ['userId'])
    op.create_index('ix_water_goals_user_updated', 'WaterGoals', ['userId', 'updatedAt'])
    op.create_table(
        'WaterEntries',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('userId', sa.String(36), nullable=False),
        sa.Column('entryDate', sa.Date(), nullable=False),
        sa.Column('entryTime', sa.Time(), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('unit', sa.String(2), server_default='ml', nullable=False),
        sa.Column('drinkType', sa.String(80), server_default='Water', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_water_entries_user_id', 'WaterEntries', ['userId'])
    op.create_index('ix_water_entries_user_date', 'WaterEntries', ['userId', 'entryDate'])
    op.create_index('ix_water_entries_user_date_time', 'WaterEntries', ['userId', 'entryDate', 'entryTime'])
    op.create_index('ix_water_entries_user_drink_type', 'WaterEntries', ['userId', 'drinkType'])
    op.create_index('ix_water_entries_user_created', 'WaterEntries', ['userId', 'createdAt'])
    op.create_index('ix_water_entries_user_updated', 'WaterEntries', ['userId', 'updatedAt'])
    op.create_index('ix_water_entries_drink_type', 'WaterEntries', ['drinkType'])


def downgrade() -> None:
    op.drop_index('ix_water_entries_drink_type', table_name='WaterEntries')
    op.drop_index('ix_water_entries_user_updated', table_name='WaterEntries')
    op.drop_index('ix_water_entries_user_created', table_name='WaterEntries')
    op.drop_index('ix_water_entries_user_drink_type', table_name='WaterEntries')
    op.drop_index('ix_water_entries_user_date_time', table_name='WaterEntries')
    op.drop_index('ix_water_entries_user_date', table_name='WaterEntries')
    op.drop_index('ix_water_entries_user_id', table_name='WaterEntries')
    op.drop_table('WaterEntries')
    op.drop_index('ix_water_goals_user_updated', table_name='WaterGoals')
    op.drop_index('ix_water_goals_user_id', table_name='WaterGoals')
    op.drop_table('WaterGoals')
