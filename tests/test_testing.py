import pandas as pd

from sqlep.testing import run_test_query
from tests.utils import read_sql_file, csv_path


def test_test_query__a__(query_runner):
    # arrange
    query_runner.read_table.side_effect = [
        pd.read_csv(csv_path('some_schema_some_table.csv')),
        pd.read_csv(csv_path('some_schema_some_table.csv'))
    ]

    # act
    run_test_query(
        runner=query_runner,
        test_schema='tezt',
        tables={
            'other_schema.other_table': 'other_schema_other_table.csv',
            'other_schema.another_table': 'other_schema_another_table.csv'
        },
        expected={
            'some_schema.some_table': 'some_schema_some_table.csv'
        },
        query=read_sql_file('query.sql')
    )

    # assert
    query_runner.execute.assert_called_once_with(
        query=read_sql_file('query_patched.sql')
    )
