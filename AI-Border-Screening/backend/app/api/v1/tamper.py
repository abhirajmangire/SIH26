from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.models import TamperResult, VerificationCase
from app.schemas.schemas import TamperResultResponse
from app.api.v1.auth import get_current_officer


router = APIRouter()


@router.get("/case/{case_id}", response_model=list[TamperResultResponse])
async def get_tamper_results(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    case_result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    result = await db.execute(select(TamperResult).where(TamperResult.case_id == case.id))
    return result.scalars().all()


@router.get("/document/{document_id}", response_model=TamperResultResponse)
async def get_document_tamper(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(TamperResult).where(TamperResult.document_id == document_id))
    tamper_result = result.scalar_one_or_none()
    if not tamper_result:
        raise HTTPException(status_code=404, detail="Tampering result not found")
    return tamper_result