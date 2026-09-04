from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.session import engine, Base
from app.api.v1 import auth, cases, documents, ocr, mrz, validation, tamper, face, verification, dashboard, risk
from app.utils.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="AI-Based Document Screening and Tamper Detection System",
    description="Officer-facing border/airport security document screening prototype",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(mrz.router, prefix="/api/v1/mrz", tags=["MRZ"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
app.include_router(tamper.router, prefix="/api/v1/tamper", tags=["Tampering Detection"])
app.include_router(face.router, prefix="/api/v1/face", tags=["Face Verification"])
app.include_router(verification.router, prefix="/api/v1/verification", tags=["Verification"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk Assessment"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI-Based Document Screening and Tamper Detection System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)