import pytest

from sqlep.runners import QueryRunner
from sqlep.testing import run_test_query
from tests.utils import read_sql_file


def test_test_query__a__(query_runner):
    # arrange


    # act
    run_test_query(
        runner=query_runner,
        test_schema='tezt',
        tables={},
        expected={},
        query=read_sql_file('query.sql')
    )

    # assert
    query_runner.execute.assert_called_once_with(
        query=read_sql_file('query_patched.sql')
    )
