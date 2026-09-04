from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database.session import get_db
from app.models.models import (
    VerificationCase, Document, Passenger, Officer,
    ProcessingStatus, RiskLevel, VerificationStatus
)
from app.schemas.schemas import DashboardResponse, DashboardStats, RecentActivity
from app.api.v1.auth import get_current_officer


router = APIRouter()


@router.get("/stats", response_model=DashboardResponse)
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
    risk_dist = {str(risk.value if risk else "unknown"): count for risk, count in risk_dist.all()}
    
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