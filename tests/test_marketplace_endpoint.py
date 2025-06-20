import os
from httpx import AsyncClient
import pytest
from localres_marketplace_service.main import lifespan, app

import logbook

logger = logbook.Logger(__name__)

STATIC_HEADER = {
    "Authorization": f"Bearer {os.environ.get('ADMIN_API_TOKEN')}"
}

@pytest.mark.asyncio
async def test_marketplace_database_run():
    logger.info("test_marketplace_run")
    async with lifespan(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/marketplace/database/run", headers=STATIC_HEADER)
            assert response.status_code == 200

