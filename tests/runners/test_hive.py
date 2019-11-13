import pandas as pd

from sqlep import run_test_query


def test_runner_connect_to_hive(hive, hive_cursor, hive_runner):
    # arrange & act
    run_test_query(
        query='',
        tables=dict(),
        expected=dict(),
        test_schema='t',
        runner=hive_runner,
    )

    # assert
    hive.connect.assert_called_once_with(
        host='somehost',
        username='anon',
        configuration={
            'tez.queue.name': 'default',
        }
    )
