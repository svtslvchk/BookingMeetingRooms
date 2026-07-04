import pytest
from httpx import AsyncClient
from fastapi import status

pytestmark = pytest.mark.asyncio

# Данные валидного пользователя
VALID_USER = {
    "email": "tester@example.com",
    "password": "securepassword123",
    "name": "Тестовый Пользователь"
}


# --- ТЕСТЫ РЕГИСТРАЦИИ ---

async def test_register_success(client: AsyncClient):
    """Проверка успешной регистрации нового пользователя."""
    response = await client.post("/auth/register", json=VALID_USER)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    data = response.json()
    assert data["email"] == VALID_USER["email"]
    assert "id" in data


async def test_register_duplicate_email(client: AsyncClient):
    """Регистрация пользователя с уже существующим email должна вызывать ошибку."""
    # 1. Регистрируем в первый раз
    await client.post("/auth/register", json=VALID_USER)

    # 2. Пытаемся зарегистрировать тот же самый email повторно
    response = await client.post("/auth/register", json=VALID_USER)

    # Сервер должен вернуть 400 Bad Request или 409 Conflict (зависит от твоей логики)
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT]


# --- ТЕСТЫ АВТОРИЗАЦИИ (ЛОГИНА) ---

async def test_login_success(client: AsyncClient):
    """Проверка успешной авторизации и получения JWT-токена."""
    # Создаем пользователя, чтобы ему было под чем войти
    await client.post("/auth/register", json=VALID_USER)

    login_data = {"email": VALID_USER["email"], "password": VALID_USER["password"]}
    response = await client.post("/auth/login", json=login_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    """Попытка входа с неверным паролем должна отклоняться."""
    await client.post("/auth/register", json=VALID_USER)

    # Передаем правильный email, но ломаем пароль
    login_data = {"email": VALID_USER["email"], "password": "wrong_password_here"}
    response = await client.post("/auth/login", json=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login_user_not_found(client: AsyncClient):
    """Попытка входа с несуществующим email должна возвращать 401."""
    # Стучимся под абсолютно левыми данными в пустую базу
    login_data = {"email": "ghost@example.com", "password": "some_password"}
    response = await client.post("/auth/login", json=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
