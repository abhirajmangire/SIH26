from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.database.session import get_db
from app.schemas.schemas import (
    OfficerCreate, OfficerLogin, OfficerResponse, Token, TokenData
)
from app.services.auth import (
    authenticate_officer, create_access_token, get_officer_by_id, create_demo_officer
)
from app.utils.config import settings


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_officer(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> OfficerResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        officer_id: str = payload.get("sub")
        if officer_id is None:
            raise credentials_exception
        token_data = TokenData(officer_id=officer_id)
    except JWTError:
        raise credentials_exception
    
    officer = await get_officer_by_id(db, officer_id=token_data.officer_id)
    if officer is None:
        raise credentials_exception
    return officer


@router.post("/login", response_model=Token)
async def login(
    form_data: OfficerLogin,
    db: AsyncSession = Depends(get_db)
):
    officer = await authenticate_officer(db, form_data.officer_id, form_data.password)
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid officer ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": officer.officer_id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=OfficerResponse)
async def register(
    officer_data: OfficerCreate,
    db: AsyncSession = Depends(get_db)
):
    existing = await get_officer_by_id(db, officer_data.officer_id)
    if existing:
        raise HTTPException(status_code=400, detail="Officer ID already registered")
    
    from app.services.auth import get_password_hash
    from app.models.models import Officer
    
    hashed_password = get_password_hash(officer_data.password)
    officer = Officer(
        officer_id=officer_data.officer_id,
        email=officer_data.email,
        hashed_password=hashed_password,
        full_name=officer_data.full_name,
        badge_number=officer_data.badge_number,
        department=officer_data.department,
    )
    db.add(officer)
    await db.commit()
    await db.refresh(officer)
    return officer


@router.get("/me", response_model=OfficerResponse)
async def read_officer_me(current_officer: OfficerResponse = Depends(get_current_officer)):
    return current_officer


@router.post("/init-demo")
async def init_demo_officer(db: AsyncSession = Depends(get_db)):
    officer = await create_demo_officer(db)
    return {"message": "Demo officer created", "officer_id": officer.officer_id}