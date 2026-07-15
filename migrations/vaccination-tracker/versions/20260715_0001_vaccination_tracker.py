"""Create Vaccination Tracker tables."""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = '20260715_0001_vaccination_tracker'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table('VaccinationProfiles', sa.Column('id', sa.String(36), nullable=False), sa.Column('userId', sa.String(36), nullable=False), sa.Column('fullName', sa.String(180), nullable=False), sa.Column('dateOfBirth', sa.Date(), nullable=True), sa.Column('relationship', sa.String(80), nullable=True), sa.Column('nickname', sa.String(120), nullable=True), sa.Column('notes', sa.Text(), nullable=True), sa.Column('archived', sa.Boolean(), server_default=sa.text('0'), nullable=False), sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_vaccination_profiles_user_id', 'VaccinationProfiles', ['userId'])
    op.create_index('ix_vaccination_profiles_user_archived', 'VaccinationProfiles', ['userId', 'archived'])
    op.create_index('ix_vaccination_profiles_user_name', 'VaccinationProfiles', ['userId', 'fullName'])
    op.create_index('ix_vaccination_profiles_user_updated', 'VaccinationProfiles', ['userId', 'updatedAt'])
    op.create_table('VaccineTypes', sa.Column('id', sa.String(36), nullable=False), sa.Column('userId', sa.String(36), nullable=False), sa.Column('name', sa.String(120), nullable=False), sa.Column('diseaseOrPurpose', sa.String(180), nullable=True), sa.Column('description', sa.Text(), nullable=True), sa.Column('sortOrder', sa.Integer(), server_default=sa.text('0'), nullable=False), sa.Column('isSystem', sa.Boolean(), server_default=sa.text('0'), nullable=False), sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('userId', 'name', name='uq_vaccine_types_owner_name'))
    op.create_index('ix_vaccine_types_user_id', 'VaccineTypes', ['userId'])
    op.create_index('ix_vaccine_types_user_name', 'VaccineTypes', ['userId', 'name'])
    op.create_index('ix_vaccine_types_user_sort', 'VaccineTypes', ['userId', 'sortOrder'])
    op.create_index('ix_vaccine_types_is_system', 'VaccineTypes', ['isSystem'])
    op.create_table('VaccinationRecords', sa.Column('id', sa.String(36), nullable=False), sa.Column('userId', sa.String(36), nullable=False), sa.Column('profileId', sa.String(36), nullable=False), sa.Column('vaccineTypeId', sa.String(36), nullable=True), sa.Column('vaccineName', sa.String(180), nullable=False), sa.Column('diseaseOrPurpose', sa.String(180), nullable=True), sa.Column('doseNumber', sa.Integer(), server_default=sa.text('1'), nullable=False), sa.Column('totalDoses', sa.Integer(), nullable=True), sa.Column('vaccinationDate', sa.Date(), nullable=True), sa.Column('nextDueDate', sa.Date(), nullable=True), sa.Column('status', sa.String(20), server_default='scheduled', nullable=False), sa.Column('clinicOrProvider', sa.String(180), nullable=True), sa.Column('professionalName', sa.String(180), nullable=True), sa.Column('countryOrLocation', sa.String(180), nullable=True), sa.Column('manufacturer', sa.String(180), nullable=True), sa.Column('batchNumber', sa.String(120), nullable=True), sa.Column('certificateReference', sa.String(180), nullable=True), sa.Column('cost', sa.Numeric(12, 2), nullable=True), sa.Column('currency', sa.String(3), server_default='USD', nullable=False), sa.Column('notes', sa.Text(), nullable=True), sa.Column('archived', sa.Boolean(), server_default=sa.text('0'), nullable=False), sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False), sa.ForeignKeyConstraint(['profileId'], ['VaccinationProfiles.id']), sa.ForeignKeyConstraint(['vaccineTypeId'], ['VaccineTypes.id']), sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_vaccination_records_user_id', 'VaccinationRecords', ['userId'])
    op.create_index('ix_vaccination_records_profile_id', 'VaccinationRecords', ['profileId'])
    op.create_index('ix_vaccination_records_vaccine_type_id', 'VaccinationRecords', ['vaccineTypeId'])
    op.create_index('ix_vaccination_records_user_profile', 'VaccinationRecords', ['userId', 'profileId'])
    op.create_index('ix_vaccination_records_user_vaccine_type', 'VaccinationRecords', ['userId', 'vaccineTypeId'])
    op.create_index('ix_vaccination_records_user_due', 'VaccinationRecords', ['userId', 'nextDueDate'])
    op.create_index('ix_vaccination_records_user_vaccination_date', 'VaccinationRecords', ['userId', 'vaccinationDate'])
    op.create_index('ix_vaccination_records_user_status', 'VaccinationRecords', ['userId', 'status'])
    op.create_index('ix_vaccination_records_user_archived', 'VaccinationRecords', ['userId', 'archived'])
    op.create_index('ix_vaccination_records_user_vaccine_dose', 'VaccinationRecords', ['userId', 'profileId', 'vaccineName', 'doseNumber'])
    op.create_index('ix_vaccination_records_user_created', 'VaccinationRecords', ['userId', 'createdAt'])
    op.create_index('ix_vaccination_records_user_updated', 'VaccinationRecords', ['userId', 'updatedAt'])

def downgrade() -> None:
    for name in ['ix_vaccination_records_user_updated','ix_vaccination_records_user_created','ix_vaccination_records_user_vaccine_dose','ix_vaccination_records_user_archived','ix_vaccination_records_user_status','ix_vaccination_records_user_vaccination_date','ix_vaccination_records_user_due','ix_vaccination_records_user_vaccine_type','ix_vaccination_records_user_profile','ix_vaccination_records_vaccine_type_id','ix_vaccination_records_profile_id','ix_vaccination_records_user_id']:
        op.drop_index(name, table_name='VaccinationRecords')
    op.drop_table('VaccinationRecords')
    for name in ['ix_vaccine_types_is_system','ix_vaccine_types_user_sort','ix_vaccine_types_user_name','ix_vaccine_types_user_id']:
        op.drop_index(name, table_name='VaccineTypes')
    op.drop_table('VaccineTypes')
    for name in ['ix_vaccination_profiles_user_updated','ix_vaccination_profiles_user_name','ix_vaccination_profiles_user_archived','ix_vaccination_profiles_user_id']:
        op.drop_index(name, table_name='VaccinationProfiles')
    op.drop_table('VaccinationProfiles')
