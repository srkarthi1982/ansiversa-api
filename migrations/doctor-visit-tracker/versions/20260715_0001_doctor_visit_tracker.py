"""Create Doctor Visit Tracker tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa
revision: str = '20260715_0001_doctor_visit_tracker'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table('DoctorSpecialties', sa.Column('id', sa.String(36), nullable=False), sa.Column('userId', sa.String(36), nullable=False), sa.Column('name', sa.String(120), nullable=False), sa.Column('sortOrder', sa.Integer(), server_default=sa.text('0'), nullable=False), sa.Column('isSystem', sa.Boolean(), server_default=sa.text('0'), nullable=False), sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('userId', 'name', name='uq_doctor_specialties_owner_name'))
    op.create_index('ix_doctor_specialties_user_id', 'DoctorSpecialties', ['userId'])
    op.create_index('ix_doctor_specialties_user_name', 'DoctorSpecialties', ['userId', 'name'])
    op.create_index('ix_doctor_specialties_user_sort', 'DoctorSpecialties', ['userId', 'sortOrder'])
    op.create_index('ix_doctor_specialties_is_system', 'DoctorSpecialties', ['isSystem'])
    op.create_table('DoctorVisits', sa.Column('id', sa.String(36), nullable=False), sa.Column('userId', sa.String(36), nullable=False), sa.Column('specialtyId', sa.String(36), nullable=False), sa.Column('visitTitle', sa.String(180), nullable=False), sa.Column('doctorName', sa.String(180), nullable=False), sa.Column('clinicName', sa.String(180), nullable=True), sa.Column('visitDate', sa.Date(), nullable=False), sa.Column('visitTime', sa.Time(), nullable=True), sa.Column('status', sa.String(20), server_default='scheduled', nullable=False), sa.Column('reason', sa.Text(), nullable=True), sa.Column('diagnosisNotes', sa.Text(), nullable=True), sa.Column('medications', sa.Text(), nullable=True), sa.Column('followUpDate', sa.Date(), nullable=True), sa.Column('visitCost', sa.Numeric(12, 2), nullable=True), sa.Column('currency', sa.String(3), server_default='USD', nullable=False), sa.Column('insuranceNotes', sa.Text(), nullable=True), sa.Column('personalNotes', sa.Text(), nullable=True), sa.Column('archived', sa.Boolean(), server_default=sa.text('0'), nullable=False), sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.ForeignKeyConstraint(['specialtyId'], ['DoctorSpecialties.id']), sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_doctor_visits_user_id', 'DoctorVisits', ['userId'])
    op.create_index('ix_doctor_visits_specialty_id', 'DoctorVisits', ['specialtyId'])
    op.create_index('ix_doctor_visits_user_specialty', 'DoctorVisits', ['userId', 'specialtyId'])
    op.create_index('ix_doctor_visits_user_date', 'DoctorVisits', ['userId', 'visitDate'])
    op.create_index('ix_doctor_visits_user_status', 'DoctorVisits', ['userId', 'status'])
    op.create_index('ix_doctor_visits_user_archived', 'DoctorVisits', ['userId', 'archived'])
    op.create_index('ix_doctor_visits_user_follow_up', 'DoctorVisits', ['userId', 'followUpDate'])
    op.create_index('ix_doctor_visits_user_updated', 'DoctorVisits', ['userId', 'updatedAt'])
    op.create_index('ix_doctor_visits_user_doctor', 'DoctorVisits', ['userId', 'doctorName'])

def downgrade() -> None:
    op.drop_index('ix_doctor_visits_user_doctor', table_name='DoctorVisits')
    op.drop_index('ix_doctor_visits_user_updated', table_name='DoctorVisits')
    op.drop_index('ix_doctor_visits_user_follow_up', table_name='DoctorVisits')
    op.drop_index('ix_doctor_visits_user_archived', table_name='DoctorVisits')
    op.drop_index('ix_doctor_visits_user_status', table_name='DoctorVisits')
    op.drop_index('ix_doctor_visits_user_date', table_name='DoctorVisits')
    op.drop_index('ix_doctor_visits_user_specialty', table_name='DoctorVisits')
    op.drop_index('ix_doctor_visits_specialty_id', table_name='DoctorVisits')
    op.drop_index('ix_doctor_visits_user_id', table_name='DoctorVisits')
    op.drop_table('DoctorVisits')
    op.drop_index('ix_doctor_specialties_is_system', table_name='DoctorSpecialties')
    op.drop_index('ix_doctor_specialties_user_sort', table_name='DoctorSpecialties')
    op.drop_index('ix_doctor_specialties_user_name', table_name='DoctorSpecialties')
    op.drop_index('ix_doctor_specialties_user_id', table_name='DoctorSpecialties')
    op.drop_table('DoctorSpecialties')
