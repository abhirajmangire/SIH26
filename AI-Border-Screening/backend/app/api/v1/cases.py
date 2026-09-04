from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.database.session import get_db
from app.models.models import (
    VerificationCase, Document, Passenger, Officer,
    DocumentType, ProcessingStatus, VerificationStatus, RiskLevel
)
from app.schemas.schemas import (
    CaseCreate, CaseResponse, CaseListResponse,
    DocumentUpload, DocumentResponse, DocumentQueueItem,
    DashboardStats, DashboardResponse, RecentActivity,
    PassengerHistoryItem, PassengerHistoryFilter,
    PassengerCreate, PassengerResponse
)
from app.api.v1.auth import get_current_officer
from app.services.ocr.ocr_service import process_ocr
from app.services.mrz.mrz_service import process_mrz
from app.services.validation.validation_service import process_validation
from app.services.tamper.tamper_service import process_tampering
from app.services.face.face_service import process_face_verification
from app.services.risk.risk_engine import calculate_risk
from app.utils.config import settings


router = APIRouter()


async def save_uploaded_file(file: UploadFile, case_id: str, doc_type: DocumentType) -> tuple[str, str]:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        ext = ".jpg"
    filename = f"{case_id}_{doc_type.value}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_path, filename


@router.post("", response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    passenger = await db.execute(select(Passenger).where(Passenger.id == case_data.passenger_id))
    passenger = passenger.scalar_one_or_none()
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    
    case = VerificationCase(
        case_id=case_data.case_id,
        officer_id=current_officer.id,
        passenger_id=case_data.passenger_id,
        overall_status=VerificationStatus.PENDING,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case


@router.get("", response_model=List[CaseListResponse])
async def list_cases(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(
        select(VerificationCase, Passenger, Officer)
        .join(Passenger, VerificationCase.passenger_id == Passenger.id)
        .join(Officer, VerificationCase.officer_id == Officer.id)
        .order_by(desc(VerificationCase.created_at))
        .offset(skip)
        .limit(limit)
    )
    cases = result.all()
    
    response = []
    for case, passenger, officer in cases:
        doc_count = await db.execute(
            select(func.count(Document.id)).where(Document.case_id == case.id)
        )
        doc_count = doc_count.scalar() or 0
        
        response.append(CaseListResponse(
            case_id=case.case_id,
            passenger_name=passenger.full_name,
            passenger_id=passenger.passenger_id,
            document_count=doc_count,
            overall_risk_level=case.overall_risk_level,
            overall_status=case.overall_status,
            officer_name=officer.full_name,
            created_at=case.created_at,
        ))
    return response


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/{case_id}/documents", response_model=DocumentResponse)
async def upload_document(
    case_id: str,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    file_path, filename = await save_uploaded_file(file, case_id, document_type)
    file_size = os.path.getsize(file_path)
    
    document = Document(
        case_id=case.id,
        document_type=document_type,
        file_path=file_path,
        original_filename=filename,
        file_size=file_size,
        mime_type=file.content_type,
        upload_status=ProcessingStatus.WAITING,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return document


@router.get("/{case_id}/documents", response_model=List[DocumentResponse])
async def get_case_documents(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    result = await db.execute(select(Document).where(Document.case_id == case.id))
    return result.scalars().all()


@router.get("/{case_id}/queue", response_model=List[DocumentQueueItem])
async def get_processing_queue(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    result = await db.execute(select(Document).where(Document.case_id == case.id))
    documents = result.scalars().all()
    
    queue = []
    for doc in documents:
        queue.append(DocumentQueueItem(
            id=doc.id,
            document_type=doc.document_type,
            upload_status=doc.upload_status,
            processing_progress=doc.processing_progress,
            current_step=doc.current_step,
        ))
    return queue


@router.post("/{case_id}/process")
async def start_processing(
    case_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.overall_status = VerificationStatus.PENDING
    await db.commit()
    
    background_tasks.add_task(process_case_pipeline, case_id)
    
    return {"message": "Processing started", "case_id": case_id}


async def process_case_pipeline(case_id: str):
    from app.database.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
        case = result.scalar_one_or_none()
        if not case:
            return
        
        result = await db.execute(select(Document).where(Document.case_id == case.id))
        documents = result.scalars().all()
        
        for doc in documents:
            doc.upload_status = ProcessingStatus.PROCESSING
            doc.current_step = "OCR Extraction"
            doc.processing_progress = 10
            await db.commit()
            
            ocr_result = await process_ocr(doc.file_path, doc.document_type, case.id, doc.id, db)
            
            doc.current_step = "MRZ Processing" if doc.document_type == DocumentType.PASSPORT else "Validation"
            doc.processing_progress = 40
            await db.commit()
            
            if doc.document_type == DocumentType.PASSPORT:
                await process_mrz(doc.file_path, ocr_result, case.id, doc.id, db)
            
            doc.current_step = "Document Validation"
            doc.processing_progress = 60
            await db.commit()
            
            await process_validation(doc, ocr_result, case.id, doc.id, db)
            
            doc.current_step = "Tampering Detection"
            doc.processing_progress = 80
            await db.commit()
            
            await process_tampering(doc.file_path, case.id, doc.id, db)
            
            doc.current_step = "Face Verification"
            doc.processing_progress = 90
            await db.commit()
            
            if doc.document_type == DocumentType.PASSPORT:
                await process_face_verification(doc.file_path, case.id, doc.id, db)
            
            doc.upload_status = ProcessingStatus.COMPLETED
            doc.processing_progress = 100
            doc.current_step = "Completed"
            await db.commit()
        
        case.current_step = "Cross-Document Verification"
        await db.commit()
        
        await process_cross_document_verification(case.id, db)
        
        case.current_step = "Risk Assessment"
        await db.commit()
        
        await calculate_risk(case.id, db)
        
        case.overall_status = VerificationStatus.VALID
        case.completed_at = datetime.utcnow()
        await db.commit()


async def process_cross_document_verification(case_id: int, db: AsyncSession):
    from app.models.models import CrossDocumentResult
    
    result = await db.execute(select(OCRResult).where(OCRResult.case_id == case_id))
    ocr_results = result.scalars().all()
    
    doc_fields = {}
    for ocr in ocr_results:
        doc_fields[ocr.document_id] = {f.field_name: f.value for f in ocr.extracted_fields}
    
    fields_to_compare = ["full_name", "date_of_birth", "passport_number", "nationality", "gender"]
    
    for field in fields_to_compare:
        values = {}
        for doc_id, fields in doc_fields.items():
            if field in fields:
                values[f"doc_{doc_id}"] = fields[field]
        
        if len(values) > 1:
            consistent = len(set(values.values())) == 1
            cross_doc = CrossDocumentResult(
                case_id=case_id,
                field_name=field,
                document_values=values,
                consistent=consistent,
                inconsistency_details=None if consistent else f"Values differ: {values}",
            )
            db.add(cross_doc)
    
    await db.commit()


@router.get("/dashboard/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    total_cases = await db.execute(select(func.count(VerificationCase.id)))
    total_cases = total_cases.scalar() or 0
    
    total_docs = await db.execute(select(func.count(Document.id)))
    total_docs = total_docs.scalar() or 0
    
    valid_docs = await db.execute(
        select(func.count(Document.id)).where(Document.upload_status == ProcessingStatus.COMPLETED)
    )
    valid_docs = valid_docs.scalar() or 0
    
    high_risk = await db.execute(
        select(func.count(VerificationCase.id)).where(VerificationCase.overall_risk_level == RiskLevel.HIGH)
    )
    high_risk = high_risk.scalar() or 0
    
    suspicious = await db.execute(
        select(func.count(VerificationCase.id)).where(VerificationCase.overall_risk_level == RiskLevel.MEDIUM)
    )
    suspicious = suspicious.scalar() or 0
    
    processing = await db.execute(
        select(func.count(Document.id)).where(Document.upload_status == ProcessingStatus.PROCESSING)
    )
    processing = processing.scalar() or 0
    
    risk_dist = await db.execute(
        select(VerificationCase.overall_risk_level, func.count(VerificationCase.id))
        .group_by(VerificationCase.overall_risk_level)
    )
    risk_dist = {str(risk): count for risk, count in risk_dist.all()}
    
    recent = await db.execute(
        select(VerificationCase, Passenger, Officer)
        .join(Passenger, VerificationCase.passenger_id == Passenger.id)
        .join(Officer, VerificationCase.officer_id == Officer.id)
        .order_by(desc(VerificationCase.created_at))
        .limit(10)
    )
    recent_cases = recent.all()
    
    recent_activity = []
    for case, passenger, officer in recent_cases:
        doc_count = await db.execute(
            select(func.count(Document.id)).where(Document.case_id == case.id)
        )
        doc_count = doc_count.scalar() or 0
        
        recent_activity.append(RecentActivity(
            case_id=case.case_id,
            passenger_name=passenger.full_name,
            document_count=doc_count,
            risk_level=case.overall_risk_level or RiskLevel.LOW,
            status=case.overall_status,
            timestamp=case.created_at,
        ))
    
    return DashboardResponse(
        stats=DashboardStats(
            total_passengers_screened=total_cases,
            total_documents_verified=total_docs,
            valid_documents=valid_docs,
            suspicious_documents=suspicious,
            high_risk_cases=high_risk,
            currently_processing=processing,
            risk_distribution=risk_dist,
        ),
        risk_distribution=risk_dist,
        recent_activity=recent_activity,
    )


@router.get("/history", response_model=List[PassengerHistoryItem])
async def get_passenger_history(
    passenger_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    risk_level: Optional[RiskLevel] = None,
    status: Optional[VerificationStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    query = select(VerificationCase, Passenger, Officer).join(
        Passenger, VerificationCase.passenger_id == Passenger.id
    ).join(Officer, VerificationCase.officer_id == Officer.id)
    
    if passenger_id:
        query = query.where(Passenger.passenger_id.ilike(f"%{passenger_id}%"))
    if date_from:
        query = query.where(VerificationCase.created_at >= date_from)
    if date_to:
        query = query.where(VerificationCase.created_at <= date_to)
    if risk_level:
        query = query.where(VerificationCase.overall_risk_level == risk_level)
    if status:
        query = query.where(VerificationCase.overall_status == status)
    
    query = query.order_by(desc(VerificationCase.created_at)).limit(100)
    
    result = await db.execute(query)
    cases = result.all()
    
    history = []
    for case, passenger, officer in cases:
        doc_count = await db.execute(
            select(func.count(Document.id)).where(Document.case_id == case.id)
        )
        doc_count = doc_count.scalar() or 0
        
        history.append(PassengerHistoryItem(
            case_id=case.case_id,
            passenger_name=passenger.full_name,
            passenger_id=passenger.passenger_id,
            date_time=case.created_at,
            document_count=doc_count,
            overall_risk=case.overall_risk_level or RiskLevel.LOW,
            verification_status=case.overall_status,
            officer_name=officer.full_name,
        ))
    return history


@router.post("/passengers", response_model=PassengerResponse)
async def create_passenger(
    passenger_data: PassengerCreate,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    existing = await db.execute(select(Passenger).where(Passenger.passenger_id == passenger_data.passenger_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Passenger ID already exists")
    
    passenger = Passenger(**passenger_data.model_dump())
    db.add(passenger)
    await db.commit()
    await db.refresh(passenger)
    return passenger


@router.get("/passengers/search")
async def search_passengers(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(
        select(Passenger).where(
            (Passenger.passenger_id.ilike(f"%{q}%")) |
            (Passenger.full_name.ilike(f"%{q}%")) |
            (Passenger.passport_number.ilike(f"%{q}%"))
        ).limit(20)
    )
    return result.scalars().all()