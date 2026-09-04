"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'officers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('officer_id', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('badge_number', sa.String(length=50), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('officer_id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_officers_officer_id', 'officers', ['officer_id'], unique=True)
    op.create_index('ix_officers_email', 'officers', ['email'], unique=True)

    op.create_table(
        'passengers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('passenger_id', sa.String(length=50), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('date_of_birth', sa.DateTime(), nullable=True),
        sa.Column('nationality', sa.String(length=50), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('passport_number', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('passenger_id'),
    )
    op.create_index('ix_passengers_passenger_id', 'passengers', ['passenger_id'], unique=True)
    op.create_index('ix_passengers_passport_number', 'passengers', ['passport_number'])

    op.create_table(
        'verification_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=False),
        sa.Column('officer_id', sa.Integer(), nullable=False),
        sa.Column('passenger_id', sa.Integer(), nullable=False),
        sa.Column('overall_status', sa.Enum('valid', 'invalid', 'warning', 'pending', name='verificationstatus'), nullable=False, default='pending'),
        sa.Column('overall_risk_level', sa.Enum('low', 'medium', 'high', name='risklevel'), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('risk_reasons', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['officer_id'], ['officers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['passenger_id'], ['passengers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_id'),
    )
    op.create_index('ix_verification_cases_case_id', 'verification_cases', ['case_id'], unique=True)

    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.Enum('passport', 'visa', 'national_id', 'permit', name='documenttype'), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('upload_status', sa.Enum('waiting', 'processing', 'completed', 'warning', 'failed', name='processingstatus'), nullable=False, default='waiting'),
        sa.Column('processing_progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('current_step', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_documents_case_id', 'documents', ['case_id'])

    op.create_table(
        'ocr_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('extracted_fields', sa.JSON(), nullable=False),
        sa.Column('confidence_scores', sa.JSON(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('waiting', 'processing', 'completed', 'warning', 'failed', name='processingstatus'), nullable=False, default='waiting'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id'),
    )
    op.create_index('ix_ocr_results_document_id', 'ocr_results', ['document_id'], unique=True)
    op.create_index('ix_ocr_results_case_id', 'ocr_results', ['case_id'])

    op.create_table(
        'mrz_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('mrz_detected', sa.Boolean(), nullable=False, default=False),
        sa.Column('mrz_raw', sa.Text(), nullable=True),
        sa.Column('mrz_type', sa.String(length=20), nullable=True),
        sa.Column('decoded_fields', sa.JSON(), nullable=True),
        sa.Column('checksum_valid', sa.Boolean(), nullable=True),
        sa.Column('checksum_details', sa.JSON(), nullable=True),
        sa.Column('ocr_mrz_comparison', sa.JSON(), nullable=True),
        sa.Column('consistency_percentage', sa.Float(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('waiting', 'processing', 'completed', 'warning', 'failed', name='processingstatus'), nullable=False, default='waiting'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id'),
    )
    op.create_index('ix_mrz_results_document_id', 'mrz_results', ['document_id'], unique=True)
    op.create_index('ix_mrz_results_case_id', 'mrz_results', ['case_id'])

    op.create_table(
        'validation_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('field_validations', sa.JSON(), nullable=False),
        sa.Column('overall_valid', sa.Boolean(), nullable=True),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('reference_db_check', sa.JSON(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('waiting', 'processing', 'completed', 'warning', 'failed', name='processingstatus'), nullable=False, default='waiting'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id'),
    )
    op.create_index('ix_validation_results_document_id', 'validation_results', ['document_id'], unique=True)
    op.create_index('ix_validation_results_case_id', 'validation_results', ['case_id'])

    op.create_table(
        'tamper_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('tampering_probability', sa.Float(), nullable=True),
        sa.Column('suspected_regions', sa.JSON(), nullable=True),
        sa.Column('heatmap_path', sa.String(length=500), nullable=True),
        sa.Column('noise_residual_path', sa.String(length=500), nullable=True),
        sa.Column('noise_analysis_reliable', sa.Boolean(), nullable=False, default=True),
        sa.Column('forensics_findings', sa.JSON(), nullable=True),
        sa.Column('rgb_image_path', sa.String(length=500), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('waiting', 'processing', 'completed', 'warning', 'failed', name='processingstatus'), nullable=False, default='waiting'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id'),
    )
    op.create_index('ix_tamper_results_document_id', 'tamper_results', ['document_id'], unique=True)
    op.create_index('ix_tamper_results_case_id', 'tamper_results', ['case_id'])

    op.create_table(
        'face_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('document_face_path', sa.String(length=500), nullable=True),
        sa.Column('live_face_path', sa.String(length=500), nullable=True),
        sa.Column('document_face_detected', sa.Boolean(), nullable=False, default=False),
        sa.Column('live_face_detected', sa.Boolean(), nullable=False, default=False),
        sa.Column('document_embedding', sa.JSON(), nullable=True),
        sa.Column('live_embedding', sa.JSON(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('match_status', sa.String(length=50), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('waiting', 'processing', 'completed', 'warning', 'failed', name='processingstatus'), nullable=False, default='waiting'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id'),
    )
    op.create_index('ix_face_results_document_id', 'face_results', ['document_id'], unique=True)
    op.create_index('ix_face_results_case_id', 'face_results', ['case_id'])

    op.create_table(
        'cross_document_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(length=50), nullable=False),
        sa.Column('document_values', sa.JSON(), nullable=False),
        sa.Column('consistent', sa.Boolean(), nullable=True),
        sa.Column('inconsistency_details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cross_document_results_case_id', 'cross_document_results', ['case_id'])

    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.Enum('low', 'medium', 'high', name='risklevel'), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('contributing_factors', sa.JSON(), nullable=False),
        sa.Column('factor_weights', sa.JSON(), nullable=True),
        sa.Column('threshold_config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_id'),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('officer_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['verification_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['officer_id'], ['officers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_case_id', 'audit_logs', ['case_id'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('risk_assessments')
    op.drop_table('cross_document_results')
    op.drop_table('face_results')
    op.drop_table('tamper_results')
    op.drop_table('validation_results')
    op.drop_table('mrz_results')
    op.drop_table('ocr_results')
    op.drop_table('documents')
    op.drop_table('verification_cases')
    op.drop_table('passengers')
    op.drop_table('officers')