# 🛂 AI-Based Document Screening & Tamper Detection System

> **Problem Statement ID: 26188** | **Smart India Hackathon (SIH) Prototype**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-SIH%20Prototype-orange)](#)

---

## 🎯 Overview

An **officer-facing** border/airport security document screening prototype with **AI-assisted verification**. A trained border security officer uploads/scans passenger documents (passport, visa, national ID, permits) and face captures, while the system performs multi-module AI verification and presents evidence-based results. **The officer remains the final decision-maker** — AI provides screening signals, not legal determinations.

### ✨ Key Capabilities

| Module | Description |
|--------|-------------|
| **🔍 OCR Extraction** | PaddleOCR-based text extraction with confidence scoring for 4 document types |
| **📖 MRZ Pipeline** | ICAO TD3 passport MRZ detection, parsing, checksum validation & OCR↔MRZ cross-field comparison |
| **✅ Document Validation** | Field-level rules, format checks, expiry validation, mock reference database lookup |
| **🔬 Tampering Detection** | **Core Innovation** — Multi-forensic: RGB analysis, noise residual (NLM), ELA, texture analysis, heatmap generation |
| **👤 Face Verification** | InsightFace embeddings + cosine similarity (document face vs live capture) |
| **🔗 Cross-Document** | Identity field consistency across all uploaded documents |
| **📊 Risk Assessment** | Weighted explainable risk engine (LOW/MEDIUM/HIGH) with factor breakdown |
| **📋 Audit Trail** | Immutable logging of all officer actions |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND (React + Vite + TS)                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│  │   Login    │  │ Dashboard  │  │Verification│  │   UI Components    │   │
│  │   (Page 1) │  │  (Page 2)  │  │  (Page 3)  │  │   (Buttons, Cards, │   │
│  └────────────┘  └────────────┘  └────────────┘  │   Tables, Charts)  │   │
└─────────────────│─────────────────│─────────────────┘────────────────────┘
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │      REST API (Axios + JWT)   │
                    └───────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND (FastAPI + Python)                       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐ ┌──────┐ ┌──────┐ │
│  │ Auth │ │Cases │ │ Docs │ │ OCR  │ │ MRZ  │ │Validat.│ │Tamper│ │ Face │ │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └────────┘ └──────┘ └──────┘ │
│  ┌────────────────────────── SERVICE LAYER ────────────────────────────┐   │
│  │  OCR → MRZ → Validation → Tampering → Face → Cross-Doc → Risk       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────│───────────────────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
   ┌────────────┐          ┌────────────┐          ┌────────────┐
   │PostgreSQL  │          │   Redis    │          │  File      │
   │(Relational)│          │(Cache/Queue)│         │  Storage   │
   └────────────┘          └────────────┘          └────────────┘
```

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
git clone <repo-url>
cd AI-Border-Screening
docker-compose up -d
```

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |

### Option 2: Manual Setup

<details>
<summary><strong>Click to expand manual setup instructions</strong></summary>

#### Prerequisites
- Python 3.10+ | Node.js 18+ | PostgreSQL 15+ | Redis 7+

#### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure DATABASE_URL
alembic upgrade head
python scripts/seed_demo_data.py
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
npm run dev
```
</details>

---

## 🔐 Demo Credentials

| Field | Value |
|-------|-------|
| **Officer ID** | `OFFICER001` |
| **Password** | `SecurePass123!` |

---

## 📸 Screenshots

### Page 1: Officer Login
> Clean, security-themed authentication with navy background and centered card

### Page 2: Officer Dashboard
> **Statistics Cards** • **Risk Distribution** • **Document Upload (Drag & Drop)** • **Live Processing Queue** • **Passenger History**

### Page 3: Verification Details
> **Timeline** • **OCR Results** • **MRZ Comparison Table** • **Validation Results** • **Cross-Document Matrix** • **Tampering Panel (RGB | Heatmap | Noise)** • **Face Comparison** • **Explainable Risk Assessment** • **Final Summary**

---

## 🧪 Demo Test Cases (Pre-Seeded)

| Case ID | Scenario | Expected Risk |
|---------|----------|---------------|
| `CASE-240115-001` | All valid, no tampering, face match | 🟢 **LOW** |
| `CASE-240115-002` | OCR/MRZ DOB mismatch + expired passport | 🔴 **HIGH** |
| `CASE-240115-003` | Digital manipulation (91% tamper prob) | 🔴 **HIGH** |
| `CASE-240115-004` | Cross-document passport# mismatch | 🔴 **HIGH** |
| `CASE-240115-005` | Face similarity 58.2% | 🟡 **MEDIUM** |

---

## 📁 Project Structure

```
AI-Border-Screening/
├── PROJECT_RULES.md           # Master specification (READ FIRST)
├── README.md                  # This file
├── docker-compose.yml         # 4-service stack
├── PROJECT_DOCUMENTATION.pdf  # Full technical docs
│
├── backend/
│   ├── app/
│   │   ├── api/v1/            # 11 REST routers
│   │   ├── models/            # 12 SQLAlchemy models
│   │   ├── schemas/           # 40+ Pydantic schemas
│   │   ├── services/          # 6 ML modules
│   │   │   ├── ocr/           # PaddleOCR wrapper
│   │   │   ├── mrz/           # TD3 parser + checksum
│   │   │   ├── validation/    # Rules + reference DB
│   │   │   ├── tamper/        # Multi-forensic pipeline
│   │   │   ├── face/          # InsightFace embeddings
│   │   │   └── risk/          # Weighted risk engine
│   │   └── database/          # Async SQLAlchemy + Alembic
│   ├── alembic/               # Migrations
│   └── scripts/seed_demo_data.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/             # Login, Dashboard, Verification
│   │   ├── components/common/ # Layout, UI kit (Button, Card, etc.)
│   │   ├── services/api.ts    # Axios client + interceptors
│   │   ├── hooks/useAuth.tsx  # Auth context
│   │   └── types/index.ts     # All TypeScript interfaces
│   └── package.json
│
├── storage/                   # File storage (gitignored)
│   ├── documents/
│   ├── heatmaps/
│   ├── noise_residuals/
│   └── faces/
│
└── models/                    # ML model weights (gitignored)
```

---

## ⚙️ Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/border_screening
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-min-32-chars
CORS_ORIGINS=["http://localhost:5173"]
UPLOAD_DIR=./storage/documents
HEATMAP_DIR=./storage/heatmaps
NOISE_RESIDUAL_DIR=./storage/noise_residuals
FACE_DIR=./storage/faces
FACE_SIMILARITY_THRESHOLD=0.75
TAMPER_THRESHOLD=0.70
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 🔑 API Endpoints

<details>
<summary><strong>Authentication</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Officer login → JWT |
| POST | `/api/v1/auth/register` | Register officer |
| GET | `/api/v1/auth/me` | Current officer profile |
| POST | `/api/v1/auth/init-demo` | Seed demo officer |
</details>

<details>
<summary><strong>Cases & Documents</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cases` | Create verification case |
| GET | `/api/v1/cases` | List cases (paginated) |
| GET | `/api/v1/cases/{id}` | Case details |
| POST | `/api/v1/cases/{id}/documents` | Upload document |
| GET | `/api/v1/cases/{id}/queue` | Processing queue status |
| POST | `/api/v1/cases/{id}/process` | Start async pipeline |
| GET | `/api/v1/cases/history` | Passenger history (filtered) |
</details>

<details>
<summary><strong>Processing Modules</strong></summary>

| Module | Endpoint |
|--------|----------|
| OCR | `GET /api/v1/ocr/case/{case_id}` |
| MRZ | `GET /api/v1/mrz/case/{case_id}` |
| Validation | `GET /api/v1/validation/case/{case_id}` |
| Tampering | `GET /api/v1/tamper/case/{case_id}` |
| Face | `GET /api/v1/face/case/{case_id}` |
| Risk | `GET /api/v1/risk/case/{case_id}` |
</details>

<details>
<summary><strong>Verification</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/verification/{case_id}/detail` | Complete evidence view |
| POST | `/api/v1/verification/{case_id}/complete` | Finalize + audit log |
</details>

---

## 🛡️ Security & Privacy

- **No real PII** — Synthetic/demo data only
- **JWT authentication** — 8hr expiry, bcrypt hashing
- **Officer-scoped access** — Middleware enforces data isolation
- **File validation** — Type allowlist, 10MB limit, secure filenames
- **Audit logging** — Every action tracked with officer, timestamp, details
- **Prototype disclaimers** — UI clearly labels "DEMO/REFERENCE DATA"
- **No government DB connections** — Mock reference database only

---

## 📦 Deployment

### Production Checklist
- [ ] Replace file storage with S3/MinIO + presigned URLs
- [ ] Deploy Celery workers as separate containers
- [ ] Add Nginx reverse proxy + TLS (Let's Encrypt)
- [ ] Configure Prometheus + Grafana monitoring
- [ ] Structured JSON logging → ELK/Loki
- [ ] Secrets management (Vault/Docker secrets)
- [ ] K8s deployment with HPA

---

## 🤝 Contributing

This is a SIH prototype. For contributions:
1. Read `PROJECT_RULES.md` first (locked requirements)
2. Check locked vs changeable sections
3. Follow existing code patterns (FastAPI + React + TypeScript)
4. Run linting: `ruff check .` (backend) / `npm run lint` (frontend)

---

## 📄 Documentation

- **Technical Guide**: `PROJECT_DOCUMENTATION.pdf` (13 chapters)
- **Master Spec**: `PROJECT_RULES.md` (constitution for all changes)
- **API Docs**: http://localhost:8000/docs (Swagger UI)

---

## ⚠️ Disclaimer

> **This is a SIH prototype, not a production immigration/border-control system.**
>
> - Does NOT connect to real government databases
> - Does NOT claim access to real blacklists
> - Does NOT automatically approve/reject passengers
> - Prototype thresholds ≠ official security standards
> - Uses synthetic data only

---

## 👥 Team

Built for **Smart India Hackathon 2024** — Problem Statement 26188

---

## 📜 License

Prototype for SIH demonstration purposes only.