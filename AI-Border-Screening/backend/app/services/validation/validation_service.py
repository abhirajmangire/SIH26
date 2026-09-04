from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import re

from app.models.models import ValidationResult, Document, DocumentType, ProcessingStatus
from app.schemas.schemas import ValidationField


class ValidationService:
    def __init__(self):
        self.reference_db = self._load_reference_db()
    
    def _load_reference_db(self) -> Dict[str, Any]:
        return {
            "passports": {
                "Z1234567": {"status": "valid", "blacklisted": False, "name": "RAJESH KUMAR SHARMA"},
                "Z9999999": {"status": "expired", "blacklisted": False, "name": "EXPIRED USER"},
                "Z8888888": {"status": "blacklisted", "blacklisted": True, "name": "SUSPECT PERSON"},
            },
            "visas": {
                "VISA-2024-001234": {"status": "valid", "passport_number": "Z1234567"},
                "VISA-2024-999999": {"status": "expired", "passport_number": "Z9999999"},
            },
            "national_ids": {
                "IN123456789012": {"status": "valid", "name": "RAJESH KUMAR SHARMA"},
            },
            "permits": {
                "PERMIT-2024-001": {"status": "valid", "passport_number": "Z1234567"},
            }
        }
    
    def validate_passport(self, fields: List[Dict]) -> tuple[List[ValidationField], List[str], List[str]]:
        field_dict = {f['field_name']: f['value'] for f in fields}
        validations = []
        warnings = []
        errors = []
        
        required = ['full_name', 'passport_number', 'nationality', 'date_of_birth', 'gender', 'date_of_expiry']
        for req in required:
            if req not in field_dict or not field_dict[req]:
                validations.append(ValidationField(field_name=req, value="", valid=False, message="Required field missing"))
                errors.append(f"Missing required field: {req}")
            else:
                validations.append(ValidationField(field_name=req, value=field_dict[req], valid=True))
        
        if 'passport_number' in field_dict:
            pn = field_dict['passport_number']
            valid_format = bool(re.match(r'^[A-Z0-9]{6,9}$', pn))
            validations.append(ValidationField(field_name='passport_number_format', value=pn, valid=valid_format, 
                message="Valid format" if valid_format else "Invalid passport number format"))
            if not valid_format:
                errors.append("Invalid passport number format")
        
        if 'date_of_expiry' in field_dict:
            try:
                exp_date = self._parse_date(field_dict['date_of_expiry'])
                if exp_date and exp_date < datetime.now():
                    validations.append(ValidationField(field_name='date_of_expiry', value=field_dict['date_of_expiry'], valid=False, message="Passport expired"))
                    errors.append("Passport has expired")
                else:
                    validations.append(ValidationField(field_name='date_of_expiry', value=field_dict['date_of_expiry'], valid=True))
            except:
                warnings.append("Could not parse expiry date")
        
        if 'date_of_birth' in field_dict:
            try:
                dob = self._parse_date(field_dict['date_of_birth'])
                if dob:
                    age = (datetime.now() - dob).days / 365.25
                    if age < 0 or age > 120:
                        warnings.append("Unusual age from date of birth")
            except:
                pass
        
        return validations, warnings, errors
    
    def validate_visa(self, fields: List[Dict]) -> tuple[List[ValidationField], List[str], List[str]]:
        field_dict = {f['field_name']: f['value'] for f in fields}
        validations = []
        warnings = []
        errors = []
        
        required = ['visa_number', 'full_name', 'passport_number', 'visa_type', 'valid_from', 'valid_until']
        for req in required:
            if req not in field_dict or not field_dict[req]:
                validations.append(ValidationField(field_name=req, value="", valid=False, message="Required field missing"))
                errors.append(f"Missing required field: {req}")
            else:
                validations.append(ValidationField(field_name=req, value=field_dict[req], valid=True))
        
        if 'valid_until' in field_dict:
            try:
                exp_date = self._parse_date(field_dict['valid_until'])
                if exp_date and exp_date < datetime.now():
                    validations.append(ValidationField(field_name='valid_until', value=field_dict['valid_until'], valid=False, message="Visa expired"))
                    errors.append("Visa has expired")
                else:
                    validations.append(ValidationField(field_name='valid_until', value=field_dict['valid_until'], valid=True))
            except:
                warnings.append("Could not parse visa expiry date")
        
        return validations, warnings, errors
    
    def validate_national_id(self, fields: List[Dict]) -> tuple[List[ValidationField], List[str], List[str]]:
        field_dict = {f['field_name']: f['value'] for f in fields}
        validations = []
        warnings = []
        errors = []
        
        required = ['full_name', 'id_number', 'date_of_birth', 'nationality']
        for req in required:
            if req not in field_dict or not field_dict[req]:
                validations.append(ValidationField(field_name=req, value="", valid=False, message="Required field missing"))
                errors.append(f"Missing required field: {req}")
            else:
                validations.append(ValidationField(field_name=req, value=field_dict[req], valid=True))
        
        if 'id_number' in field_dict:
            id_num = field_dict['id_number']
            valid_format = bool(re.match(r'^[A-Z0-9]{10,14}$', id_num))
            validations.append(ValidationField(field_name='id_number_format', value=id_num, valid=valid_format,
                message="Valid format" if valid_format else "Invalid ID number format"))
            if not valid_format:
                errors.append("Invalid national ID format")
        
        return validations, warnings, errors
    
    def validate_permit(self, fields: List[Dict]) -> tuple[List[ValidationField], List[str], List[str]]:
        field_dict = {f['field_name']: f['value'] for f in fields}
        validations = []
        warnings = []
        errors = []
        
        required = ['full_name', 'passport_number', 'permit_type', 'valid_from', 'valid_until']
        for req in required:
            if req not in field_dict or not field_dict[req]:
                validations.append(ValidationField(field_name=req, value="", valid=False, message="Required field missing"))
                errors.append(f"Missing required field: {req}")
            else:
                validations.append(ValidationField(field_name=req, value=field_dict[req], valid=True))
        
        if 'valid_until' in field_dict:
            try:
                exp_date = self._parse_date(field_dict['valid_until'])
                if exp_date and exp_date < datetime.now():
                    validations.append(ValidationField(field_name='valid_until', value=field_dict['valid_until'], valid=False, message="Permit expired"))
                    errors.append("Permit has expired")
                else:
                    validations.append(ValidationField(field_name='valid_until', value=field_dict['valid_until'], valid=True))
            except:
                warnings.append("Could not parse permit expiry date")
        
        return validations, warnings, errors
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%y', '%d-%m-%y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        return None
    
    def check_reference_db(self, document_type: DocumentType, fields: List[Dict]) -> Dict[str, Any]:
        field_dict = {f['field_name']: f['value'] for f in fields}
        result = {"found": False, "status": "unknown", "details": {}}
        
        if document_type == DocumentType.PASSPORT and 'passport_number' in field_dict:
            pn = field_dict['passport_number']
            if pn in self.reference_db['passports']:
                result = {"found": True, **self.reference_db['passports'][pn]}
        elif document_type == DocumentType.VISA and 'visa_number' in field_dict:
            vn = field_dict['visa_number']
            if vn in self.reference_db['visas']:
                result = {"found": True, **self.reference_db['visas'][vn]}
        elif document_type == DocumentType.NATIONAL_ID and 'id_number' in field_dict:
            idn = field_dict['id_number']
            if idn in self.reference_db['national_ids']:
                result = {"found": True, **self.reference_db['national_ids'][idn]}
        elif document_type == DocumentType.PERMIT and 'permit_number' in field_dict:
            pn = field_dict['permit_number']
            if pn in self.reference_db['permits']:
                result = {"found": True, **self.reference_db['permits'][pn]}
        
        return result


