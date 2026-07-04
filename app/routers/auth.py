from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserOut, Token
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Зависимость для получения сессии БД
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли пользователь
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Хешируем пароль и сохраняем
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        name=user_data.name
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    # Ищем пользователя по email
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # Проверяем существование и пароль
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Создаем JWT токен (sub принимает строковое значение ID)
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
