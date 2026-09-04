import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.models.models import (
    Officer, Passenger, VerificationCase, Document,
    OCRResult, MRZResult, ValidationResult, TamperResult,
    FaceResult, CrossDocumentResult, RiskAssessment, AuditLog,
    DocumentType, ProcessingStatus, VerificationStatus, RiskLevel
)
from app.services.auth import get_password_hash, create_demo_officer


async def seed_demo_data():
    async with AsyncSessionLocal() as db:
        # Create demo officer
        officer = await create_demo_officer(db)
        print(f"Created demo officer: {officer.officer_id}")

        # Create demo passengers
        passengers_data = [
            {
                "passenger_id": "PAX-2024-001",
                "full_name": "RAJESH KUMAR SHARMA",
                "date_of_birth": datetime(1985, 8, 15),
                "nationality": "IND",
                "gender": "M",
                "passport_number": "Z1234567",
            },
            {
                "passenger_id": "PAX-2024-002",
                "full_name": "PRIYA SINGH",
                "date_of_birth": datetime(1990, 3, 22),
                "nationality": "IND",
                "gender": "F",
                "passport_number": "Z9999999",
            },
            {
                "passenger_id": "PAX-2024-003",
                "full_name": "AMIT PATEL",
                "date_of_birth": datetime(1988, 11, 5),
                "nationality": "IND",
                "gender": "M",
                "passport_number": "Z8888888",
            },
            {
                "passenger_id": "PAX-2024-004",
                "full_name": "SUNITA DEVI",
                "date_of_birth": datetime(1992, 7, 18),
                "nationality": "IND",
                "gender": "F",
                "passport_number": "Z7777777",
            },
            {
                "passenger_id": "PAX-2024-005",
                "full_name": "VIKRAM SINGH",
                "date_of_birth": datetime(1983, 12, 30),
                "nationality": "IND",
                "gender": "M",
                "passport_number": "Z6666666",
            },
        ]

        passengers = []
        for p_data in passengers_data:
            passenger = Passenger(**p_data)
            db.add(passenger)
            passengers.append(passenger)
        
        await db.flush()
        print(f"Created {len(passengers)} demo passengers")

        # Create demo cases with different risk scenarios
        cases_data = [
            {
                "case_id": "CASE-240115-001",
                "passenger": passengers[0],
                "risk_level": RiskLevel.LOW,
                "risk_score": 0.12,
                "status": VerificationStatus.VALID,
                "reasons": [],
                "documents": [
                    {"type": DocumentType.PASSPORT, "filename": "passport_001.jpg"},
                    {"type": DocumentType.VISA, "filename": "visa_001.jpg"},
                    {"type": DocumentType.NATIONAL_ID, "filename": "national_id_001.jpg"},
                ],
            },
            {
                "case_id": "CASE-240115-002",
                "passenger": passengers[1],
                "risk_level": RiskLevel.HIGH,
                "risk_score": 0.78,
                "status": VerificationStatus.WARNING,
                "reasons": ["OCR ↔ MRZ DOB mismatch", "Passport expired"],
                "documents": [
                    {"type": DocumentType.PASSPORT, "filename": "passport_002.jpg"},
                    {"type": DocumentType.VISA, "filename": "visa_002.jpg"},
                ],
            },
            {
                "case_id": "CASE-240115-003",
                "passenger": passengers[2],
                "risk_level": RiskLevel.HIGH,
                "risk_score": 0.85,
                "status": VerificationStatus.WARNING,
                "reasons": ["Tampering probability: 91%", "Possible photo manipulation"],
                "documents": [
                    {"type": DocumentType.PASSPORT, "filename": "passport_003.jpg"},
                    {"type": DocumentType.NATIONAL_ID, "filename": "national_id_003.jpg"},
                ],
            },
            {
                "case_id": "CASE-240115-004",
                "passenger": passengers[3],
                "risk_level": RiskLevel.HIGH,
                "risk_score": 0.72,
                "status": VerificationStatus.WARNING,
                "reasons": ["Visa passport number mismatch", "Cross-document inconsistency"],
                "documents": [
                    {"type": DocumentType.PASSPORT, "filename": "passport_004.jpg"},
                    {"type": DocumentType.VISA, "filename": "visa_004.jpg"},
                    {"type": DocumentType.PERMIT, "filename": "permit_004.jpg"},
                ],
            },
            {
                "case_id": "CASE-240115-005",
                "passenger": passengers[4],
                "risk_level": RiskLevel.MEDIUM,
                "risk_score": 0.45,
                "status": VerificationStatus.WARNING,
                "reasons": ["Face similarity below threshold (58.2%)", "Possible identity mismatch"],
                "documents": [
                    {"type": DocumentType.PASSPORT, "filename": "passport_005.jpg"},
                    {"type": DocumentType.NATIONAL_ID, "filename": "national_id_005.jpg"},
                ],
            },
        ]

        for case_data in cases_data:
            case = VerificationCase(
                case_id=case_data["case_id"],
                officer_id=officer.id,
                passenger_id=case_data["passenger"].id,
                overall_status=case_data["status"],
                overall_risk_level=case_data["risk_level"],
                risk_score=case_data["risk_score"],
                risk_reasons=case_data["reasons"],
                started_at=datetime.utcnow() - timedelta(hours=2),
                completed_at=datetime.utcnow() - timedelta(hours=1),
            )
            db.add(case)
            await db.flush()

            # Create documents
            documents = []
            for i, doc_data in enumerate(case_data["documents"]):
                doc = Document(
                    case_id=case.id,
                    document_type=doc_data["type"],
                    file_path=f"/storage/documents/{doc_data['filename']}",
                    original_filename=doc_data["filename"],
                    file_size=2048576,
                    mime_type="image/jpeg",
                    upload_status=ProcessingStatus.COMPLETED,
                    processing_progress=100.0,
                    current_step="Completed",
                )
                db.add(doc)
                documents.append(doc)

            await db.flush()

            # Create OCR results
            for doc in documents:
                if doc.document_type == DocumentType.PASSPORT:
                    ocr_fields = [
                        {"field_name": "full_name", "value": case_data["passenger"].full_name, "confidence": 0.95},
                        {"field_name": "passport_number", "value": case_data["passenger"].passport_number, "confidence": 0.98},
                        {"field_name": "nationality", "value": "IND", "confidence": 0.99},
                        {"field_name": "date_of_birth", "value": case_data["passenger"].date_of_birth.strftime("%d/%m/%Y"), "confidence": 0.94},
                        {"field_name": "gender", "value": case_data["passenger"].gender, "confidence": 0.99},
                        {"field_name": "date_of_expiry", "value": "14/08/2030", "confidence": 0.96},
                    ]
                elif doc.document_type == DocumentType.VISA:
                    ocr_fields = [
                        {"field_name": "visa_number", "value": f"VISA-2024-{doc.id:06d}", "confidence": 0.93},
                        {"field_name": "full_name", "value": case_data["passenger"].full_name, "confidence": 0.95},
                        {"field_name": "passport_number", "value": case_data["passenger"].passport_number if doc_data["type"] != DocumentType.VISA or case_data["case_id"] != "CASE-240115-004" else "Z9999999", "confidence": 0.98},
                        {"field_name": "visa_type", "value": "TOURIST", "confidence": 0.92},
                        {"field_name": "valid_from", "value": "01/01/2024", "confidence": 0.90},
                        {"field_name": "valid_until", "value": "31/12/2024" if case_data["case_id"] != "CASE-240115-002" else "31/12/2022", "confidence": 0.91},
                        {"field_name": "stay_duration", "value": "180 DAYS", "confidence": 0.89},
                    ]
                elif doc.document_type == DocumentType.NATIONAL_ID:
                    ocr_fields = [
                        {"field_name": "full_name", "value": case_data["passenger"].full_name, "confidence": 0.94},
                        {"field_name": "id_number", "value": f"IN{doc.id:012d}", "confidence": 0.97},
                        {"field_name": "date_of_birth", "value": case_data["passenger"].date_of_birth.strftime("%d/%m/%Y"), "confidence": 0.93},
                        {"field_name": "nationality", "value": "IND", "confidence": 0.98},
                    ]
                elif doc.document_type == DocumentType.PERMIT:
                    ocr_fields = [
                        {"field_name": "full_name", "value": case_data["passenger"].full_name, "confidence": 0.93},
                        {"field_name": "passport_number", "value": case_data["passenger"].passport_number, "confidence": 0.97},
                        {"field_name": "permit_type", "value": "RESIDENCE", "confidence": 0.91},
                        {"field_name": "valid_from", "value": "01/01/2024", "confidence": 0.89},
                        {"field_name": "valid_until", "value": "31/12/2025", "confidence": 0.90},
                    ]

                ocr_result = OCRResult(
                    case_id=case.id,
                    document_id=doc.id,
                    extracted_fields=ocr_fields,
                    confidence_scores={f["field_name"]: f["confidence"] for f in ocr_fields},
                    raw_text="\n".join([f"{f['field_name']}: {f['value']}" for f in ocr_fields]),
                    processing_time_ms=1200,
                    status=ProcessingStatus.COMPLETED,
                )
                db.add(ocr_result)

                # MRZ for passport only
                if doc.document_type == DocumentType.PASSPORT:
                    mrz_result = MRZResult(
                        case_id=case.id,
                        document_id=doc.id,
                        mrz_detected=True,
                        mrz_raw=f"P<INDSHARMA<<{case_data['passenger'].full_name.replace(' ', '<')}<<<<<<<<<<<<<<<<<<<<<\n{case_data['passenger'].passport_number}<8IND850815<7M300814<5<<<<<<<<<<<<<<<<<",
                        mrz_type="TD3",
                        decoded_fields={
                            "surname": case_data["passenger"].full_name.split()[-1],
                            "given_names": " ".join(case_data["passenger"].full_name.split()[:-1]),
                            "passport_number": case_data["passenger"].passport_number,
                            "nationality": "IND",
                            "date_of_birth": case_data["passenger"].date_of_birth.strftime("%y%m%d"),
                            "gender": case_data["passenger"].gender,
                            "date_of_expiry": "300814",
                        },
                        checksum_valid=case_data["case_id"] != "CASE-240115-002",
                        checksum_details={"overall_valid": case_data["case_id"] != "CASE-240115-002"},
                        ocr_mrz_comparison=[
                            {"field_name": "passport_number", "ocr_value": case_data["passenger"].passport_number, "mrz_value": case_data["passenger"].passport_number, "match": True},
                            {"field_name": "date_of_birth", "ocr_value": case_data["passenger"].date_of_birth.strftime("%d/%m/%Y"), "mrz_value": case_data["passenger"].date_of_birth.strftime("%y%m%d"), "match": case_data["case_id"] != "CASE-240115-002"},
                            {"field_name": "date_of_expiry", "ocr_value": "14/08/2030", "mrz_value": "300814", "match": True},
                            {"field_name": "nationality", "ocr_value": "IND", "mrz_value": "IND", "match": True},
                        ],
                        consistency_percentage=100.0 if case_data["case_id"] != "CASE-240115-002" else 75.0,
                        processing_time_ms=800,
                        status=ProcessingStatus.COMPLETED,
                    )
                    db.add(mrz_result)

                # Validation results
                if case_data["case_id"] == "CASE-240115-002" and doc.document_type == DocumentType.PASSPORT:
                    field_validations = [
                        {"field_name": "full_name", "value": case_data["passenger"].full_name, "valid": True, "message": None},
                        {"field_name": "passport_number", "value": case_data["passenger"].passport_number, "valid": True, "message": "Valid format"},
                        {"field_name": "nationality", "value": "IND", "valid": True, "message": None},
                        {"field_name": "date_of_birth", "value": case_data["passenger"].date_of_birth.strftime("%d/%m/%Y"), "valid": True, "message": None},
                        {"field_name": "gender", "value": case_data["passenger"].gender, "valid": True, "message": None},
                        {"field_name": "date_of_expiry", "value": "14/08/2022", "valid": False, "message": "Passport expired"},
                    ]
                    overall_valid = False
                    errors = ["Passport has expired"]
                elif case_data["case_id"] == "CASE-240115-004" and doc.document_type == DocumentType.VISA:
                    field_validations = [
                        {"field_name": "visa_number", "value": f"VISA-2024-{doc.id:06d}", "valid": True, "message": None},
                        {"field_name": "full_name", "value": case_data["passenger"].full_name, "valid": True, "message": None},
                        {"field_name": "passport_number", "value": "Z9999999", "valid": False, "message": "Passport number mismatch with passport document"},
                        {"field_name": "visa_type", "value": "TOURIST", "valid": True, "message": None},
                        {"field_name": "valid_from", "value": "01/01/2024", "valid": True, "message": None},
                        {"field_name": "valid_until", "value": "31/12/2024", "valid": True, "message": None},
                    ]
                    overall_valid = False
                    errors = ["Passport number mismatch with passport document"]
                else:
                    field_validations = [{"field_name": f["field_name"], "value": f["value"], "valid": True, "message": None} for f in ocr_fields]
                    overall_valid = True
                    errors = None

                val_result = ValidationResult(
                    case_id=case.id,
                    document_id=doc.id,
                    field_validations=field_validations,
                    overall_valid=overall_valid,
                    warnings=None,
                    errors=errors,
                    reference_db_check={"found": True, "status": "valid", "blacklisted": case_data["case_id"] == "CASE-240115-003"},
                    processing_time_ms=500,
                    status=ProcessingStatus.COMPLETED if overall_valid else ProcessingStatus.WARNING,
                )
                db.add(val_result)

                # Tamper results
                if case_data["case_id"] == "CASE-240115-003" and doc.document_type == DocumentType.PASSPORT:
                    tamper_prob = 0.91
                    regions = [
                        {"region": "photograph", "probability": 0.91, "description": "Possible photo replacement detected"},
                        {"region": "text", "probability": 0.67, "description": "Possible text manipulation in MRZ region"},
                    ]
                elif case_data["case_id"] == "CASE-240115-004" and doc.document_type == DocumentType.VISA:
                    tamper_prob = 0.35
                    regions = [
                        {"region": "text", "probability": 0.35, "description": "Minor compression anomalies in visa number field"},
                    ]
                else:
                    tamper_prob = 0.05
                    regions = []

                tamper_result = TamperResult(
                    case_id=case.id,
                    document_id=doc.id,
                    tampering_probability=tamper_prob,
                    suspected_regions=regions,
                    heatmap_path=f"/storage/heatmaps/{doc.original_filename.replace('.', '_heatmap.')}",
                    noise_residual_path=f"/storage/noise_residuals/{doc.original_filename.replace('.', '_noise.')}",
                    noise_analysis_reliable=True,
                    forensics_findings={"ela_analysis": "completed", "compression_inconsistencies": len(regions) > 0},
                    rgb_image_path=doc.file_path,
                    processing_time_ms=2500,
                    status=ProcessingStatus.COMPLETED,
                )
                db.add(tamper_result)

                # Face results
                if case_data["case_id"] == "CASE-240115-005":
                    similarity = 0.582
                    match_status = "POSSIBLE_MISMATCH"
                else:
                    similarity = 0.964
                    match_status = "MATCH"

                face_result = FaceResult(
                    case_id=case.id,
                    document_id=doc.id,
                    document_face_path=f"/storage/faces/{case.id}/doc_{doc.id}_doc.jpg",
                    live_face_path=f"/storage/faces/{case.id}/doc_{doc.id}_live.jpg",
                    document_face_detected=True,
                    live_face_detected=True,
                    document_embedding=[0.1] * 512,
                    live_embedding=[0.1] * 512,
                    similarity_score=similarity,
                    match_status=match_status,
                    processing_time_ms=1800,
                    status=ProcessingStatus.COMPLETED,
                )
                db.add(face_result)

            # Cross-document results
            if len(documents) > 1:
                for field in ["full_name", "date_of_birth", "passport_number", "nationality"]:
                    values = {}
                    consistent = True
                    for doc in documents:
                        # Get OCR field value
                        ocr_result = await db.execute(
                            select(OCRResult).where(OCRResult.document_id == doc.id)
                        )
                        ocr = ocr_result.scalar_one_or_none()
                        if ocr:
                            for f in ocr.extracted_fields:
                                if f["field_name"] == field:
                                    values[f"doc_{doc.id}"] = f["value"]
                                    break
                    
                    # Check consistency
                    if len(set(values.values())) > 1:
                        consistent = False
                    
                    # Special case for CASE-004 passport number mismatch
                    if case_data["case_id"] == "CASE-240115-004" and field == "passport_number":
                        consistent = False
                    
                    cross_result = CrossDocumentResult(
                        case_id=case.id,
                        field_name=field,
                        document_values=values,
                        consistent=consistent,
                        inconsistency_details=f"Values differ: {values}" if not consistent else None,
                    )
                    db.add(cross_result)

            # Risk assessment
            factors = [
                {"factor": "Document Validation", "weight": 0.15, "contribution": 0.0 if case_data["risk_level"] == RiskLevel.LOW else 0.1, "description": "All documents passed validation checks" if case_data["risk_level"] == RiskLevel.LOW else "Some documents failed validation"},
                {"factor": "MRZ Checksum", "weight": 0.10, "contribution": 0.0 if case_data["case_id"] != "CASE-240115-002" else 0.1, "description": "MRZ checksums valid" if case_data["case_id"] != "CASE-240115-002" else "MRZ checksum failures detected"},
                {"factor": "OCR-MRZ Consistency", "weight": 0.15, "contribution": 0.0 if case_data["case_id"] != "CASE-240115-002" else 0.12, "description": "OCR and MRZ fields consistent" if case_data["case_id"] != "CASE-240115-002" else "OCR-MRZ field mismatches detected"},
                {"factor": "Cross-Document Consistency", "weight": 0.15, "contribution": 0.0 if case_data["case_id"] != "CASE-240115-004" else 0.12, "description": "Information consistent across documents" if case_data["case_id"] != "CASE-240115-004" else "Cross-document inconsistencies found"},
                {"factor": "Tampering Detection", "weight": 0.25, "contribution": 0.0 if case_data["case_id"] != "CASE-240115-003" else 0.23, "description": "No significant tampering detected" if case_data["case_id"] != "CASE-240115-003" else "Possible document manipulation detected"},
                {"factor": "Face Verification", "weight": 0.15, "contribution": 0.0 if case_data["case_id"] != "CASE-240115-005" else 0.06, "description": "Face match successful" if case_data["case_id"] != "CASE-240115-005" else "Face similarity below threshold"},
                {"factor": "Document Expiry", "weight": 0.05, "contribution": 0.0 if case_data["case_id"] != "CASE-240115-002" else 0.05, "description": "All documents valid" if case_data["case_id"] != "CASE-240115-002" else "Expired documents detected"},
            ]

            risk_assessment = RiskAssessment(
                case_id=case.id,
                risk_level=case_data["risk_level"],
                risk_score=case_data["risk_score"],
                contributing_factors=factors,
                factor_weights={"document_validation": 0.15, "mrz_checksum": 0.10, "ocr_mrz_consistency": 0.15, "cross_document_consistency": 0.15, "tampering_probability": 0.25, "face_similarity": 0.15, "expired_document": 0.05},
                threshold_config={"low_max": 0.3, "medium_max": 0.6},
            )
            db.add(risk_assessment)

            # Audit log
            audit = AuditLog(
                case_id=case.id,
                officer_id=officer.id,
                action="VERIFICATION_COMPLETED",
                details={"risk_level": case_data["risk_level"], "risk_score": case_data["risk_score"]}
            )
            db.add(audit)

        await db.commit()
        print("Demo data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())