validation_service = ValidationService()


async def process_validation(
    document: Document,
    ocr_result: OCRResult,
    case_id: int,
    document_id: int,
    db: AsyncSession
) -> ValidationResult:
    import time
    start_time = time.time()
    
    if document.document_type == DocumentType.PASSPORT:
        validations, warnings, errors = validation_service.validate_passport(ocr_result.extracted_fields)
        ref_check = validation_service.check_reference_db(DocumentType.PASSPORT, ocr_result.extracted_fields)
    elif document.document_type == DocumentType.VISA:
        validations, warnings, errors = validation_service.validate_visa(ocr_result.extracted_fields)
        ref_check = validation_service.check_reference_db(DocumentType.VISA, ocr_result.extracted_fields)
    elif document.document_type == DocumentType.NATIONAL_ID:
        validations, warnings, errors = validation_service.validate_national_id(ocr_result.extracted_fields)
        ref_check = validation_service.check_reference_db(DocumentType.NATIONAL_ID, ocr_result.extracted_fields)
    elif document.document_type == DocumentType.PERMIT:
        validations, warnings, errors = validation_service.validate_permit(ocr_result.extracted_fields)
        ref_check = validation_service.check_reference_db(DocumentType.PERMIT, ocr_result.extracted_fields)
    else:
        validations, warnings, errors = [], ["Unknown document type"], ["Unknown document type"]
        ref_check = {"found": False, "status": "unknown"}
    
    overall_valid = len(errors) == 0 and all(v.valid for v in validations)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    validation_result = ValidationResult(
        case_id=case_id,
        document_id=document_id,
        field_validations=[v.model_dump() for v in validations],
        overall_valid=overall_valid,
        warnings=warnings if warnings else None,
        errors=errors if errors else None,
        reference_db_check=ref_check,
        processing_time_ms=processing_time,
        status=ProcessingStatus.COMPLETED if overall_valid else ProcessingStatus.WARNING,
    )
    db.add(validation_result)
    await db.commit()
    await db.refresh(validation_result)
    
    doc = await db.get(Document, document_id)
    if doc:
        doc.processing_progress = 70
        doc.current_step = "Validation Completed"
        await db.commit()
    
    return validation_result