from fastapi import APIRouter, Depends
from app.schemas.user import UserOut
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Возвращает данные текущего аутентифицированного пользователя."""
    return current_user
