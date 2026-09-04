from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.models import Document, VerificationCase
from app.schemas.schemas import DocumentResponse
from app.api.v1.auth import get_current_officer


router = APIRouter()


@router.get("/case/{case_id}", response_model=list[DocumentResponse])
async def get_case_documents(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    case_result = await db.execute(select(VerificationCase).where(VerificationCase.case_id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    result = await db.execute(select(Document).where(Document.case_id == case.id))
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_officer)
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    import os
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    await db.delete(document)
    await db.commit()
    
    return {"message": "Document deleted successfully"}