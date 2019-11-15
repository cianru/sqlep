import pandas as pd
import pytest

from sqlep.runners import QueryRunner
from sqlep.testing import run_test_query
from tests.utils import read_sql_file, csv_path


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
            'other_schema.other_table': csv_path(
                'results_the_same_and_debug_true__no_exception_raised/other_schema_other_table.csv'),
            'other_schema.another_table': csv_path(
                'results_the_same_and_debug_true__no_exception_raised/other_schema_another_table.csv')
        },
        expected={
            'some_schema.some_table': csv_path(
                'results_the_same_and_debug_true__no_exception_raised/some_schema_some_table.csv')
        },
        query=read_sql_file('results_the_same_and_debug_true__no_exception_raised/query.sql'),
        debug=True
    )

    # assert
    query_runner.set_debug.assert_called_once_with(debug=True)

    assert query_runner.drop_table_if_exists.mock_calls == [
        mocker.call(table_name='tezt.other_schema_another_table'),
        mocker.call(table_name='tezt.other_schema_other_table'),
        mocker.call(table_name='tezt.some_schema_some_table'),
        mocker.call(table_name='tezt.some_schema_some_table_expected')
    ]

    assert query_runner.create_table_like.mock_calls == [
        mocker.call(new_table='tezt.other_schema_other_table', origin_table='other_schema.other_table'),
        mocker.call(new_table='tezt.other_schema_another_table', origin_table='other_schema.another_table'),
        mocker.call(new_table='tezt.some_schema_some_table', origin_table='some_schema.some_table'),
        mocker.call(new_table='tezt.some_schema_some_table_expected', origin_table='some_schema.some_table'),
    ]

    assert query_runner.fill_table_from_csv.mock_calls == [
        mocker.call(
            table_name='tezt.other_schema_other_table',
            csv_filename=csv_path(
                'results_the_same_and_debug_true__no_exception_raised/other_schema_other_table.csv'
            )
        ),
        mocker.call(
            table_name='tezt.other_schema_another_table',
            csv_filename=csv_path(
                'results_the_same_and_debug_true__no_exception_raised/other_schema_another_table.csv'
            )
        ),
        mocker.call(
            table_name='tezt.some_schema_some_table_expected',
            csv_filename=csv_path(
                'results_the_same_and_debug_true__no_exception_raised/some_schema_some_table.csv'
            )
        ),
    ]

    query_runner.add_column.assert_called_once_with(
        table_name='tezt.some_schema_some_table_expected',
        column_name='test_case_comment',
    )

    query_runner.execute.assert_called_once_with(
        query=read_sql_file(
            'results_the_same_and_debug_true__no_exception_raised/query_patched.sql'
        )
    )

    assert query_runner.read_table.mock_calls == [
        mocker.call(table_name='tezt.some_schema_some_table'),
        mocker.call(table_name='tezt.some_schema_some_table_expected'),
    ]

def test_run_test_query__results_the_same_and_debug_true_several_statements__no_exception_raised(mocker, query_runner: QueryRunner):
    # arrange
    query_runner.read_table.side_effect = [
        pd.read_csv(csv_path('results_the_same_and_debug_true_several_statements__no_exception_raised/some_schema_some_table.csv')),
        pd.read_csv(csv_path('results_the_same_and_debug_true_several_statements__no_exception_raised/some_schema_some_table.csv'))
    ]

    # act
    run_test_query(
        runner=query_runner,
        test_schema='tezt',
        tables={
            'other_schema.other_table': csv_path(
                'results_the_same_and_debug_true_several_statements__no_exception_raised/other_schema_other_table.csv'),
            'other_schema.another_table': csv_path(
                'results_the_same_and_debug_true_several_statements__no_exception_raised/other_schema_another_table.csv')
        },
        expected={
            'some_schema.some_table': csv_path(
                'results_the_same_and_debug_true_several_statements__no_exception_raised/some_schema_some_table.csv')
        },
        query=read_sql_file('results_the_same_and_debug_true_several_statements__no_exception_raised/query.sql'),
        debug=True
    )

    # assert
    query_runner.set_debug.assert_called_once_with(debug=True)

    assert query_runner.drop_table_if_exists.mock_calls == [
        mocker.call(table_name='tezt.other_schema_another_table'),
        mocker.call(table_name='tezt.other_schema_other_table'),
        mocker.call(table_name='tezt.some_schema_some_table'),
        mocker.call(table_name='tezt.some_schema_some_table_expected')
    ]

    assert query_runner.create_table_like.mock_calls == [
        mocker.call(new_table='tezt.other_schema_other_table', origin_table='other_schema.other_table'),
        mocker.call(new_table='tezt.other_schema_another_table', origin_table='other_schema.another_table'),
        mocker.call(new_table='tezt.some_schema_some_table', origin_table='some_schema.some_table'),
        mocker.call(new_table='tezt.some_schema_some_table_expected', origin_table='some_schema.some_table'),
    ]

    assert query_runner.fill_table_from_csv.mock_calls == [
        mocker.call(
            table_name='tezt.other_schema_other_table',
            csv_filename=csv_path(
                'results_the_same_and_debug_true_several_statements__no_exception_raised/other_schema_other_table.csv'
            )
        ),
        mocker.call(
            table_name='tezt.other_schema_another_table',
            csv_filename=csv_path(
                'results_the_same_and_debug_true_several_statements__no_exception_raised/other_schema_another_table.csv'
            )
        ),
        mocker.call(
            table_name='tezt.some_schema_some_table_expected',
            csv_filename=csv_path(
                'results_the_same_and_debug_true_several_statements__no_exception_raised/some_schema_some_table.csv'
            )
        ),
    ]

    query_runner.add_column.assert_called_once_with(
        table_name='tezt.some_schema_some_table_expected',
        column_name='test_case_comment',
    )

    assert query_runner.execute.mock_calls == [
        mocker.call(query='SET some_var = some_var'),
        mocker.call(query='ADD SOMETHING'),
        mocker.call(query='INSERT OVERWRITE TABLE tezt.some_schema_some_table PARTITION (field4=2) SELECT a.field1 FROM tezt.other_schema_other_table a'),
    ]
    assert query_runner.read_table.mock_calls == [
        mocker.call(table_name='tezt.some_schema_some_table'),
        mocker.call(table_name='tezt.some_schema_some_table_expected'),
    ]


