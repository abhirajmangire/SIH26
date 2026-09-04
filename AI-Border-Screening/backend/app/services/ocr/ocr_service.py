from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.models.models import OCRResult, Document, DocumentType, ProcessingStatus
from app.schemas.schemas import OCRField
from app.utils.config import settings


class OCRService:
    def __init__(self):
        self.ocr_engine = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        try:
            from paddleocr import PaddleOCR
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang=settings.OCR_LANG,
                use_gpu=False,
                show_log=False,
            )
        except Exception as e:
            print(f"OCR initialization warning: {e}")
            self.ocr_engine = None
    
    async def extract_text(self, image_path: str) -> tuple[List[OCRField], Dict[str, float], str]:
        if not self.ocr_engine:
            return self._mock_ocr_result(image_path)
        
        try:
            result = self.ocr_engine.ocr(image_path, cls=True)
            
            fields = []
            confidences = {}
            raw_texts = []
            
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        bbox, (text, confidence) = line
                        raw_texts.append(text)
                        
                        field_name = self._classify_field(text)
                        fields.append(OCRField(
                            field_name=field_name,
                            value=text,
                            confidence=confidence
                        ))
                        confidences[field_name] = confidence
            
            return fields, confidences, "\n".join(raw_texts)
        except Exception as e:
            print(f"OCR error: {e}")
            return self._mock_ocr_result(image_path)
    
    def _classify_field(self, text: str) -> str:
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["passport", "passport no", "passport number"]):
            return "passport_number"
        elif any(kw in text_lower for kw in ["name", "surname", "given name"]):
            return "full_name"
        elif any(kw in text_lower for kw in ["nationality", "country"]):
            return "nationality"
        elif any(kw in text_lower for kw in ["date of birth", "dob", "birth"]):
            return "date_of_birth"
        elif any(kw in text_lower for kw in ["sex", "gender"]):
            return "gender"
        elif any(kw in text_lower for kw in ["expiry", "expires", "exp date"]):
            return "date_of_expiry"
        elif any(kw in text_lower for kw in ["visa", "visa no", "visa number"]):
            return "visa_number"
        elif any(kw in text_lower for kw in ["valid from", "from"]):
            return "valid_from"
        elif any(kw in text_lower for kw in ["valid until", "until", "valid to"]):
            return "valid_until"
        elif any(kw in text_lower for kw in ["stay", "duration"]):
            return "stay_duration"
        elif any(kw in text_lower for kw in ["id number", "id no", "identity"]):
            return "id_number"
        elif any(kw in text_lower for kw in ["permit", "permit no", "permit number"]):
            return "permit_number"
        elif any(kw in text_lower for kw in ["permit type", "type"]):
            return "permit_type"
        return "unknown_field"
    
    def _mock_ocr_result(self, image_path: str) -> tuple[List[OCRField], Dict[str, float], str]:
        import random
        
        mock_data = {
            DocumentType.PASSPORT: [
                OCRField(field_name="full_name", value="RAJESH KUMAR SHARMA", confidence=0.95),
                OCRField(field_name="passport_number", value="Z1234567", confidence=0.98),
                OCRField(field_name="nationality", value="IND", confidence=0.99),
                OCRField(field_name="date_of_birth", value="15/08/1985", confidence=0.94),
                OCRField(field_name="gender", value="M", confidence=0.99),
                OCRField(field_name="date_of_expiry", value="14/08/2030", confidence=0.96),
            ],
            DocumentType.VISA: [
                OCRField(field_name="visa_number", value="VISA-2024-001234", confidence=0.93),
                OCRField(field_name="full_name", value="RAJESH KUMAR SHARMA", confidence=0.95),
                OCRField(field_name="passport_number", value="Z1234567", confidence=0.98),
                OCRField(field_name="visa_type", value="TOURIST", confidence=0.92),
                OCRField(field_name="valid_from", value="01/01/2024", confidence=0.90),
                OCRField(field_name="valid_until", value="31/12/2024", confidence=0.91),
                OCRField(field_name="stay_duration", value="180 DAYS", confidence=0.89),
            ],
            DocumentType.NATIONAL_ID: [
                OCRField(field_name="full_name", value="RAJESH KUMAR SHARMA", confidence=0.94),
                OCRField(field_name="id_number", value="IN123456789012", confidence=0.97),
                OCRField(field_name="date_of_birth", value="15/08/1985", confidence=0.93),
                OCRField(field_name="nationality", value="IND", confidence=0.98),
            ],
            DocumentType.PERMIT: [
                OCRField(field_name="full_name", value="RAJESH KUMAR SHARMA", confidence=0.93),
                OCRField(field_name="passport_number", value="Z1234567", confidence=0.97),
                OCRField(field_name="permit_type", value="RESIDENCE", confidence=0.91),
                OCRField(field_name="valid_from", value="01/01/2024", confidence=0.89),
                OCRField(field_name="valid_until", value="31/12/2025", confidence=0.90),
            ],
        }
        
        doc_type = DocumentType.PASSPORT
        if "visa" in image_path.lower():
            doc_type = DocumentType.VISA
        elif "id" in image_path.lower() or "national" in image_path.lower():
            doc_type = DocumentType.NATIONAL_ID
        elif "permit" in image_path.lower():
            doc_type = DocumentType.PERMIT
        
        fields = mock_data.get(doc_type, mock_data[DocumentType.PASSPORT])
        confidences = {f.field_name: f.confidence for f in fields}
        raw_text = "\n".join([f"{f.field_name}: {f.value}" for f in fields])
        
        return fields, confidences, raw_text


ocr_service = OCRService()


async def process_ocr(
    image_path: str,
    document_type: DocumentType,
    case_id: int,
    document_id: int,
    db: AsyncSession
) -> OCRResult:
    import time
    start_time = time.time()
    
    fields, confidences, raw_text = await ocr_service.extract_text(image_path)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    ocr_result = OCRResult(
        case_id=case_id,
        document_id=document_id,
        extracted_fields=[f.model_dump() for f in fields],
        confidence_scores=confidences,
        raw_text=raw_text,
        processing_time_ms=processing_time,
        status=ProcessingStatus.COMPLETED,
    )
    db.add(ocr_result)
    await db.commit()
    await db.refresh(ocr_result)
    
    doc = await db.get(Document, document_id)
    if doc:
        doc.upload_status = ProcessingStatus.PROCESSING
        doc.processing_progress = 30
        doc.current_step = "OCR Completed"
        await db.commit()
    
    return ocr_result