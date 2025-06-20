import os
from fastapi import Response
import logbook
from fastapi.testclient import TestClient
from localres_marketplace_service.src.blockchain.user import Threshold, UserViewModel
from localres_marketplace_service.main import lifespan, app
import pytest

logger = logbook.Logger(__name__)

ADMIN_HEADER = {
    "Authorization": f"Bearer {os.environ.get('ADMIN_API_TOKEN')}"
}
CLIENT_HEADER = {
    "Authorization": f"Bearer {os.environ.get('CLIENT_API_TOKEN')}"
}


@pytest.mark.asyncio
async def test_add_user():
    logger.info("test_add_user")
    async with lifespan(app):
        client = TestClient(app)
        test_threshold_new_user: list[Threshold] = [
            Threshold(hour=0, value=0),
            Threshold(hour=1, value=0),
            Threshold(hour=2, value=0),
            Threshold(hour=3, value=0),
            Threshold(hour=4, value=0),
            Threshold(hour=5, value=0),
            Threshold(hour=6, value=0),
            Threshold(hour=7, value=0),
            Threshold(hour=8, value=0),
            Threshold(hour=9, value=0),
            Threshold(hour=10, value=0),
            Threshold(hour=11, value=0),
            Threshold(hour=12, value=0),
            Threshold(hour=13, value=0),
            Threshold(hour=14, value=0),
            Threshold(hour=15, value=0),
            Threshold(hour=16, value=0),
            Threshold(hour=17, value=0),
            Threshold(hour=18, value=0),
            Threshold(hour=19, value=0),
            Threshold(hour=20, value=0),
            Threshold(hour=21, value=0),
            Threshold(hour=22, value=0),
            Threshold(hour=23, value=0)
        ]
        test_user: UserViewModel = UserViewModel(
            user_id="88",
            balance=0,
            thresholds=test_threshold_new_user

        )
        response: Response = client.put(headers=ADMIN_HEADER, url="/blockchain/user", json=test_user.model_dump()  # test_user
                                        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_user():
    logger.info("test_delete_user")
    async with lifespan(app):
        client = TestClient(app)
        user_id = "88"
        response = client.delete(f"/blockchain/user/{user_id}", headers=ADMIN_HEADER)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_data_by_user():
    logger.info("test_read_data_by_user")
    async with lifespan(app):
        client = TestClient(app)
        user_id = "66"
        response = client.get(
            f"/blockchain/user/{user_id}", headers=CLIENT_HEADER)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_all_users():
    logger.info("test_get_all_users")
    async with lifespan(app):
        client = TestClient(app)
        response = client.get("/blockchain/user", headers=CLIENT_HEADER)
        assert response.status_code == 200