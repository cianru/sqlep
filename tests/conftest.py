import pytest

from sqlep.runners import QueryRunner
from sqlep.runners.hive import HiveRunner


@pytest.fixture
def query_runner(mocker):
    query_runner: QueryRunner = mocker.MagicMock()
    query_runner.set_debug.return_value = None
    query_runner.execute.return_value = None
    query_runner.drop_table_if_exists.return_value = None
    query_runner.create_table_like.return_value = None
    query_runner.fill_table_from_csv.return_value = None
    query_runner.add_column.return_value = None
    yield query_runner


@pytest.fixture
def hive(mocker):
    mocked_hive = mocker.patch('sqlep.runners.hive.hive')
    return mocked_hive


@pytest.fixture
def hive_cursor(mocker, hive):
    connect = mocker.MagicMock()
    hive.connect.return_value = connect
    cursor = mocker.MagicMock()
    connect.cursor.return_value.__enter__.return_value = cursor
    return cursor


@pytest.fixture
def hive_runner(mocker):
    return HiveRunner(
        config={
            'host': 'somehost',
            'username': 'anon',
            'configuration': {
                'tez.queue.name': 'default',
            }
        }
    )
