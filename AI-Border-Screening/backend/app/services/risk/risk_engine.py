from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import (
    RiskAssessment, VerificationCase, Document, OCRResult, MRZResult,
    ValidationResult, TamperResult, FaceResult, CrossDocumentResult,
    RiskLevel, ProcessingStatus
)
from app.schemas.schemas import RiskFactor


class RiskEngine:
    def __init__(self):
        self.weights = {
            "document_validation": 0.15,
            "mrz_checksum": 0.10,
            "ocr_mrz_consistency": 0.15,
            "cross_document_consistency": 0.15,
            "tampering_probability": 0.25,
            "face_similarity": 0.15,
            "expired_document": 0.05,
        }
        
        self.thresholds = {
            "low_max": 0.3,
            "medium_max": 0.6,
        }
    
    async def calculate_risk(self, case_id: int, db: AsyncSession) -> RiskAssessment:
        case_result = await db.execute(select(VerificationCase).where(VerificationCase.id == case_id))
        case = case_result.scalar_one_or_none()
        if not case:
            raise ValueError("Case not found")
        
        factors = []
        
        doc_result = await db.execute(select(Document).where(Document.case_id == case_id))
        documents = doc_result.scalars().all()
        
        val_score = await self._assess_document_validation(case_id, db)
        factors.append(RiskFactor(
            factor="Document Validation",
            weight=self.weights["document_validation"],
            contribution=val_score * self.weights["document_validation"],
            description="All documents passed validation checks" if val_score < 0.3 else "Some documents failed validation"
        ))
        
        mrz_score = await self._assess_mrz(case_id, db)
        factors.append(RiskFactor(
            factor="MRZ Checksum",
            weight=self.weights["mrz_checksum"],
            contribution=mrz_score * self.weights["mrz_checksum"],
            description="MRZ checksums valid" if mrz_score < 0.3 else "MRZ checksum failures detected"
        ))
        
        ocr_mrz_score = await self._assess_ocr_mrz_consistency(case_id, db)
        factors.append(RiskFactor(
            factor="OCR-MRZ Consistency",
            weight=self.weights["ocr_mrz_consistency"],
            contribution=ocr_mrz_score * self.weights["ocr_mrz_consistency"],
            description="OCR and MRZ fields consistent" if ocr_mrz_score < 0.3 else "OCR-MRZ field mismatches detected"
        ))
        
        cross_doc_score = await self._assess_cross_document(case_id, db)
        factors.append(RiskFactor(
            factor="Cross-Document Consistency",
            weight=self.weights["cross_document_consistency"],
            contribution=cross_doc_score * self.weights["cross_document_consistency"],
            description="Information consistent across documents" if cross_doc_score < 0.3 else "Cross-document inconsistencies found"
        ))
        
        tamper_score = await self._assess_tampering(case_id, db)
        factors.append(RiskFactor(
            factor="Tampering Detection",
            weight=self.weights["tampering_probability"],
            contribution=tamper_score * self.weights["tampering_probability"],
            description="No significant tampering detected" if tamper_score < 0.3 else "Possible document manipulation detected"
        ))
        
        face_score = await self._assess_face(case_id, db)
        factors.append(RiskFactor(
            factor="Face Verification",
            weight=self.weights["face_similarity"],
            contribution=face_score * self.weights["face_similarity"],
            description="Face match successful" if face_score < 0.3 else "Face similarity below threshold"
        ))
        
        expiry_score = await self._assess_expiry(case_id, db)
        factors.append(RiskFactor(
            factor="Document Expiry",
            weight=self.weights["expired_document"],
            contribution=expiry_score * self.weights["expired_document"],
            description="All documents valid" if expiry_score < 0.3 else "Expired documents detected"
        ))
        
        total_score = sum(f.contribution for f in factors)
        
        if total_score <= self.thresholds["low_max"]:
            risk_level = RiskLevel.LOW
        elif total_score <= self.thresholds["medium_max"]:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        risk_assessment = RiskAssessment(
            case_id=case_id,
            risk_level=risk_level,
            risk_score=total_score,
            contributing_factors=[f.model_dump() for f in factors],
            factor_weights=self.weights,
            threshold_config=self.thresholds,
        )
        db.add(risk_assessment)
        await db.commit()
        await db.refresh(risk_assessment)
        
        case.overall_risk_level = risk_level
        case.risk_score = total_score
        case.risk_reasons = [f.description for f in factors if f.contribution > 0.05]
        case.overall_status = risk_level == RiskLevel.LOW
        await db.commit()
        
        return risk_assessment
    
    async def _assess_document_validation(self, case_id: int, db: AsyncSession) -> float:
        result = await db.execute(select(ValidationResult).where(ValidationResult.case_id == case_id))
        validations = result.scalars().all()
        
        if not validations:
            return 0.5
        
        failed = sum(1 for v in validations if not v.overall_valid)
        return failed / len(validations)
    
    async def _assess_mrz(self, case_id: int, db: AsyncSession) -> float:
        result = await db.execute(select(MRZResult).where(MRZResult.case_id == case_id))
        mrz_results = result.scalars().all()
        
        if not mrz_results:
            return 0.0
        
        failed = sum(1 for m in mrz_results if m.checksum_valid is False)
        return failed / len(mrz_results)
    
    async def _assess_ocr_mrz_consistency(self, case_id: int, db: AsyncSession) -> float:
        result = await db.execute(select(MRZResult).where(MRZResult.case_id == case_id))
        mrz_results = result.scalars().all()
        
        if not mrz_results:
            return 0.0
        
        total_mismatch = 0
        total_compared = 0
        for mrz in mrz_results:
            if mrz.ocr_mrz_comparison:
                for comp in mrz.ocr_mrz_comparison:
                    total_compared += 1
                    if not comp.get('match', True):
                        total_mismatch += 1
        
        return total_mismatch / total_compared if total_compared > 0 else 0.0
    
    async def _assess_cross_document(self, case_id: int, db: AsyncSession) -> float:
        result = await db.execute(select(CrossDocumentResult).where(CrossDocumentResult.case_id == case_id))
        cross_results = result.scalars().all()
        
        if not cross_results:
            return 0.0
        
        inconsistent = sum(1 for c in cross_results if c.consistent is False)
        return inconsistent / len(cross_results)
    
    async def _assess_tampering(self, case_id: int, db: AsyncSession) -> float:
        result = await db.execute(select(TamperResult).where(TamperResult.case_id == case_id))
        tamper_results = result.scalars().all()
        
        if not tamper_results:
            return 0.0
        
        max_prob = max((t.tampering_probability or 0.0) for t in tamper_results)
        return max_prob
    
    async def _assess_face(self, case_id: int, db: AsyncSession) -> float:
        result = await db.execute(select(FaceResult).where(FaceResult.case_id == case_id))
        face_results = result.scalars().all()
        
        if not face_results:
            return 0.0
        
        min_similarity = min((f.similarity_score or 1.0) for f in face_results)
        return 1.0 - min_similarity
    
    async def _assess_expiry(self, case_id: int, db: AsyncSession) -> float:
        result = await db.execute(select(ValidationResult).where(ValidationResult.case_id == case_id))
        validations = result.scalars().all()
        
        expired_count = 0
        for v in validations:
            if v.errors:
                for err in v.errors:
                    if "expired" in err.lower():
                        expired_count += 1
                        break
        
        return expired_count / len(validations) if validations else 0.0


risk_engine = RiskEngine()


async def calculate_risk(case_id: int, db: AsyncSession) -> RiskAssessment:
    return await risk_engine.calculate_risk(case_id, db)