def test_run_test_query__results_different_and_debug_true__exception_raised(mocker, query_runner: QueryRunner):
    # arrange
    query_runner.read_table.side_effect = [
        pd.read_csv(csv_path('results_the_same_and_debug_true__exception_raised/some_schema_some_table_actual.csv')),
        pd.read_csv(csv_path('results_the_same_and_debug_true__exception_raised/some_schema_some_table_expected.csv')),
    ]

    # act
    with pytest.raises(AssertionError):
        run_test_query(
            runner=query_runner,
            test_schema='tezt',
            tables={
                'other_schema.other_table': csv_path(
                    'results_the_same_and_debug_true__exception_raised/other_schema_other_table.csv'),
                'other_schema.another_table': csv_path(
                    'results_the_same_and_debug_true__exception_raised/other_schema_another_table.csv')
            },
            expected={
                'some_schema.some_table': csv_path(
                    'results_the_same_and_debug_true__exception_raised/some_schema_some_table_expected.csv')
            },
            query=read_sql_file('results_the_same_and_debug_true__exception_raised/query.sql'),
            debug=True
        )

    # assert
    query_runner.set_debug.assert_called_once_with(debug=True)

    assert query_runner.drop_table_if_exists.mock_calls == [
        mocker.call(table_name='tezt.other_schema_another_table'),
        mocker.call(table_name='tezt.other_schema_other_table'),
        mocker.call(table_name='tezt.some_schema_some_table'),
        mocker.call(table_name='tezt.some_schema_some_table_expected')
    ]

    assert query_runner.create_table_like.mock_calls == [
        mocker.call(new_table='tezt.other_schema_other_table', origin_table='other_schema.other_table'),
        mocker.call(new_table='tezt.other_schema_another_table', origin_table='other_schema.another_table'),
        mocker.call(new_table='tezt.some_schema_some_table', origin_table='some_schema.some_table'),
        mocker.call(new_table='tezt.some_schema_some_table_expected', origin_table='some_schema.some_table'),
    ]

    assert query_runner.fill_table_from_csv.mock_calls == [
        mocker.call(
            table_name='tezt.other_schema_other_table',
            csv_filename=csv_path(
                'results_the_same_and_debug_true__exception_raised/other_schema_other_table.csv'
            )
        ),
        mocker.call(
            table_name='tezt.other_schema_another_table',
            csv_filename=csv_path(
                'results_the_same_and_debug_true__exception_raised/other_schema_another_table.csv'
            )
        ),
        mocker.call(
            table_name='tezt.some_schema_some_table_expected',
            csv_filename=csv_path(
                'results_the_same_and_debug_true__exception_raised/some_schema_some_table_expected.csv'
            )
        ),
    ]

    query_runner.add_column.assert_called_once_with(
        table_name='tezt.some_schema_some_table_expected',
        column_name='test_case_comment',
    )

    query_runner.execute.assert_called_once_with(
        query=read_sql_file(
            'results_the_same_and_debug_true__exception_raised/query_patched.sql'
        )
    )

    assert query_runner.read_table.mock_calls == [
        mocker.call(table_name='tezt.some_schema_some_table'),
        mocker.call(table_name='tezt.some_schema_some_table_expected'),
    ]
