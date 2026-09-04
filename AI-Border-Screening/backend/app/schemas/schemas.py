from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    PASSPORT = "passport"
    VISA = "visa"
    NATIONAL_ID = "national_id"
    PERMIT = "permit"


class ProcessingStatus(str, Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    WARNING = "warning"
    FAILED = "failed"


class VerificationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OfficerBase(BaseModel):
    officer_id: str
    email: EmailStr
    full_name: str
    badge_number: Optional[str] = None
    department: Optional[str] = None


class OfficerCreate(OfficerBase):
    password: str = Field(..., min_length=8)


class OfficerLogin(BaseModel):
    officer_id: str
    password: str


class OfficerResponse(OfficerBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    officer_id: Optional[str] = None


class PassengerBase(BaseModel):
    passenger_id: str
    full_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    passport_number: Optional[str] = None


class PassengerCreate(PassengerBase):
    pass


class PassengerResponse(PassengerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    document_type: DocumentType
    original_filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class DocumentUpload(BaseModel):
    document_type: DocumentType


class DocumentResponse(DocumentBase):
    id: int
    case_id: int
    file_path: str
    upload_status: ProcessingStatus
    processing_progress: float
    current_step: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentQueueItem(BaseModel):
    id: int
    document_type: DocumentType
    thumbnail_path: Optional[str] = None
    upload_status: ProcessingStatus
    processing_progress: float
    current_step: Optional[str] = None


class CaseBase(BaseModel):
    case_id: str
    passenger_id: int


class CaseCreate(CaseBase):
    pass


class CaseResponse(CaseBase):
    id: int
    officer_id: int
    overall_status: VerificationStatus
    overall_risk_level: Optional[RiskLevel] = None
    risk_score: Optional[float] = None
    risk_reasons: Optional[List[str]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    case_id: str
    passenger_name: Optional[str] = None
    passenger_id: str
    document_count: int
    overall_risk_level: Optional[RiskLevel] = None
    overall_status: VerificationStatus
    officer_name: str
    created_at: datetime


class OCRField(BaseModel):
    field_name: str
    value: str
    confidence: float


class OCRResultBase(BaseModel):
    extracted_fields: List[OCRField]
    confidence_scores: Optional[Dict[str, float]] = None
    raw_text: Optional[str] = None


class OCRResultResponse(OCRResultBase):
    id: int
    case_id: int
    document_id: int
    processing_time_ms: Optional[int] = None
    status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class MRZField(BaseModel):
    field_name: str
    ocr_value: Optional[str] = None
    mrz_value: Optional[str] = None
    match: Optional[bool] = None


class MRZResultBase(BaseModel):
    mrz_detected: bool
    mrz_raw: Optional[str] = None
    mrz_type: Optional[str] = None
    decoded_fields: Optional[Dict[str, str]] = None
    checksum_valid: Optional[bool] = None
    checksum_details: Optional[Dict[str, Any]] = None
    ocr_mrz_comparison: Optional[List[MRZField]] = None
    consistency_percentage: Optional[float] = None


class MRZResultResponse(MRZResultBase):
    id: int
    case_id: int
    document_id: int
    processing_time_ms: Optional[int] = None
    status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ValidationField(BaseModel):
    field_name: str
    value: str
    valid: bool
    message: Optional[str] = None


class ValidationResultBase(BaseModel):
    field_validations: List[ValidationField]
    overall_valid: Optional[bool] = None
    warnings: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    reference_db_check: Optional[Dict[str, Any]] = None


class ValidationResultResponse(ValidationResultBase):
    id: int
    case_id: int
    document_id: int
    processing_time_ms: Optional[int] = None
    status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class TamperResultBase(BaseModel):
    tampering_probability: Optional[float] = None
    suspected_regions: Optional[List[Dict[str, Any]]] = None
    heatmap_path: Optional[str] = None
    noise_residual_path: Optional[str] = None
    noise_analysis_reliable: bool = True
    forensics_findings: Optional[Dict[str, Any]] = None
    rgb_image_path: Optional[str] = None


class TamperResultResponse(TamperResultBase):
    id: int
    case_id: int
    document_id: int
    processing_time_ms: Optional[int] = None
    status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class FaceResultBase(BaseModel):
    document_face_path: Optional[str] = None
    live_face_path: Optional[str] = None
    document_face_detected: bool = False
    live_face_detected: bool = False
    similarity_score: Optional[float] = None
    match_status: Optional[str] = None


class FaceResultResponse(FaceResultBase):
    id: int
    case_id: int
    document_id: int
    processing_time_ms: Optional[int] = None
    status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class CrossDocumentField(BaseModel):
    field_name: str
    document_values: Dict[str, str]
    consistent: bool
    inconsistency_details: Optional[str] = None


class CrossDocumentResultBase(BaseModel):
    comparisons: List[CrossDocumentField]


class CrossDocumentResultResponse(CrossDocumentResultBase):
    id: int
    case_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RiskFactor(BaseModel):
    factor: str
    weight: float
    contribution: float
    description: str


class RiskAssessmentBase(BaseModel):
    risk_level: RiskLevel
    risk_score: float
    contributing_factors: List[RiskFactor]


class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    case_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VerificationProgress(BaseModel):
    stage: str
    status: ProcessingStatus
    progress: float
    message: Optional[str] = None


class VerificationProgressResponse(BaseModel):
    overall_progress: float
    stages: List[VerificationProgress]
    current_stage: Optional[str] = None


class DashboardStats(BaseModel):
    total_passengers_screened: int
    total_documents_verified: int
    valid_documents: int
    suspicious_documents: int
    high_risk_cases: int
    currently_processing: int
    risk_distribution: Dict[str, int]


class RecentActivity(BaseModel):
    case_id: str
    passenger_name: Optional[str] = None
    document_count: int
    risk_level: RiskLevel
    status: VerificationStatus
    timestamp: datetime


class DashboardResponse(BaseModel):
    stats: DashboardStats
    risk_distribution: Dict[str, int]
    recent_activity: List[RecentActivity]


class PassengerHistoryItem(BaseModel):
    case_id: str
    passenger_name: Optional[str] = None
    passenger_id: str
    date_time: datetime
    document_count: int
    overall_risk: RiskLevel
    verification_status: VerificationStatus
    officer_name: str


class PassengerHistoryFilter(BaseModel):
    passenger_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    risk_level: Optional[RiskLevel] = None
    status: Optional[VerificationStatus] = None


class ProcessingStep(BaseModel):
    name: str
    status: ProcessingStatus
    progress: float
    details: Optional[str] = None


class VerificationDetailResponse(BaseModel):
    case_id: str
    passenger_name: str
    passenger_id: str
    timestamp: datetime
    overall_status: VerificationStatus
    overall_risk_level: RiskLevel
    documents: List[DocumentResponse]
    ocr_results: List[OCRResultResponse]
    mrz_results: List[MRZResultResponse]
    validation_results: List[ValidationResultResponse]
    tamper_results: List[TamperResultResponse]
    face_results: List[FaceResultResponse]
    cross_document_results: List[CrossDocumentResultResponse]
    risk_assessment: RiskAssessmentResponse
    processing_steps: List[ProcessingStep]