import pandas as pd

from sqlep import run_test_query


def test_runner_connect_to_hive(hive, hive_cursor, hive_runner):
    # arrange & act
    run_test_query(
        query='',
        tables=dict(),
        expected=dict(),
        test_schema='',
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


def test_unicode_in_map(mocker, tmpdir, hive_cursor, hive_runner):
    # arrange

    hive_cursor.fetchall.return_value = [('field1', 'map<string,string>', '')]
    hive_cursor.description.side_effect = ['a', 'b', 'c']

    test_file = tmpdir.join('test.csv')
    test_file.write(u'field1\n\'"key1","Юникод1","key2","Юникод2"\''.encode('utf8'), mode='wb')

    calls = [
        mocker.call('DROP TABLE IF EXISTS tezt.source_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.source_table LIKE source.table'),
        mocker.call('DESC tezt.source_table'),
        mocker.call(u'INSERT INTO TABLE tezt.source_table SELECT map("key1","\u042e\u043d\u0438\u043a\u043e\u04341","key2","\u042e\u043d\u0438\u043a\u043e\u04342") FROM tezt.dummy'),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.source_table')
    ]

    # act
    run_test_query(
        query='select 1',
        tables={'source.table': test_file},
        expected=dict(),
        test_schema='tezt',
        runner=hive_runner,
    )

    # assert
    assert hive_cursor.execute.mock_calls == calls
