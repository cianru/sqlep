import pytest

from sqlep.runners import QueryRunner


@pytest.fixture
def query_runner(mocker):
    query_runner: QueryRunner = mocker.MagicMock()
    query_runner.set_debug.return_value = None
    query_runner.execute.return_value = None
    query_runner.drop_table_if_exists.return_value = None
    query_runner.create_table_like.return_value = None
    query_runner.fill_table_from_csv.return_value = None
    query_runner.add_column.return_value = None
    query_runner.read_table.return_value = []
    yield query_runner
