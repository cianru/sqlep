import pandas as pd

from sqlep import QueryRunner
from sqlep.testing import run_test_query
from tests.utils import read_sql_file, csv_path, assertItemsEqual


def test_run_test_query__results_the_same_and_debug_true__no_exception_raised(mocker, query_runner: QueryRunner):
    # arrange
    query_runner.read_table.side_effect = [
        pd.read_csv(csv_path('results_the_same_and_debug_true__no_exception_raised/some_schema_some_table.csv')),
        pd.read_csv(csv_path('results_the_same_and_debug_true__no_exception_raised/some_schema_some_table.csv'))
    ]

    # act
    run_test_query(
        runner=query_runner,
        test_schema='tezt',
        tables={
            'other_schema.other_table': 'results_the_same_and_debug_true__no_exception_raised/other_schema_other_table.csv',
            'other_schema.another_table': 'results_the_same_and_debug_true__no_exception_raised/other_schema_another_table.csv'
        },
        expected={
            'some_schema.some_table': 'results_the_same_and_debug_true__no_exception_raised/some_schema_some_table.csv'
        },
        query=read_sql_file('results_the_same_and_debug_true__no_exception_raised/query.sql'),
        debug=True
    )

    # assert
    query_runner.set_debug.assert_called_once_with(True)

    assert query_runner.drop_table_if_exists.mock_calls == [
        mocker.call(table='tezt.other_schema_another_table'),
        mocker.call(table='tezt.other_schema_other_table'),
        mocker.call(table='tezt.some_schema_some_table'),
        mocker.call(table='tezt.some_schema_some_table_expected')
    ]

    # query_runner.create_table_like.assert_called_once_with()

    query_runner.add_column.assert_called_once_with(
        table='tezt.some_schema_some_table_expected',
        column_name='test_case_comment',
        column_type='STRING'
    )

    query_runner.execute.assert_called_once_with(
        query=read_sql_file('results_the_same_and_debug_true__no_exception_raised/query_patched.sql')
    )

    assert query_runner.read_table.mock_calls == [
        mocker.call(table_name='tezt.some_schema_some_table'),
        mocker.call(table_name='tezt.some_schema_some_table_expected'),
    ]
