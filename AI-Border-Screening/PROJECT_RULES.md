# PROJECT_RULES.md

**MASTER PROJECT SPECIFICATION AND DESIGN CONSTITUTION**

**Application:** AI-Based Document Screening and Tamper Detection System
**Problem Statement ID:** 26188

---

**IMPORTANT:** This file must be treated as the highest-priority project-level instruction for all future development work. The AI coding agent/developer MUST READ PROJECT_RULES.md BEFORE EVERY EXECUTION, CODE CHANGE, FEATURE ADDITION, REFACTOR, UI CHANGE, DATABASE CHANGE, MODEL CHANGE, OR FILE MODIFICATION.

The purpose of this file is to prevent accidental changes to already-approved architecture, workflow, UI, modules, terminology, and design decisions.

---

## SECTION 1 — PROJECT PURPOSE

This project is an **officer-facing AI-assisted border/airport identity and document screening prototype**.

- The system is **NOT a passenger self-service system**.
- A trained border/security officer operates the system.
- The AI provides verification results, evidence, warnings, and risk signals.
- The officer remains the **final decision-maker**.
- The project is a prototype for SIH and must not claim access to real government immigration databases or real blacklist databases.

---

## SECTION 2 — NON-NEGOTIABLE / LOCKED REQUIREMENTS

🔒 **LOCKED — MUST NOT BE CHANGED WITHOUT EXPLICIT USER APPROVAL**

### 1. APPLICATION TYPE
The application is an officer-facing border/airport security screening system. It must NOT be converted into a passenger self-service application.

### 2. NUMBER OF MAIN PAGES
The application has exactly **3 primary pages**:
- **PAGE 1:** Officer Login
- **PAGE 2:** Officer Home / Scan & Upload + Dashboard + Processing Queue + Passenger History
- **PAGE 3:** Passenger Verification Details

A completion/thank-you state can exist after verification, but it is NOT a separate primary page.

### 3. MODULE STRUCTURE
Keep exactly **4 modules**:
- **MODULE 1** — OCR EXTRACTION
- **MODULE 2** — DOCUMENT VALIDATION
- **MODULE 3** — TAMPERING DETECTION
- **MODULE 4** — FACE VERIFICATION

Do NOT merge Module 4 into Module 3. Do NOT rename or remove these official module numbers. Module 3 may internally contain supporting fraud-analysis functions, but Face Verification remains Module 4.

### 4. PASSPORT PIPELINE
Passport processing must include:
```
Passport Image → OCR Extraction → MRZ Extraction → MRZ Decoding/Parsing → MRZ Checksum Validation → OCR ↔ MRZ Cross-Field Verification
```
MRZ processing is specifically associated with passports in this prototype.

### 5. OTHER DOCUMENT PIPELINE
Other supported documents (Visa, National ID, Residence/Travel Permit) use:
```
Document Image → OCR → Field Validation → Intra-Document Verification → Cross-Document Verification
```
Do not force MRZ processing onto documents that do not have an applicable MRZ.

### 6. CROSS-DOCUMENT VERIFICATION
The system must compare relevant fields across documents belonging to the same passenger.
Examples: Passport ↔ Visa, Passport ↔ National ID, Passport ↔ Permit
Relevant fields: Name, DOB, Passport number, Nationality, Other applicable identity fields

### 7. TAMPERING DETECTION
Tampering detection is the **CORE AI INNOVATION**. It must operate on **EVERY uploaded document**, not only passports.
Approved tampering approach:
- RGB Image Analysis
- Noise Residual Analysis
- Image Forensics
- Tamper Heatmap

The dashboard must display: Clear RGB image, Tamper heatmap, Noise residual visualization where technically reliable. Do not remove any of these without explicit approval.

### 8. FACE VERIFICATION
Face Verification is **MODULE 4** and remains separate. It must compare:
- Document Face ↔ Live Passenger Face
Display: Document face, Live face, Similarity/match percentage, Match status

### 9. PROCESSING QUEUE
Document/passenger processing must visually occur through a queue. Show: Waiting, Processing, Completed, Warning, Failed. Show processing percentage and current processing stage.

### 10. FINAL DASHBOARD
The final verification screen must display combined results of:
- OCR, Document validation, MRZ, Checksum, OCR ↔ MRZ verification
- Cross-document verification, Tampering detection, RGB image
- Tamper heatmap, Noise residual where available
- Face verification, Risk assessment, Document validity

### 11. RISK ASSESSMENT
The system must provide: **LOW, MEDIUM, HIGH**. The risk result must be explainable. Always show reasons behind the risk result. Do not present prototype thresholds as real government security standards.

### 12. OFFICER FINAL DECISION
The AI must NOT be represented as the final legal authority. The officer reviews the evidence and makes the final decision.

---

## SECTION 3 — LOCKED UI / THEME

🔒 **LOCKED DESIGN SYSTEM**

**Approved Visual Theme:** "Government Technology × Aviation Security × AI Forensics"

The interface must feel: Professional, Trustworthy, Secure, Modern, Government/institutional, Airport/border-security oriented, AI-powered, Technologically advanced.

It must NOT look like: Gaming UI, Consumer social media, Generic SaaS dashboard, Cartoon application, Excessively futuristic sci-fi interface.

