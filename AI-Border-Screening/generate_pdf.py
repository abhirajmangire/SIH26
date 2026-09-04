from fpdf import FPDF
import os

def safe(text):
    """Replace non-latin1 characters with ASCII equivalents"""
    replacements = {
        '\u2022': '-',      # bullet
        '\u250c': '+',      # box drawing
        '\u2500': '-',
        '\u2510': '+',
        '\u2502': '|',
        '\u2514': '+',
        '\u2518': '+',
        '\u251c': '+',
        '\u2524': '+',
        '\u2534': '+',
        '\u253c': '+',
        '\u2580': '#',
        '\u2584': '#',
        '\u2588': '#',
        '\u2591': ':',
        '\u2592': ':',
        '\u2593': ':',
        '\u2713': 'OK',     # checkmark
        '\u2717': 'X',      # cross
        '\u2192': '->',     # arrow
        '\u2190': '<-',
        '\u2264': '<=',
        '\u2265': '>=',
        '\u00b1': '+/-',
        '\u2013': '-',      # en dash
        '\u2014': '--',     # em dash
        '\u2018': "'",      # smart quotes
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2026': '...',    # ellipsis
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

class ProjectPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, safe('AI-Based Document Screening & Tamper Detection System - Problem Statement ID: 26188'), align='C')
            self.ln(8)
            self.set_draw_color(0, 103, 224)
            self.set_line_width(0.3)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
    
    def chapter_title(self, num, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(11, 31, 58)
        self.cell(0, 10, safe(f'{num}. {title}'), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 168, 232)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
    
    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(23, 105, 224)
        self.cell(0, 8, safe(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
    
    def sub_section_title(self, title):
        self.set_font('Helvetica', 'BI', 10)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, safe(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
    
    def body_text(self, text):
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, safe(text))
        self.ln(2)
    
    def bullet_point(self, text, indent=15):
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(4, 5, '-')
        self.multi_cell(0, 5, safe(text))
        self.ln(1)
    
    def bullet_bold_value(self, label, value, indent=15):
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(4, 5, '-')
        self.set_font('Helvetica', 'B', 9.5)
        self.cell(self.get_string_width(safe(label)) + 1, 5, safe(label))
        self.set_font('Helvetica', '', 9.5)
        self.multi_cell(0, 5, safe(value))
        self.ln(1)
    
    def code_block(self, text):
        self.set_font('Courier', '', 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(30, 30, 30)
        x = self.get_x()
        self.set_x(x + 10)
        self.multi_cell(180, 4.5, safe(text), fill=True)
        self.ln(3)
    
    def table_header(self, cols, widths):
        self.set_font('Helvetica', 'B', 8.5)
        self.set_fill_color(11, 31, 58)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, safe(col), border=1, fill=True, align='C')
        self.ln()
    
    def table_row(self, cols, widths, fill=False):
        self.set_font('Helvetica', '', 8)
        self.set_text_color(40, 40, 40)
        if fill:
            self.set_fill_color(240, 245, 250)
        else:
            self.set_fill_color(255, 255, 255)
        max_h = 7
        for i, col in enumerate(cols):
            self.cell(widths[i], max_h, safe(str(col)[:30]), border=1, fill=True, align='L')
        self.ln()


pdf = ProjectPDF()
pdf.alias_nb_pages()
pdf.add_page()

# ============ COVER PAGE ============
pdf.ln(30)
pdf.set_font('Helvetica', 'B', 28)
pdf.set_text_color(11, 31, 58)
pdf.cell(0, 15, 'AI-Based Document Screening', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 15, '& Tamper Detection System', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)

pdf.set_draw_color(0, 168, 232)
pdf.set_line_width(1)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(10)

pdf.set_font('Helvetica', '', 14)
pdf.set_text_color(23, 105, 224)
pdf.cell(0, 10, 'Problem Statement ID: 26188', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

pdf.set_font('Helvetica', '', 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, 'Officer-Facing Border/Airport Security Screening Prototype', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'SIH Demonstration Project', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(20)

pdf.set_font('Helvetica', 'I', 10)
pdf.set_text_color(128, 128, 128)
pdf.cell(0, 8, 'Technical Architecture & Implementation Guide', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, f'Generated: {os.popen("date /t").read().strip()}', align='C', new_x="LMARGIN", new_y="NEXT")

# ============ TABLE OF CONTENTS ============
pdf.add_page()
pdf.set_font('Helvetica', 'B', 16)
pdf.set_text_color(11, 31, 58)
pdf.cell(0, 12, 'Table of Contents', new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

toc = [
    ("1", "Project Overview"),
    ("2", "Technology Stack & Rationale"),
    ("3", "System Architecture"),
    ("4", "Database Design (PostgreSQL)"),
    ("5", "Backend Modules Detailed"),
    ("  5.1", "Authentication Module"),
    ("  5.2", "Case Management"),
    ("  5.3", "OCR Module (PaddleOCR)"),
    ("  5.4", "MRZ Module (Passport Only)"),
    ("  5.5", "Validation Module"),
    ("  5.6", "Tampering Detection (Core Innovation)"),
    ("  5.7", "Face Verification Module"),
    ("  5.8", "Cross-Document Verification"),
    ("  5.9", "Risk Assessment Engine"),
    ("6", "Frontend Pages Detailed"),
    ("  6.1", "Page 1: Officer Login"),
    ("  6.2", "Page 2: Officer Dashboard"),
    ("  6.3", "Page 3: Verification Details"),
    ("7", "End-to-End Data Flow"),
    ("8", "Security & Privacy"),
    ("9", "Deployment Architecture"),
    ("10", "Development Workflow"),
    ("11", "Why This Architecture"),
    ("12", "File Count Summary"),
    ("13", "Running Without Docker"),
]

for num, title in toc:
    pdf.set_font('Helvetica', 'B' if not num.startswith(' ') else '', 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(15, 6, safe(num))
    pdf.cell(0, 6, safe(title), new_x="LMARGIN", new_y="NEXT")

# ============ 1. PROJECT OVERVIEW ============
pdf.add_page()
pdf.chapter_title("1", "Project Overview")

pdf.body_text(
    "This project is an officer-facing AI-assisted border/airport identity and document screening prototype. "
    "The system is NOT a passenger self-service system. A trained border/security officer operates the system "
    "to upload/scan passenger documents and face captures, while the system performs AI-assisted verification "
    "and presents evidence-based results to the officer. The AI provides screening/risk signals; the officer "
    "remains the final decision-maker."
)

pdf.section_title("Key Constraints")
pdf.bullet_point("Prototype for SIH demonstration - not a production immigration system")
pdf.bullet_point("No connection to real government immigration/blacklist databases")
pdf.bullet_point("Uses synthetic/demo/reference data only")
pdf.bullet_point("Modular architecture for future real database integration")
pdf.bullet_point("Three main pages: Login, Dashboard, Verification Details")

pdf.section_title("Core Workflow")
pdf.body_text(
    "Officer Login -> Scan/Upload Passenger Documents -> Documents Enter Processing Queue -> "
    "OCR Extraction -> Passport MRZ + Checksum -> OCR<->MRZ Cross-Field Verification -> "
    "Document Validation -> Cross-Document Verification -> AI Tampering Detection "
    "(RGB + Image Forensics + Noise Residual + Tamper Heatmap) -> Face Verification -> "
    "Explainable Risk Assessment -> Officer Dashboard -> Final Verification Summary -> Completion"
)

# ============ 2. TECHNOLOGY STACK ============
pdf.add_page()
pdf.chapter_title("2", "Technology Stack & Rationale")

pdf.section_title("Backend Stack")
backend_stack = [
    ("Python 3.10+", "Best AI/ML ecosystem (PyTorch, OpenCV, PaddleOCR), async support, type hints"),
    ("FastAPI", "Async native, auto OpenAPI docs, Pydantic validation, high performance, DI"),
    ("SQLAlchemy 2.0 (async)", "Mature ORM, async PostgreSQL support, declarative models"),
    ("PostgreSQL 15", "Relational integrity, JSONB for ML results, ACID, production-ready"),
    ("Alembic", "Version-controlled schema migrations, auto-generation"),
    ("JWT + bcrypt", "Stateless auth, scalable, industry standard"),
    ("Celery + Redis", "Background ML processing without blocking API"),
]
for tech, reason in backend_stack:
    pdf.bullet_bold_value(f"{tech}: ", reason)

pdf.section_title("Frontend Stack")
frontend_stack = [
    ("TypeScript", "Type safety across API contracts, compile-time error detection"),
    ("React 18", "Component-based, concurrent features, large ecosystem"),
    ("Vite", "Instant HMR, fast builds, ES modules native"),
    ("Tailwind CSS", "Utility-first, consistent design system, small bundle"),
    ("React Router v6", "Declarative routing, nested routes, lazy loading"),
    ("Axios", "Interceptors, request/response transforms, TS support"),
    ("Lucide React", "Clean, consistent, tree-shakeable icons"),
]
for tech, reason in frontend_stack:
    pdf.bullet_bold_value(f"{tech}: ", reason)

pdf.section_title("AI/ML Pipeline")
ml_stack = [
    ("PaddleOCR", "Multi-language OCR, high accuracy, structured document support"),
    ("Tesseract + Custom Parser", "ICAO TD3 MRZ extraction, checksum validation"),
    ("InsightFace (buffalo_l)", "SOTA face recognition, 512-d embeddings, ONNX runtime"),
    ("OpenCV + NumPy + scikit-image", "ELA, noise residual, texture analysis, heatmap generation"),
]
for tech, reason in ml_stack:
    pdf.bullet_bold_value(f"{tech}: ", reason)

# ============ 3. SYSTEM ARCHITECTURE ============
pdf.add_page()
pdf.chapter_title("3", "System Architecture")

pdf.body_text(
    "The system follows a clean client-server architecture with a React frontend communicating via REST APIs "
    "to a FastAPI backend. The backend orchestrates an asynchronous ML pipeline using Celery/Redis for "
    "long-running document processing tasks."
)

pdf.section_title("Architecture Diagram")
pdf.code_block(safe("""
+---------------------------------------------------------------+
|                      FRONTEND (React + Vite)                  |
|  +---------+ +-----------+ +-------------+ +--------------+  |
|  | Login   | | Dashboard | | Verification| | Components   |  |
|  | Page 1  | | Page 2    | | Page 3      | | Shared       |  |
|  +---------+ +-----------+ +-------------+ +--------------+  |
|                      | Axios API Client (JWT)               |
+----------------------|--------------------------------------+
                       | HTTPS/REST
                       v
+---------------------------------------------------------------+
|                       BACKEND (FastAPI)                       |
|  +------+ +------+ +------+ +------+ +------+ +----------+  |
|  | Auth | |Cases | | Docs | | OCR  | | MRZ  | | Valid    |  |
|  +------+ +------+ +------+ +------+ +------+ +----------+  |
|  +------+ +------+ +------+ +------+ +------+ +----------+  |
|  |Tamper| | Face | |Verify| |Dashbd| | Risk | |Services  |  |
|  +------+ +------+ +------+ +------+ +------+ +----------+  |
|  +------------- SERVICE LAYER (Business Logic) -------------+
|       OCR -> MRZ -> Validation -> Tamper -> Face -> Risk    |
+---------------------------------------------------------------+
                |                    |                  |
                v                    v                  v
         +----------+         +----------+        +----------+
         |PostgreSQL|         |  Redis   |        |  File    |
         |(Relational)       |(Cache/Q) |        | Storage  |
         +----------+         +----------+        +----------+
"""))

# ============ 4. DATABASE DESIGN ============
pdf.add_page()
pdf.chapter_title("4", "Database Design (PostgreSQL)")

pdf.section_title("Core Tables (12 Tables)")
pdf.body_text("The database uses a fully normalized relational schema with JSONB columns for flexible ML results storage.")

tables = [
    ("officers", "Authentication & audit trail", "id, officer_id, email, hashed_password, full_name, badge_number, department, is_active"),
    ("passengers", "Passenger identity (synthetic)", "id, passenger_id, full_name, date_of_birth, nationality, gender, passport_number"),
    ("verification_cases", "Main case record per screening", "id, case_id, officer_id, passenger_id, overall_status, overall_risk_level, risk_score, risk_reasons"),
    ("documents", "Uploaded files per case", "id, case_id, document_type, file_path, upload_status, processing_progress, current_step"),
    ("ocr_results", "Extracted text with confidence", "id, case_id, document_id, extracted_fields (JSON), confidence_scores, raw_text"),
    ("mrz_results", "Passport MRZ extraction & checksum", "id, case_id, document_id, mrz_detected, mrz_raw, decoded_fields, checksum_valid, ocr_mrz_comparison"),
    ("validation_results", "Field validation + reference DB", "id, case_id, document_id, field_validations, overall_valid, warnings, errors, reference_db_check"),
    ("tamper_results", "Forensic analysis per document", "id, case_id, document_id, tampering_probability, suspected_regions, heatmap_path, noise_residual_path, forensics_findings"),
    ("face_results", "Face comparison results", "id, case_id, document_id, document_face_path, live_face_path, similarity_score, match_status"),
    ("cross_document_results", "Cross-document consistency", "id, case_id, field_name, document_values, consistent, inconsistency_details"),
    ("risk_assessments", "Final explainable risk score", "id, case_id, risk_level, risk_score, contributing_factors, factor_weights, threshold_config"),
    ("audit_logs", "Immutable action trail", "id, case_id, officer_id, action, details, timestamp"),
]

widths = [30, 55, 105]
pdf.table_header(["Table", "Purpose", "Key Columns"], widths)
for i, (table, purpose, cols) in enumerate(tables):
    pdf.table_row([table, purpose, cols], widths, fill=i%2==0)

pdf.ln(5)
pdf.section_title("Key Design Decisions")
decisions = [
    ("Separate tables per module", "Independent querying, clear ownership, scalable"),
    ("JSONB for ML results", "Flexible schema for varying OCR/ML outputs, queryable"),
    ("File paths not BLOBs", "Database performance, backup size, streaming support"),
    ("Enum types in DB", "Data integrity, self-documenting, indexable"),
    ("Cascade deletes", "Cleanup when case deleted, referential integrity"),
    ("Indexes on case_id, document_id", "Fast lookups for dashboard and verification pages"),
]
for decision, reason in decisions:
    pdf.bullet_bold_value(f"{decision}: ", reason)

# ============ 5. BACKEND MODULES ============
pdf.add_page()
pdf.chapter_title("5", "Backend Modules Detailed")

# 5.1 Auth
pdf.section_title("5.1 Authentication Module")
pdf.body_text("Location: app/services/auth.py, app/api/v1/auth.py")
pdf.body_text("Features: JWT access tokens (HS256, 8-hour expiry), bcrypt password hashing (cost 12), demo officer auto-creation, protected routes via Depends(get_current_officer).")

pdf.sub_section_title("Endpoints")
auth_endpoints = [
    ("POST /api/v1/auth/login", "Returns access_token"),
    ("POST /api/v1/auth/register", "Create officer (admin use)"),
    ("GET /api/v1/auth/me", "Current officer profile"),
    ("POST /api/v1/auth/init-demo", "Seed demo credentials"),
]
for ep, desc in auth_endpoints:
    pdf.bullet_bold_value(f"{ep}: ", desc)

# 5.2 Cases
pdf.section_title("5.2 Case Management")
pdf.body_text("Location: app/api/v1/cases.py")
pdf.body_text("Core Flow: Create Case -> Upload Documents -> Start Processing -> Poll Queue -> View Results")
pdf.sub_section_title("Key Endpoints")
case_endpoints = [
    ("POST /api/v1/cases", "Create new verification case"),
    ("GET /api/v1/cases", "Paginated case list"),
    ("GET /api/v1/cases/{case_id}", "Case details"),
    ("POST /api/v1/cases/{case_id}/documents", "Upload document (multipart)"),
    ("GET /api/v1/cases/{case_id}/documents", "List case documents"),
    ("GET /api/v1/cases/{case_id}/queue", "Processing queue status"),
    ("POST /api/v1/cases/{case_id}/process", "Trigger async pipeline"),
    ("GET /api/v1/cases/history", "Filtered passenger history"),
    ("GET /api/v1/cases/passengers/search", "Passenger search"),
]
for ep, desc in case_endpoints:
    pdf.bullet_bold_value(f"{ep}: ", desc)

# 5.3 OCR
pdf.section_title("5.3 OCR Module (PaddleOCR)")
pdf.body_text("Location: app/services/ocr/ocr_service.py")
pdf.body_text("Pipeline: Image -> PaddleOCR -> Text Detection -> Text Recognition -> Field Classification -> Confidence Scoring")
pdf.sub_section_title("Output Structure")
pdf.code_block(safe("""{
  "extracted_fields": [
    {"field_name": "passport_number", "value": "Z1234567", "confidence": 0.98},
    {"field_name": "full_name", "value": "RAJESH KUMAR SHARMA", "confidence": 0.95}
  ],
  "confidence_scores": {"passport_number": 0.98, "full_name": 0.95},
  "raw_text": "PASSPORT NUMBER: Z1234567\nFULL NAME: RAJESH KUMAR SHARMA..."
}"""))
pdf.body_text("Field Classification: Keyword-based mapping for passport_number, full_name, date_of_birth, nationality, gender, date_of_expiry, visa_number, valid_from, valid_until, id_number, permit_type, etc.")

# 5.4 MRZ
pdf.add_page()
pdf.section_title("5.4 MRZ Module (Passport Only)")
pdf.body_text("Location: app/services/mrz/mrz_service.py")
pdf.body_text("Passport-Only Pipeline: Passport Image -> Bottom Region Crop -> Tesseract OCR (whitelist) -> Parse TD3 Format -> Checksum Validation -> OCR<->MRZ Cross-Field Comparison")

pdf.sub_section_title("MRZ TD3 Format (2 lines x 44 chars)")
pdf.code_block("Line 1: P<CTRY<<SURNAME<<GIVEN<NAMES<<<<<<<<<<<<<<<<<<<<\nLine 2: PASSPORT#<C<NAT<DOB<SEX<EXP<PERS<<<<<<<<<<<<<<<C")

pdf.sub_section_title("Checksum Algorithm (ICAO 9303)")
pdf.body_text("Weight sequence: 7, 3, 1 repeating. Characters: 0-9=0-9, A-Z=10-35, <=0. Validates: passport_number, date_of_birth, date_of_expiry, composite.")

pdf.sub_section_title("Cross-Field Comparison Table")
mrz_cols = ["Field", "OCR Value", "MRZ Value", "Normalized", "Match"]
mrz_data = [
    ["passport_number", "Z1234567", "Z1234567", "Z1234567", "YES"],
    ["date_of_birth", "15/08/1985", "850815", "850815", "YES"],
    ["nationality", "IND", "IND", "IND", "YES"],
    ["date_of_expiry", "14/08/2030", "300814", "300814", "YES"],
]
widths = [35, 30, 30, 30, 20]
pdf.table_header(mrz_cols, widths)
for i, row in enumerate(mrz_data):
    pdf.table_row(row, widths, fill=i%2==0)

# 5.5 Validation
pdf.section_title("5.5 Validation Module")
pdf.body_text("Location: app/services/validation/validation_service.py")

pdf.sub_section_title("Per-Document Rules")
val_cols = ["Document", "Required Fields", "Format Checks", "Expiry Check", "Reference DB"]
val_data = [
    ["Passport", "name, number, nationality, DOB, gender, expiry", "Passport # regex", "Not expired", "Mock passport DB"],
    ["Visa", "visa#, name, passport#, type, valid_from, valid_until", "Visa # format", "Not expired", "Mock visa DB"],
    ["National ID", "name, ID#, DOB, nationality", "ID# format", "N/A", "Mock ID DB"],
    ["Permit", "name, passport#, type, valid_from, valid_until", "Permit # format", "Not expired", "Mock permit DB"],
]
widths = [22, 42, 30, 25, 35]
pdf.table_header(val_cols, widths)
for i, row in enumerate(val_data):
    pdf.table_row(row, widths, fill=i%2==0)

pdf.ln(3)
pdf.sub_section_title("Reference Database (Mock/Synthetic)")
pdf.code_block(safe("""{
  "passports": {
    "Z1234567": {"status": "valid", "blacklisted": false},
    "Z9999999": {"status": "expired", "blacklisted": false},
    "Z8888888": {"status": "blacklisted", "blacklisted": true}
  },
  "visas": {...}, "national_ids": {...}, "permits": {...}
}"""))

# 5.6 Tampering
pdf.add_page()
pdf.section_title("5.6 Tampering Detection Module (CORE INNOVATION)")
pdf.body_text("Location: app/services/tamper/tamper_service.py")
pdf.body_text("Multi-Forensic Pipeline operating on EVERY uploaded document (not just passports):")

pdf.sub_section_title("Pipeline Stages")
pdf.code_block(safe("""
+---------------------------------------------------------------+
|                   TAMPERING DETECTION PIPELINE                 |
+---------------------------------------------------------------+
|                                                                |
|  Input Image                                                   |
|       |                                                        |
|       v                                                        |
|  +-------------+ +----------------+ +------------------------+ |
|  | RGB ANALYSIS| | NOISE RESIDUAL | | IMAGE FORENSICS      | |
|  |             | |                | |                      | |
|  | - Dimensions| | - NLM Denoise  | | - ELA (Error Level   | |
|  | - Channel   | | - Residual =   | |   Analysis)          | |
|  |   Stats     | |   Orig - Denoise| | - Block DCT         | |
|  | - Mean/Std  | | - Reliability  | |   Variance          | |
|  +-------------+ +----------------+ | - Texture (GLCM)    | |
|       |                |            | - Photo Region      | |
|       +----------------+------------+   Detection          | |
|                        v              +--------------------+ |
|              +-------------------------+                    |
|              |  HEATMAP GENERATION     |                    |
|              |                         |                    |
|              | - Aggregate signals     |                    |
|              | - Gaussian blur         |                    |
|              | - Color map (JET)       |                    |
|              | - Overlay on RGB        |                    |
|              +-------------------------+                    |
|                        |                                     |
|                        v                                     |
|         Output: probability, regions, heatmap, noise map    |
+---------------------------------------------------------------+
"""))

pdf.sub_section_title("Output Example")
pdf.code_block(safe("""{
  "tampering_probability": 0.91,
  "suspected_regions": [
    {"region": "photograph", "probability": 0.91, "description": "Possible photo replacement"},
    {"region": "text", "probability": 0.67, "description": "MRZ text manipulation"}
  ],
  "heatmap_path": "/storage/heatmaps/passport_001_heatmap.jpg",
  "noise_residual_path": "/storage/noise_residuals/passport_001_noise.jpg",
  "noise_analysis_reliable": true,
  "forensics_findings": {
    "ela_analysis": "completed",
    "compression_inconsistencies": [...],
    "texture_analysis": {"contrast": 12.4, "homogeneity": 0.31}
  }
}"""))

# 5.7 Face
pdf.section_title("5.7 Face Verification Module")
pdf.body_text("Location: app/services/face/face_service.py")
pdf.body_text("Pipeline: Document Image -> Face Detection -> Alignment -> Embedding (512-d) | Live Capture -> Same -> Cosine Similarity -> Match Status")

pdf.sub_section_title("Thresholds (Prototype)")
pdf.bullet_bold_value(">= 0.75: ", "MATCH")
pdf.bullet_bold_value("0.50 - 0.75: ", "POSSIBLE_MISMATCH")
pdf.bullet_bold_value("< 0.50: ", "MISMATCH")

pdf.body_text("Important: Never makes legal determination - only provides evidence for officer review.")

# 5.8 Cross-Document
pdf.section_title("5.8 Cross-Document Verification")
pdf.body_text("Location: app/api/v1/cases.py (process_cross_document_verification)")
pdf.body_text("Compared Fields: full_name, date_of_birth, passport_number, nationality, gender")
pdf.body_text("Logic: For each field, collect values from all document OCR results. If all identical -> CONSISTENT. Else -> MISMATCH with details.")

pdf.sub_section_title("Example Output")
pdf.code_block(safe("""DOB:       Passport=15/08/1985, Visa=15/08/1985, National_ID=15/08/1985 -> CONSISTENT
Passport#: Passport=Z1234567, Visa=Z9999999 -> MISMATCH"""))

# 5.9 Risk
pdf.section_title("5.9 Risk Assessment Engine")
pdf.body_text("Location: app/services/risk/risk_engine.py")
pdf.body_text("Weighted Factor Model:")

risk_cols = ["Factor", "Weight", "Description"]
risk_data = [
    ["Document Validation", "15%", "All fields valid, reference DB clean"],
    ["MRZ Checksum", "10%", "Passport MRZ checksums pass"],
    ["OCR<->MRZ Consistency", "15%", "Field-level match percentage"],
    ["Cross-Document Consistency", "15%", "Identity fields match across docs"],
    ["Tampering Detection", "25%", "Max tampering probability across docs"],
    ["Face Verification", "15%", "1 - similarity_score"],
    ["Document Expiry", "5%", "Any expired document"],
]
widths = [50, 20, 120]
pdf.table_header(risk_cols, widths)
for i, row in enumerate(risk_data):
    pdf.table_row(row, widths, fill=i%2==0)

pdf.ln(3)
pdf.sub_section_title("Risk Levels")
pdf.bullet_bold_value("Score <= 0.30: ", "LOW (Green)")
pdf.bullet_bold_value("0.30 < Score <= 0.60: ", "MEDIUM (Amber)")
pdf.bullet_bold_value("Score > 0.60: ", "HIGH (Red)")

pdf.body_text("Explainability: Every factor shows contribution, weight, and human-readable description.")

# ============ 6. FRONTEND PAGES ============
pdf.add_page()
pdf.chapter_title("6", "Frontend Pages Detailed")

pdf.section_title("6.1 Page 1: Officer Login (LoginPage.tsx)")
pdf.body_text("Clean security-themed UI with deep navy background, centered frosted card. Features:")
pdf.bullet_point("Officer ID + Password with show/hide toggle")
pdf.bullet_point("JWT token storage in localStorage with auto-redirect on valid session")
pdf.bullet_point("Demo credentials displayed for testing (OFFICER001 / SecurePass123!)")
pdf.bullet_point("Error handling with inline messages")
pdf.bullet_point("Visual: Navy background with subtle grid pattern, royal blue primary button")

pdf.section_title("6.2 Page 2: Officer Dashboard (DashboardPage.tsx)")
pdf.body_text("Three main sections:")

pdf.sub_section_title("A. Overview Dashboard")
pdf.code_block(safe("""+---------------------------------------------------------------+
|  STAT CARDS (6)                    |  RISK DISTRIBUTION        |
|  +-----+ +-----+ +-----+           |  HIGH   ######## 12%      |
|  |Pass | |Docs | |Valid|           |  MED    ######   28%      |
|  |engers| |Verif| |Docs |           |  LOW    ########## 60%    |
|  +-----+ +-----+ +-----+           |                           |
|  +-----+ +-----+ +-----+           |  RECENT ACTIVITY          |
|  |Susp | |High | |Proc |           |  CASE-001  GREEN  10:30   |
|  |Docs | |Risk | |essing|          |  CASE-002  RED    09:15   |
|  +-----+ +-----+ +-----+           |  ...                      |
+---------------------------------------------------------------+"""))

pdf.sub_section_title("B. Document Upload / Scan Area")
pdf.bullet_point("Drag-and-drop zone with visual feedback")
pdf.bullet_point("Multiple file selection with per-file document type dropdown")
pdf.bullet_point("File preview with remove button")
pdf.bullet_point("Face capture panel (webcam + upload fallback)")

pdf.sub_section_title("C. Processing Queue (Live Updates)")
pdf.code_block(safe("""Document          Status        Progress    Current Step
-----------------------------------------------------------------
Passport        CHECK COMPLETED  ########## 100%  Completed
Visa            WARNING          ########     78%   Tampering Detection...
National ID     WAITING          0%    0%   Waiting"""))

pdf.sub_section_title("D. Passenger History")
pdf.bullet_point("Searchable/filterable table with filters: Passenger ID, Date Range, Risk Level, Status")
pdf.bullet_point("Click row -> navigate to Verification Details")

# 6.3 Verification Page
pdf.section_title("6.3 Page 3: Verification Details (VerificationPage.tsx)")
pdf.body_text("Most complex page - complete evidence view with expandable sections for each module:")

pdf.sub_section_title("Layout Structure")
pdf.code_block(safe("""+--------------------------------------------------------------+
| CASE-240115-001  2024-01-15 10:30          [HIGH RISK] [COMPLETE]|
+--------------------------------------------------------------+
| VERIFICATION TIMELINE (visual progress with icons)            |
+--------------------------------------------------------------+
| DOCUMENTS | MRZ DETAILS | VALIDATION | CROSS-DOC | TAMPER | FACE|
| [Expandable sections with tables, images, heatmaps]           |
+--------------------------------------------------------------+
| FINAL RISK ASSESSMENT (Prominent color-coded card)            |
|   Contributing factors with weights & descriptions            |
+--------------------------------------------------------------+
| FINAL SUMMARY (Condensed decision-ready view)                 |
| DOCUMENT STATUS | MRZ | CROSS-DOC | TAMPERING | FACE         |
| OVERALL RISK: HIGH  [COMPLETE VERIFICATION]                   |
+--------------------------------------------------------------+"""))

pdf.sub_section_title("Key UI Components")
components = [
    "Timeline - Visual progress with icons (CHECK/LOADING/WAITING/WARNING/FAIL)",
    "MRZ Table - Field | OCR Value | MRZ Value | Result (CHECK/FAIL)",
    "Tamper Panel - 3-column: RGB Image | Heatmap | Noise Residual",
    "Face Comparison - Side-by-side with circular similarity % indicator",
    "Risk Panel - Color-coded, factor breakdown with weights",
    "Final Summary - Condensed decision-ready view for officer",
]
for c in components:
    pdf.bullet_point(c)

# ============ 7. DATA FLOW ============
pdf.add_page()
pdf.chapter_title("7", "End-to-End Data Flow")

flow_steps = [
    ("1. OFFICER LOGIN", "POST /auth/login -> JWT -> stored in localStorage"),
    ("2. CREATE CASE", "POST /cases {case_id, passenger_id} -> VerificationCase record"),
    ("3. UPLOAD DOCUMENTS", "POST /cases/{id}/documents (multipart) -> Document records + files saved"),
    ("4. START PROCESSING", "POST /cases/{id}/process -> Background task triggered"),
    ("5. BACKGROUND PIPELINE", "Async processing per document (see below)"),
    ("6. POLLING", "GET /cases/{id}/queue every 2s -> Updates UI progress bars"),
    ("7. VIEW RESULTS", "GET /verification/{id}/detail -> Complete VerificationDetail response"),
    ("8. COMPLETE", "POST /verification/{id}/complete -> Audit log entry"),
]
for step, desc in flow_steps:
    pdf.bullet_bold_value(f"{step}: ", desc)

pdf.section_title("Background Pipeline (Per Document)")
pipeline_steps = [
    "OCR Extraction (PaddleOCR) -> ocr_results",
    "IF Passport: MRZ Pipeline -> mrz_results (Detection, Parse, Checksum, OCR<->MRZ Comparison)",
    "Document Validation -> validation_results (Required fields, Format, Expiry, Reference DB)",
    "Tampering Detection -> tamper_results (RGB, Noise, Forensics, Heatmap)",
    "IF Passport: Face Verification -> face_results (Detect, Embed, Compare, Match Status)",
]
for s in pipeline_steps:
    pdf.bullet_point(s)

pdf.body_text("After all documents: Cross-Document Verification -> Risk Assessment (aggregate weighted factors, apply thresholds, generate explanations)")

# ============ 8. SECURITY ============
pdf.chapter_title("8", "Security & Privacy")

sec_measures = [
    ("Authentication", "JWT with 8hr expiry, bcrypt passwords"),
    ("Authorization", "Officer-scoped data access via middleware"),
    ("CORS", "Restricted to frontend origin"),
    ("File Upload", "Type validation, 10MB limit, secure filenames"),
    ("Data Storage", "No real PII - synthetic demo data only"),
    ("Audit Trail", "Every action logged with officer, timestamp, details"),
    ("No Real DB Connections", "Mock reference database clearly labeled"),
    ("Prototype Disclaimers", "UI states 'DEMO/REFERENCE DATA' throughout"),
]
for measure, impl in sec_measures:
    pdf.bullet_bold_value(f"{measure}: ", impl)

# ============ 9. DEPLOYMENT ============
pdf.chapter_title("9", "Deployment Architecture")

pdf.section_title("Docker Compose Services")
deploy_cols = ["Service", "Port", "Purpose"]
deploy_data = [
    ["postgres", "5432", "Primary database"],
    ["redis", "6379", "Cache & Celery broker"],
    ["backend", "8000", "FastAPI (uvicorn + reload)"],
    ["frontend", "5173", "Vite dev server (HMR)"],
]
widths = [30, 20, 140]
pdf.table_header(deploy_cols, widths)
for i, row in enumerate(deploy_data):
    pdf.table_row(row, widths, fill=i%2==0)

pdf.ln(5)
pdf.section_title("Production Considerations")
prod_items = [
    ("File Storage", "S3/MinIO with presigned URLs"),
    ("Background Tasks", "Celery workers (separate containers)"),
    ("SSL/TLS", "Nginx reverse proxy + Let's Encrypt"),
    ("Monitoring", "Prometheus + Grafana"),
    ("Logging", "Structured JSON logs -> ELK/Loki"),
    ("Secrets", "Vault or Docker secrets"),
    ("Scaling", "K8s deployment with HPA"),
]
for item, upgrade in prod_items:
    pdf.bullet_bold_value(f"{item}: ", upgrade)

# ============ 10. DEVELOPMENT ============
pdf.add_page()
pdf.chapter_title("10", "Development Workflow")

pdf.section_title("Adding a New Feature")
dev_steps = [
    "Check PROJECT_RULES.md - Verify not locked",
    "Backend: Add model -> schema -> service -> router -> migrate",
    "Frontend: Add types -> API call -> component -> page integration",
    "Test: Run both servers, verify flow",
    "Document: Update README if new endpoints",
]
for i, step in enumerate(dev_steps, 1):
    pdf.bullet_bold_value(f"Step {i}: ", step)

pdf.section_title("Code Quality Commands")
pdf.code_block(safe("""# Backend
cd backend && ruff check . && pytest

# Frontend
cd frontend && npm run lint && npm run build"""))

# ============ 11. WHY THIS ARCHITECTURE ============
pdf.chapter_title("11", "Why This Architecture")

why_items = [
    ("Officer-facing (not passenger)", "Auth, dashboard, case-centric workflow"),
    ("Explainable AI", "Risk engine shows every factor with weight"),
    ("Modular ML pipeline", "Each module independent service, swappable"),
    ("Real-time progress", "Polling queue with status updates"),
    ("Professional UI", "Tailwind design system, government aesthetic"),
    ("SIH Demo Ready", "5 pre-seeded cases covering all scenarios"),
    ("Extensible", "Clean interfaces for real DB integration"),
    ("Audit Compliant", "Immutable logs for every verification"),
]
for req, sol in why_items:
    pdf.bullet_bold_value(f"{req}: ", sol)

# ============ 12. FILE COUNT ============
pdf.chapter_title("12", "File Count Summary")

pdf.body_text("Total: ~45 source files")

pdf.sub_section_title("Backend (23 files)")
backend_files = [
    "app/main.py + config + database",
    "app/models/models.py (12 tables)",
    "app/schemas/schemas.py (40+ Pydantic models)",
    "app/api/v1/ (11 routers)",
    "app/services/ (6 ML modules)",
    "alembic/ (migrations)",
    "scripts/seed_demo_data.py",
    "requirements.txt, Dockerfile, .env.example",
]
for f in backend_files:
    pdf.bullet_point(f)

pdf.sub_section_title("Frontend (18 files)")
frontend_files = [
    "src/pages/ (3 main pages)",
    "src/components/common/ (Layout, UI kit)",
    "src/services/api.ts",
    "src/hooks/useAuth.tsx",
    "src/types/index.ts (all interfaces)",
    "src/utils/helpers.ts",
    "package.json, tsconfig, vite.config, tailwind.config",
    "Dockerfile, .env",
]
for f in frontend_files:
    pdf.bullet_point(f)

pdf.sub_section_title("Root (3 files)")
pdf.bullet_point("docker-compose.yml")
pdf.bullet_point("PROJECT_RULES.md")
pdf.bullet_point("README.md")

# ============ 13. RUNNING WITHOUT DOCKER ============
pdf.add_page()
pdf.chapter_title("13", "Running Without Docker")

pdf.section_title("Prerequisites")
prereq = [
    ("Python 3.10+", "https://python.org/downloads"),
    ("Node.js 18+", "https://nodejs.org"),
    ("PostgreSQL 15", "https://www.postgresql.org/download/"),
    ("Redis 7", "https://redis.io/download (Windows: github.com/microsoftarchive/redis/releases)"),
]
widths = [40, 150]
pdf.table_header(["Tool", "Download"], widths)
for i, (tool, link) in enumerate(prereq):
    pdf.table_row([tool, link], widths, fill=i%2==0)

pdf.ln(5)
pdf.section_title("Backend Setup")
pdf.code_block(safe("""cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with PostgreSQL credentials
alembic upgrade head
python scripts/seed_demo_data.py
uvicorn app.main:app --reload --port 8000"""))

pdf.section_title("Frontend Setup")
pdf.code_block(safe("""cd frontend
npm install
echo VITE_API_URL=http://localhost:8000/api/v1 > .env
npm run dev"""))

pdf.section_title("Verify")
verify_items = [
    ("Backend API", "http://localhost:8000/docs", "Swagger UI loads"),
    ("Frontend", "http://localhost:5173", "Login page appears"),
    ("Login", "OFFICER001 / SecurePass123!", "Redirects to dashboard"),
]
widths = [30, 70, 90]
pdf.table_header(["Service", "URL", "Test"], widths)
for i, row in enumerate(verify_items):
    pdf.table_row(row, widths, fill=i%2==0)

# ============ FINAL PAGE ============
pdf.add_page()
pdf.ln(30)
pdf.set_font('Helvetica', 'B', 18)
pdf.set_text_color(11, 31, 58)
pdf.cell(0, 12, 'End of Document', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font('Helvetica', '', 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, 'AI-Based Document Screening & Tamper Detection System', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'Problem Statement ID: 26188', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font('Helvetica', 'I', 10)
pdf.cell(0, 8, 'This document serves as the complete technical reference for the project.', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, 'All code is located in C:\\Users\\Abhiraj Mangire\\Documents\\AI-Border-Screening\\', align='C', new_x="LMARGIN", new_y="NEXT")

# Save
output_path = "C:\\Users\\Abhiraj Mangire\\Documents\\AI-Border-Screening\\PROJECT_DOCUMENTATION.pdf"
pdf.output(output_path)
print(f"PDF generated: {output_path}")