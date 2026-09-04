from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.models import (
    VerificationCase, Document, OCRResult, MRZResult, ValidationResult,
    TamperResult, FaceResult, CrossDocumentResult, RiskAssessment,
    ProcessingStatus, VerificationStatus, RiskLevel
)
from app.schemas.schemas import (
    VerificationDetailResponse, DocumentResponse, OCRResultResponse,
    MRZResultResponse, ValidationResultResponse, TamperResultResponse,
    FaceResultResponse, CrossDocumentResultResponse, RiskAssessmentResponse,
    ProcessingStep
)
from app.api.v1.auth import get_current_officer


router = APIRouter()


@router.get("/{case_id}/detail", response_model=VerificationDetailResponse)
async def get_verification_detail(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    case_result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    from app.models.models import Passenger
    passenger_result = await db.execute(select(Passenger).where(Passenger.id == case.passenger_id))
    passenger = passenger_result.scalar_one_or_none()
    
    doc_result = await db.execute(select(Document).where(Document.case_id == case.id))
    documents = doc_result.scalars().all()
    
    ocr_result = await db.execute(select(OCRResult).where(OCRResult.case_id == case.id))
    ocr_results = ocr_result.scalars().all()
    
    mrz_result = await db.execute(select(MRZResult).where(MRZResult.case_id == case.id))
    mrz_results = mrz_result.scalars().all()
    
    val_result = await db.execute(select(ValidationResult).where(ValidationResult.case_id == case.id))
    val_results = val_result.scalars().all()
    
    tamper_result = await db.execute(select(TamperResult).where(TamperResult.case_id == case.id))
    tamper_results = tamper_result.scalars().all()
    
    face_result = await db.execute(select(FaceResult).where(FaceResult.case_id == case.id))
    face_results = face_result.scalars().all()
    
    cross_result = await db.execute(select(CrossDocumentResult).where(CrossDocumentResult.case_id == case.id))
    cross_results = cross_result.scalars().all()
    
    risk_result = await db.execute(select(RiskAssessment).where(RiskAssessment.case_id == case.id))
    risk_assessment = risk_result.scalar_one_or_none()
    
    processing_steps = [
        ProcessingStep(name="Document Identification", status=ProcessingStatus.COMPLETED, progress=100),
        ProcessingStep(name="OCR Extraction", status=ProcessingStatus.COMPLETED, progress=100),
        ProcessingStep(name="MRZ + Checksum", status=ProcessingStatus.COMPLETED if any(m.mrz_detected for m in mrz_results) else ProcessingStatus.WARNING, progress=100),
        ProcessingStep(name="OCR ↔ MRZ Verification", status=ProcessingStatus.COMPLETED if mrz_results else ProcessingStatus.WAITING, progress=100 if mrz_results else 0),
        ProcessingStep(name="Document Validation", status=ProcessingStatus.COMPLETED, progress=100),
        ProcessingStep(name="Cross-Document Verification", status=ProcessingStatus.COMPLETED if cross_results else ProcessingStatus.WAITING, progress=100 if cross_results else 0),
        ProcessingStep(name="Tampering Detection", status=ProcessingStatus.COMPLETED, progress=100),
        ProcessingStep(name="Face Verification", status=ProcessingStatus.COMPLETED if face_results else ProcessingStatus.WAITING, progress=100 if face_results else 0),
        ProcessingStep(name="Risk Assessment", status=ProcessingStatus.COMPLETED if risk_assessment else ProcessingStatus.WAITING, progress=100 if risk_assessment else 0),
    ]
    
    overall_progress = sum(s.progress for s in processing_steps) / len(processing_steps)
    
    return VerificationDetailResponse(
        case_id=case.case_id,
        passenger_name=passenger.full_name if passenger else "Unknown",
        passenger_id=passenger.passenger_id if passenger else "Unknown",
        timestamp=case.created_at,
        overall_status=VerificationStatus.VALID if case.overall_risk_level == RiskLevel.LOW else VerificationStatus.WARNING,
        overall_risk_level=case.overall_risk_level or RiskLevel.LOW,
        documents=[DocumentResponse.model_validate(d) for d in documents],
        ocr_results=[OCRResultResponse.model_validate(o) for o in ocr_results],
        mrz_results=[MRZResultResponse.model_validate(m) for m in mrz_results],
        validation_results=[ValidationResultResponse.model_validate(v) for v in val_results],
        tamper_results=[TamperResultResponse.model_validate(t) for t in tamper_results],
        face_results=[FaceResultResponse.model_validate(f) for f in face_results],
        cross_document_results=[CrossDocumentResultResponse.model_validate(c) for c in cross_results],
        risk_assessment=RiskAssessmentResponse.model_validate(risk_assessment) if risk_assessment else None,
        processing_steps=processing_steps,
    )


@router.post("/{case_id}/complete")
async def complete_verification(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    case_result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    from app.models.models import AuditLog
    
    audit = AuditLog(
        case_id=case.id,
        officer_id=current_officer.id,
        action="VERIFICATION_COMPLETED",
        details={"risk_level": case.overall_risk_level, "risk_score": case.risk_score}
    )
    db.add(audit)
    await db.commit()
    
    return {"message": "Verification completed successfully", "case_id": case_id}