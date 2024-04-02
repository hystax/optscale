import asyncio
import importlib
import pytest
from arcee.arcee_receiver.tests.base import AConfigClMock, DB_MOCK


@pytest.fixture
def mock_base(mocker):
    mocker.patch('optscale_client.aconfig_cl.aconfig_cl.AConfigCl',
                 AConfigClMock)
    mocker.patch('arcee.arcee_receiver.server.db', DB_MOCK)


@pytest.fixture
def app(mock_base):
    arcee_app = importlib.import_module('arcee.arcee_receiver.server')
    return arcee_app.app


async def clean_env():
    await DB_MOCK['token'].drop()
    await DB_MOCK['metric'].drop()
    await DB_MOCK['task'].drop()
    await DB_MOCK['leaderboard'].drop()
    await DB_MOCK['run'].drop()
    await DB_MOCK['model'].drop()
    await DB_MOCK['model_version'].drop()


@pytest.fixture(autouse=True)
def clean_db_after_test():
    yield
    asyncio.run(clean_env())
