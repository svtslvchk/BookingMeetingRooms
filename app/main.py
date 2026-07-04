import logging
import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from app.routers import auth, users, room, booking


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Система бронирования переговорных комнат",
    version="0.1.0"
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Ловит любые непредвиденные ошибки (KeyError, ValueError, Ошибки БД и т.д.),
    которые не были обработаны вручную через HTTPException.
    """
    # exc_info=True автоматически прикрепит весь трейсбек ошибки в консоль
    logger.error(
        f"Непредвиденная ошибка при запросе {request.method} {request.url.path}: {exc}", 
        exc_info=True
    )
    
    # Возвращаем стандартизированный JSON клиенту
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "error": "Internal Server Error",
            "message": "На сервере произошла непредвиденная ошибка. Мы уже чиним её."
        }
    )

# Подключение роутера аутентификации
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(room.router)
app.include_router(booking.router)


@app.get("/test-500")
async def trigger_unexpected_error():
    """Тестовый эндпоинт, чтобы проверить работу хендлера."""
    # Искусственно вызываем падение, которого нет в HTTPException
    division_by_zero = 1 / 0
    return {"result": division_by_zero}


@app.get("/", response_class=FileResponse)
async def read_root():
    index_path = os.path.join("app", "static", "index.html")
    return FileResponse(index_path)

app.mount("/static", StaticFiles(directory="app/static"), name="static")