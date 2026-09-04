from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.models import ValidationResult, VerificationCase
from app.schemas.schemas import ValidationResultResponse
from app.api.v1.auth import get_current_officer


router = APIRouter()


@router.get("/case/{case_id}", response_model=list[ValidationResultResponse])
async def get_validation_results(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    case_result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    result = await db.execute(select(ValidationResult).where(ValidationResult.case_id == case.id))
    return result.scalars().all()


@router.get("/document/{document_id}", response_model=ValidationResultResponse)
async def get_document_validation(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(ValidationResult).where(ValidationResult.document_id == document_id))
    validation_result = result.scalar_one_or_none()
    if not validation_result:
        raise HTTPException(status_code=404, detail="Validation result not found")
    return validation_result