**Approved Colour Semantics:**
- **GREEN** (#16A34A) = Verified / Valid / Low Risk
- **AMBER** (#F59E0B) = Warning / Medium Risk / Manual Review
- **RED** (#DC2626) = High Risk / Suspicious / Tampering
- **BLUE** (#1769E0) = Primary actions / Security interface
- **NEUTRAL** = Main interface

Use vibrant colours strategically. Do not arbitrarily replace the approved colour semantics.

**Typography:** Professional, highly readable, government/institutional sans-serif font. Do not use fake government seals, logos or imply affiliation with real government agency.

---

## SECTION 4 — LOCKED TECHNOLOGY ARCHITECTURE

Unless explicitly approved by the user, do not replace:

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| Image Processing | OpenCV |
| OCR | PaddleOCR |
| AI/ML Framework | PyTorch |
| Face Verification | Approved face embedding/comparison |
| API | REST |
| Version Control | Git |

The developer may add supporting libraries if necessary, but must not replace the primary architecture without asking first.

---

## SECTION 5 — DATABASE RULES

The database must remain relational and structured. Core entities:
- Officers, Passengers, Verification Cases, Documents
- OCR Results, MRZ Results, Validation Results
- Tampering Results, Face Results, Cross-Document Results
- Risk Assessments, Audit Logs

Large image files must not unnecessarily be stored directly inside PostgreSQL. Use file/object storage and store references/paths in the database.

---

## SECTION 6 — DEMO / DATA PRIVACY RULES

This is a prototype. Never claim access to:
- Real immigration databases
- Real government passport databases
- Real blacklist databases
- Real border-control systems

Use synthetic/demo/reference data. Never expose real personal identity data in demonstrations. Do not add real passenger data to the repository.

---

## SECTION 7 — WHAT CAN BE CHANGED WITHOUT ASKING

The developer MAY modify these without asking, provided locked requirements remain unchanged:
- Internal variable names, Function names, Component names, CSS implementation
- Minor spacing adjustments, Responsive layout improvements, Bug fixes
- Performance improvements, Error handling, Loading animations
- Accessibility improvements, Code organization, Internal API implementation
- Database query optimization, Minor UI alignment improvements
- Dependency versions when compatible, Internal helper functions, Test implementation

However, these changes must NOT alter the approved user experience or architecture.

---

## SECTION 8 — CHANGES THAT REQUIRE USER APPROVAL

⚠️ **ASK THE USER BEFORE MAKING ANY OF THESE CHANGES:**
- Changing the number of pages
- Changing the four-module structure
- Merging or removing modules
- Moving Face Verification into another module
- Removing MRZ processing from Passport
- Removing checksum validation
- Removing OCR ↔ MRZ cross-field verification
- Removing cross-document verification
- Removing RGB analysis, noise residual analysis, tamper heatmap, face verification
- Changing the overall workflow
- Changing the officer-facing nature of the application
- Changing the main frontend/backend framework
- Changing PostgreSQL, AI/ML architecture, approved theme, primary colour semantics
- Adding a major new page, Removing a major feature
- Changing the risk-assessment concept
- Connecting to real government systems
- Changing database architecture
- Changing security/privacy principles

---

## SECTION 9 — WHEN THE USER REQUESTS A CHANGE

If the user explicitly requests a change to a LOCKED requirement:
1. Identify which locked requirement is affected.
2. Briefly explain what will change.
3. Ask for confirmation if the request is ambiguous.
4. Only implement the change after explicit approval when necessary.

Do not silently override locked requirements.

---

## SECTION 10 — BEFORE EVERY EXECUTION

Before every development action:
1. **STEP 1:** Read this entire PROJECT_RULES.md file.
2. **STEP 2:** Identify which parts of the project the requested task affects.
3. **STEP 3:** Check the task against the LOCKED requirements.
4. **STEP 4:** If the task conflicts with a locked requirement, STOP and ask the user before modifying it.
5. **STEP 5:** If there is no conflict, proceed.
6. **STEP 6:** After implementation, verify that no locked requirement was accidentally changed.

---

## SECTION 11 — CHANGE LOG

Maintain a CHANGELOG section at the bottom of this file. Every user-approved change to a locked requirement must be recorded here.

**Format:**
```
DATE:
CHANGE:
REASON:
USER APPROVAL:
AFFECTED COMPONENTS:
```

Do not modify historical change-log entries.

---

## SECTION 12 — DEVELOPMENT PRINCIPLE

The application should prioritize:
1. Correctness
2. Explainability
3. Security
4. Privacy
5. Reliability
6. Modularity
7. Maintainability
8. Professional UI
9. SIH demonstration quality

Do not add unnecessary features simply to make the application appear larger. Every feature should contribute to the core problem statement.

---

## FINAL INSTRUCTION

**PROJECT_RULES.md is the MASTER PROJECT CONSTITUTION.**

**READ IT BEFORE EVERY EXECUTION.**

- Never silently change a locked requirement.
- Never remove an approved feature to simplify implementation without asking.
- Never replace an approved technology stack without asking.
- Never change the application workflow without approval.
- When uncertain whether a requested change conflicts with this document, **ASK THE USER FIRST**.

The goal is to continuously improve the implementation while preserving all previously approved architectural, functional and design decisions.