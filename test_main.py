import asyncio
from database import engine
import models
from fastapi.testclient import TestClient
from main import app

# Принудительно создаем таблицы в базе данных перед запуском тестов в CI
async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

asyncio.run(init_test_db())

client = TestClient(app)


def test_create_recipe():
    response = client.post(
        "/recipes",
        json={
            "title": "Тестовый пирог",
            "cooking_time": 45,
            "ingredients": "Мука, сахар, яблоки",
            "description": "Смешать и запекать 45 минут.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тестовый пирог"
    assert "id" in data


def test_get_recipes():
    response = client.get("/recipes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_recipe_detail_and_increment_views():
    # Создаем рецепт для теста
    create_response = client.post(
        "/recipes",
        json={
            "title": "Суп тестовый",
            "cooking_time": 20,
            "ingredients": "Вода, соль",
            "description": "Вскипятить воду, посолить.",
        },
    )
    recipe_id = create_response.json()["id"]

    # Проверяем детальную информацию
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["views"] >= 1
