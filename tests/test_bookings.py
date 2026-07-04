import pytest
from httpx import AsyncClient
from fastapi import status

# Тестовый пользователь для регистрации и авторизации
TEST_USER = {
    "email": "booking_tester@example.com",
    "password": "supersecretpassword",
    "name": "Семён Тестеров"
}


async def get_auth_headers(client: AsyncClient) -> dict:
    """Вспомогательная функция для регистрации, логина и получения токена."""
    # 1. Регистрируем пользователя
    await client.post("/auth/register", json=TEST_USER)
    
    # 2. Логинимся, чтобы забрать токен
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    login_response = await client.post("/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_room(client: AsyncClient):
    """Проверка успешного создания новой переговорной комнаты."""
    # Получаем токен (если создание комнат требует авторизации)
    headers = await get_auth_headers(client)

    room_data = {
        "name": "Переговорка Альфа",
        "capacity": 12
    }

    response = await client.post("/rooms", json=room_data, headers=headers)

    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    data = response.json()
    assert "id" in data
    assert data["name"] == room_data["name"]
    assert data["capacity"] == room_data["capacity"]


@pytest.mark.asyncio
async def test_create_booking_success(client: AsyncClient):
    """Проверка успешного бронирования комнаты на свободное время."""
    headers = await get_auth_headers(client)

    # 1. Создаем комнату, которую будем бронировать
    room_data = {"name": "Зал Совета", "capacity": 8}
    room_response = await client.post("/rooms", json=room_data, headers=headers)
    room_id = room_response.json()["id"]

    # 2. Формируем запрос на бронирование (на свободное время)
    booking_data = {
        "room_id": room_id,
        "time_start": "2026-07-04T14:00:00",
        "time_end": "2026-07-04T15:00:00"
    }

    response = await client.post("/bookings", json=booking_data, headers=headers)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    data = response.json()
    assert "id" in data
    assert data["room_id"] == room_id
    assert data["time_start"].startswith("2026-07-04T14:00")


@pytest.mark.asyncio
async def test_booking_overlap_conflict(client: AsyncClient):
    """Проверка пересечения временных интервалов (оверлап).
    Второе бронирование на то же время должно падать с ошибкой 409 Conflict.
    """
    headers = await get_auth_headers(client)

    # 1. Создаем комнату
    room_data = {"name": "Кремниевая Долина", "capacity": 6}
    room_response = await client.post("/rooms", json=room_data, headers=headers)
    room_id = room_response.json()["id"]

    # 2. Первая бронь: с 14:00 до 15:00 (Успешно)
    first_booking = {
        "room_id": room_id,
        "time_start": "2026-07-04T14:00:00",
        "time_end": "2026-07-04T15:00:00"
    }
    first_response = await client.post("/bookings", json=first_booking, headers=headers)
    assert first_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    # 3. Вторая бронь: с 14:30 до 15:30 (Должен быть конфликт)
    conflict_booking = {
        "room_id": room_id,
        "time_start": "2026-07-04T14:30:00",
        "time_end": "2026-07-04T15:30:00"
    }
    conflict_response = await client.post("/bookings", json=conflict_booking, headers=headers)

    # Проверяем, что сервер вернул 409 Conflict
    assert conflict_response.status_code == status.HTTP_409_CONFLICT

    # На всякий случай проверяем, что в теле ответа есть вменяемая ошибка
    assert "detail" in conflict_response.json()
