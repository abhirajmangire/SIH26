from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.models import RiskAssessment, VerificationCase
from app.schemas.schemas import RiskAssessmentResponse
from app.api.v1.auth import get_current_officer


router = APIRouter()


@router.get("/case/{case_id}", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    case_result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    result = await db.execute(select(RiskAssessment).where(RiskAssessment.case_id == case.id))
    risk_assessment = result.scalar_one_or_none()
    if not risk_assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not found")
    return risk_assessment