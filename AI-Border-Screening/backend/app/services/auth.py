from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Officer
from app.utils.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_officer(db: AsyncSession, officer_id: str, password: str) -> Optional[Officer]:
    result = await db.execute(select(Officer).where(Officer.officer_id == officer_id))
    officer = result.scalar_one_or_none()
    if not officer:
        return None
    if not verify_password(password, officer.hashed_password):
        return None
    return officer


async def get_officer_by_id(db: AsyncSession, officer_id: str) -> Optional[Officer]:
    result = await db.execute(select(Officer).where(Officer.officer_id == officer_id))
    return result.scalar_one_or_none()


async def create_demo_officer(db: AsyncSession) -> Officer:
    demo_officer = Officer(
        officer_id="OFFICER001",
        email="officer001@border.gov.in",
        hashed_password=get_password_hash("SecurePass123!"),
        full_name="Officer Rajesh Kumar",
        badge_number="BADGE-2024-001",
        department="Immigration & Border Security",
        is_active=True,
    )
    db.add(demo_officer)
    await db.commit()
    await db.refresh(demo_officer)
    return demo_officer