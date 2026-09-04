# AI-Based Document Screening and Tamper Detection System

**Problem Statement ID:** 26188

An officer-facing border/airport security document screening prototype with AI-assisted verification and tamper detection.

## Architecture

- **Frontend:** React + Vite + TypeScript + Tailwind CSS
- **Backend:** Python + FastAPI + SQLAlchemy (async)
- **Database:** PostgreSQL 15
- **Cache/Queue:** Redis 7
- **OCR:** PaddleOCR
- **Face Verification:** InsightFace (buffalo_l model)
- **Tampering Detection:** Custom forensic pipeline (OpenCV + NumPy)

## Project Structure

```
AI-Border-Screening/
├── PROJECT_RULES.md          # Master specification (READ FIRST)
├── README.md
├── docker-compose.yml
├── frontend/                 # React + Vite application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components (Login, Dashboard, Verification)
│   │   ├── services/         # API service layer
│   │   ├── hooks/            # Custom React hooks
│   │   ├── utils/            # Utility functions
│   │   └── types/            # TypeScript type definitions
│   └── package.json
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/v1/           # API routes
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic services
│   │   │   ├── ocr/          # OCR extraction
│   │   │   ├── mrz/          # MRZ parsing & validation
│   │   │   ├── validation/   # Document validation
│   │   │   ├── tamper/       # Tampering detection
│   │   │   ├── face/         # Face verification
│   │   │   └── risk/         # Risk assessment engine
│   │   ├── database/         # Database session & config
│   │   └── utils/            # Configuration & utilities
│   ├── requirements.txt
│   └── .env.example
├── storage/                  # File storage (documents, heatmaps, etc.)
├── models/                   # ML model weights
└── tests/                    # Test suites
```

## Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Node.js 18+, Python 3.10+, PostgreSQL 15+, Redis 7+

### Using Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd AI-Border-Screening

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Manual Setup

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Create demo officer
python -c "
import asyncio
from app.database.session import AsyncSessionLocal
from app.services.auth import create_demo_officer

async def init():
    async with AsyncSessionLocal() as db:
        await create_demo_officer(db)

asyncio.run(init())
"

# Start server
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Demo Credentials

For prototype demonstration:
- **Officer ID:** `OFFICER001`
- **Password:** `SecurePass123!`

## Demo Test Cases

| Case | Description | Expected Risk |
|------|-------------|---------------|
| CASE 001 | All valid, no tampering, face match | LOW |
| CASE 002 | OCR/MRZ DOB mismatch | HIGH |
| CASE 003 | Digital manipulation detected | HIGH |
| CASE 004 | Cross-document passport number mismatch | HIGH |
| CASE 005 | Face similarity below threshold | MEDIUM |

To run demo cases, use the provided test scripts or upload sample documents through the UI.

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Officer login
- `POST /api/v1/auth/register` - Register new officer
- `GET /api/v1/auth/me` - Get current officer info
- `POST /api/v1/auth/init-demo` - Initialize demo officer

### Cases
- `POST /api/v1/cases` - Create new verification case
- `GET /api/v1/cases` - List cases (paginated)
- `GET /api/v1/cases/{case_id}` - Get case details
- `POST /api/v1/cases/{case_id}/documents` - Upload document
- `GET /api/v1/cases/{case_id}/documents` - Get case documents
- `GET /api/v1/cases/{case_id}/queue` - Get processing queue
- `POST /api/v1/cases/{case_id}/process` - Start processing pipeline
- `GET /api/v1/cases/history` - Get passenger history (with filters)
- `GET /api/v1/cases/passengers/search` - Search passengers
- `POST /api/v1/cases/passengers` - Create passenger record

### Processing Modules
- `GET /api/v1/ocr/case/{case_id}` - Get OCR results
- `GET /api/v1/mrz/case/{case_id}` - Get MRZ results
- `GET /api/v1/validation/case/{case_id}` - Get validation results
- `GET /api/v1/tamper/case/{case_id}` - Get tampering results
- `GET /api/v1/face/case/{case_id}` - Get face verification results
- `GET /api/v1/risk/case/{case_id}` - Get risk assessment

### Verification
- `GET /api/v1/verification/{case_id}/detail` - Get complete verification details
- `POST /api/v1/verification/{case_id}/complete` - Complete verification

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics

## Key Features

### 1. Officer Login (Page 1)
- Secure authentication with JWT tokens
- Demo credentials for quick testing
- Professional security-themed UI

### 2. Officer Dashboard (Page 2)
- Real-time statistics cards
- Risk distribution visualization
- Document upload with drag-and-drop
- Face capture interface
- Live processing queue with progress tracking
- Passenger history with search/filter

### 3. Verification Details (Page 3)
- Complete verification pipeline visualization
- OCR extraction results with confidence scores
- MRZ parsing, decoding, and checksum validation
- OCR ↔ MRZ cross-field comparison
- Document validation with reference database checks
- Cross-document consistency verification
- AI tampering detection:
  - RGB image analysis
  - Noise residual analysis
  - Forensic analysis (ELA, compression, texture)
  - Tamper heatmap generation
- Face verification with similarity scoring
- Explainable risk assessment with contributing factors
- Final verification summary

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
cd backend
ruff check .

# Frontend linting
cd frontend
npm run lint
```

## Configuration

### Backend Environment Variables (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/border_screening
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
CORS_ORIGINS=["http://localhost:5173"]
UPLOAD_DIR=./storage/documents
HEATMAP_DIR=./storage/heatmaps
NOISE_RESIDUAL_DIR=./storage/noise_residuals
FACE_DIR=./storage/faces
MAX_FILE_SIZE=10485760
OCR_LANG=en
FACE_SIMILARITY_THRESHOLD=0.75
TAMPER_THRESHOLD=0.70
DEBUG=true
```

### Frontend Environment Variables (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Prototype Constraints

This is a SIH prototype, not a production immigration/border-control system.

**DOES NOT:**
- Connect to real government immigration databases
- Claim access to real blacklist databases
- Automatically approve/reject real passengers
- Present prototype risk thresholds as official security standards
- Claim 100% forgery detection accuracy
- Store real sensitive passenger information unnecessarily

**USES:**
- Synthetic/demo/reference data
- Mock reference database with test records
- Modular architecture for future real database integration

## Security Notes

- All passwords hashed with bcrypt
- JWT tokens with configurable expiration
- CORS configured for specific origins
- File upload validation and size limits
- No sensitive data in frontend code
- Audit logging for all verification actions

## License

Prototype for SIH demonstration purposes only.