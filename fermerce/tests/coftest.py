import pytest
from fermerce.core.settings import config
import edgy
from edgy.testclient import DatabaseTestClient
from esmerald.testclient import EsmeraldTestClient

from main import get_application

database = DatabaseTestClient(config.get_database_url(), drop_database=True)
models = edgy.Registry(database=database)

pytestmark = pytest.mark.anyio


@pytest.fixture(autouse=True, scope="module")
def test_application():
    app = get_application()
    client = EsmeraldTestClient(app)
    yield client


@pytest.fixture(autouse=True, scope="module")
async def create_test_database():
    await models.create_all()
    yield
    await models.drop_all()


@pytest.fixture(autouse=True)
async def rollback_transactions():
    with database.force_rollback():
        async with database:
            yield
