import asyncio
import importlib
import pytest
from arcee.arcee_receiver.tests.base import AConfigClMock, DB_MOCK


@pytest.fixture
def mock_base(mocker):
    mocker.patch('optscale_client.aconfig_cl.aconfig_cl.AConfigCl',
                 AConfigClMock)
    mocker.patch('arcee.arcee_receiver.server.db', DB_MOCK)


async def return_false(*_args):
    return False


@pytest.fixture
def mock_dataset(mock_base, mocker):
    mocker.patch(
        'arcee.arcee_receiver.server._dataset_used_in_leaderboard',
        return_false)


@pytest.fixture
def app(mock_base):
    arcee_app = importlib.import_module('arcee.arcee_receiver.server')
    return arcee_app.app


async def clean_env():
    await DB_MOCK['token'].drop()
    await DB_MOCK['metric'].drop()
    await DB_MOCK['task'].drop()
    await DB_MOCK['leaderboard'].drop()
    await DB_MOCK['leaderboard_dataset'].drop()
    await DB_MOCK['run'].drop()
    await DB_MOCK['model'].drop()
    await DB_MOCK['model_version'].drop()
    await DB_MOCK['log'].drop()
    await DB_MOCK['platform'].drop()
    await DB_MOCK['dataset'].drop()
    await DB_MOCK['artifact'].drop()


@pytest.fixture(autouse=True)
def clean_db_after_test():
    yield
    asyncio.run(clean_env())
