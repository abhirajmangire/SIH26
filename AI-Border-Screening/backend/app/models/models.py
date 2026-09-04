import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Boolean, JSON, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from app.database.session import Base


class DocumentType(str, enum.Enum):
    PASSPORT = "passport"
    VISA = "visa"
    NATIONAL_ID = "national_id"
    PERMIT = "permit"


class ProcessingStatus(str, enum.Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    WARNING = "warning"
    FAILED = "failed"


class VerificationStatus(str, enum.Enum):
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Officer(Base):
    __tablename__ = "officers"
    
    id = Column(Integer, primary_key=True, index=True)
    officer_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    badge_number = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    cases = relationship("VerificationCase", back_populates="officer")


class Passenger(Base):
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    nationality = Column(String(50), nullable=True)
    gender = Column(String(20), nullable=True)
    passport_number = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    cases = relationship("VerificationCase", back_populates="passenger")


class VerificationCase(Base):
    __tablename__ = "verification_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(50), unique=True, index=True, nullable=False)
    officer_id = Column(Integer, ForeignKey("officers.id"), nullable=False)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    overall_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    overall_risk_level = Column(Enum(RiskLevel), nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_reasons = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    officer = relationship("Officer", back_populates="cases")
    passenger = relationship("Passenger", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    ocr_results = relationship("OCRResult", back_populates="case", cascade="all, delete-orphan")
    mrz_results = relationship("MRZResult", back_populates="case", cascade="all, delete-orphan")
    validation_results = relationship("ValidationResult", back_populates="case", cascade="all, delete-orphan")
    tamper_results = relationship("TamperResult", back_populates="case", cascade="all, delete-orphan")
    face_results = relationship("FaceResult", back_populates="case", cascade="all, delete-orphan")
    cross_doc_results = relationship("CrossDocumentResult", back_populates="case", cascade="all, delete-orphan")
    risk_assessment = relationship("RiskAssessment", back_populates="case", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="case", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    upload_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.WAITING)
    processing_progress = Column(Float, default=0.0)
    current_step = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    case = relationship("VerificationCase", back_populates="documents")
    ocr_result = relationship("OCRResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    mrz_result = relationship("MRZResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    validation_result = relationship("ValidationResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    tamper_result = relationship("TamperResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    face_result = relationship("FaceResult", back_populates="document", uselist=False, cascade="all, delete-orphan")


class OCRResult(Base):
    __tablename__ = "ocr_results"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    extracted_fields = Column(JSON, nullable=False)
    confidence_scores = Column(JSON, nullable=True)
    raw_text = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.WAITING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    case = relationship("VerificationCase", back_populates="ocr_results")
    document = relationship("Document", back_populates="ocr_result")


class MRZResult(Base):
    __tablename__ = "mrz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    mrz_detected = Column(Boolean, default=False)
    mrz_raw = Column(Text, nullable=True)
    mrz_type = Column(String(20), nullable=True)
    decoded_fields = Column(JSON, nullable=True)
    checksum_valid = Column(Boolean, nullable=True)
    checksum_details = Column(JSON, nullable=True)
    ocr_mrz_comparison = Column(JSON, nullable=True)
    consistency_percentage = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.WAITING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    case = relationship("VerificationCase", back_populates="mrz_results")
    document = relationship("Document", back_populates="mrz_result")


class ValidationResult(Base):
    __tablename__ = "validation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    field_validations = Column(JSON, nullable=False)
    overall_valid = Column(Boolean, nullable=True)
    warnings = Column(JSON, nullable=True)
    errors = Column(JSON, nullable=True)
    reference_db_check = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.WAITING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    case = relationship("VerificationCase", back_populates="validation_results")
    document = relationship("Document", back_populates="validation_result")


class TamperResult(Base):
    __tablename__ = "tamper_results"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    tampering_probability = Column(Float, nullable=True)
    suspected_regions = Column(JSON, nullable=True)
    heatmap_path = Column(String(500), nullable=True)
    noise_residual_path = Column(String(500), nullable=True)
    noise_analysis_reliable = Column(Boolean, default=True)
    forensics_findings = Column(JSON, nullable=True)
    rgb_image_path = Column(String(500), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.WAITING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    case = relationship("VerificationCase", back_populates="tamper_results")
    document = relationship("Document", back_populates="tamper_result")


class FaceResult(Base):
    __tablename__ = "face_results"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    document_face_path = Column(String(500), nullable=True)
    live_face_path = Column(String(500), nullable=True)
    document_face_detected = Column(Boolean, default=False)
    live_face_detected = Column(Boolean, default=False)
    document_embedding = Column(JSON, nullable=True)
    live_embedding = Column(JSON, nullable=True)
    similarity_score = Column(Float, nullable=True)
    match_status = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.WAITING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    case = relationship("VerificationCase", back_populates="face_results")
    document = relationship("Document", back_populates="face_result")


class CrossDocumentResult(Base):
    __tablename__ = "cross_document_results"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False)
    field_name = Column(String(50), nullable=False)
    document_values = Column(JSON, nullable=False)
    consistent = Column(Boolean, nullable=True)
    inconsistency_details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    case = relationship("VerificationCase", back_populates="cross_doc_results")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False, unique=True)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_score = Column(Float, nullable=False)
    contributing_factors = Column(JSON, nullable=False)
    factor_weights = Column(JSON, nullable=True)
    threshold_config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    case = relationship("VerificationCase", back_populates="risk_assessment")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("verification_cases.id"), nullable=False)
    officer_id = Column(Integer, ForeignKey("officers.id"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    case = relationship("VerificationCase", back_populates="audit_logs")


Index("ix_verification_cases_case_id", VerificationCase.case_id)
Index("ix_documents_case_id", Document.case_id)
Index("ix_ocr_results_document_id", OCRResult.document_id)
Index("ix_mrz_results_document_id", MRZResult.document_id)
Index("ix_audit_logs_case_id", AuditLog.case_id)