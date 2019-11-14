import pandas as pd
from io import StringIO

import pytest

from sqlep import run_test_query
from sqlep.settings import READ_CSV_KWARGS
from tests.utils import csv_path, is_subseq


def test_runner_connect_to_hive(hive, hive_runner):
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


def test_multiple_table_queries(mocker, hive_cursor, hive_runner):
    # arrange

    df_test_data = [(str(i), str(i)) for i in range(2)]

    hive_cursor.fetchall.side_effect = [
        [('field1', 'string', ''), ('field2', 'string', '')],
        [('field1', 'string', ''), ('field2', 'string', '')],
        [('field1', 'string', ''), ('field2', 'string', '')],
        [('field1', 'string', ''), ('field2', 'string', '')],
        df_test_data,
        df_test_data,
        df_test_data,
        df_test_data,
    ]
    hive_cursor.description = [('schema_table1.field1',), ('schema_table1.field2',)]
    mocker.patch(
        'sqlep.runners.hive.pd.read_csv',
        side_effect=[
            pd.DataFrame(df_test_data, columns=['field1', 'field2']),
            pd.DataFrame(df_test_data, columns=['field1', 'field2']),
            pd.DataFrame(df_test_data, columns=['field1', 'field2']),
            pd.DataFrame(df_test_data, columns=['field1', 'field2']),
        ]
    )

    # act
    run_test_query(
        query='select 1',
        tables={'schema.table1': 'table1.csv', 'schema.table2': 'table2.csv'},
        expected={'schema.expected1': 'expected1.csv', 'schema.expected2': 'expected2.csv'},
        runner=hive_runner,
        test_schema='tezt'
    )

    # assert
    def assert_is_subseq(l):
        assert is_subseq(map(mocker.call, l), hive_cursor.execute.mock_calls)

    # schema.table1
    assert_is_subseq([
        'DROP TABLE IF EXISTS tezt.schema_table1',
        'CREATE TABLE IF NOT EXISTS tezt.schema_table1 LIKE schema.table1',
        'select 1',
        'SELECT * FROM tezt.schema_expected1',
        'DROP TABLE IF EXISTS tezt.schema_table1',
    ])

    # schema.table2
    assert_is_subseq([
        'DROP TABLE IF EXISTS tezt.schema_table2',
        'CREATE TABLE IF NOT EXISTS tezt.schema_table2 LIKE schema.table2',
        'select 1',
        'SELECT * FROM tezt.schema_expected2',
        'DROP TABLE IF EXISTS tezt.schema_table2',
    ])

    # schema.expected1
    assert_is_subseq([
        'DROP TABLE IF EXISTS tezt.schema_expected1',
        'CREATE TABLE IF NOT EXISTS tezt.schema_expected1 LIKE schema.expected1',
        'select 1',
        'SELECT * FROM tezt.schema_expected1',
        'DROP TABLE IF EXISTS tezt.schema_expected1',
    ])

    # schema.expected1_expected
    assert_is_subseq([
        'DROP TABLE IF EXISTS tezt.schema_expected1_expected',
        'CREATE TABLE IF NOT EXISTS tezt.schema_expected1_expected LIKE schema.expected1',
        'ALTER TABLE tezt.schema_expected1_expected ADD COLUMNS (`test_case_comment` STRING)',
        'DESC tezt.schema_expected1_expected',
        'INSERT INTO TABLE tezt.schema_expected1_expected SELECT \'0\', \'0\' FROM tezt.dummy ' +
        'UNION ALL SELECT \'1\', \'1\' FROM tezt.dummy',
        'select 1',
        'SELECT * FROM tezt.schema_expected1_expected',
        'DROP TABLE IF EXISTS tezt.schema_expected1_expected',
    ])

    # schema.expected2
    assert_is_subseq([
        'DROP TABLE IF EXISTS tezt.schema_expected2',
        'CREATE TABLE IF NOT EXISTS tezt.schema_expected2 LIKE schema.expected2',
        'select 1',
        'SELECT * FROM tezt.schema_expected2',
        'DROP TABLE IF EXISTS tezt.schema_expected2',
    ])

    # schema.expected2_expected
    assert_is_subseq([
        'DROP TABLE IF EXISTS tezt.schema_expected2_expected',
        'CREATE TABLE IF NOT EXISTS tezt.schema_expected2_expected LIKE schema.expected2',
        'ALTER TABLE tezt.schema_expected2_expected ADD COLUMNS (`test_case_comment` STRING)',
        'DESC tezt.schema_expected2_expected',
        'INSERT INTO TABLE tezt.schema_expected2_expected SELECT \'0\', \'0\' FROM tezt.dummy ' +
        'UNION ALL SELECT \'1\', \'1\' FROM tezt.dummy',
        'select 1',
        'SELECT * FROM tezt.schema_expected2_expected',
        'DROP TABLE IF EXISTS tezt.schema_expected2_expected',
    ])


def test_source_result_same_queries(mocker, hive_cursor, hive_runner):
    # arrange
    df_test_data = [(str(i), str(i)) for i in range(2)]

    hive_cursor.fetchall.side_effect = [
        [('field1', 'string', ''), ('field2', 'string', '')],
        [('field1', 'string', ''), ('field2', 'string', '')],
        df_test_data,
        df_test_data,
    ]
    hive_cursor.description = [('schema.field1',), ('schema.field2',), ]
    mocker.patch(
        'sqlep.runners.hive.pd.read_csv',
        side_effect=[
            pd.DataFrame(df_test_data, columns=['field1', 'field2']),
            pd.DataFrame(df_test_data, columns=['field1', 'field2']),
        ]
    )

    # act
    run_test_query(
        query='select 1',
        tables={'schema.table': 'table.csv'},
        expected={'schema.table': 'expected.csv'},
        runner=hive_runner,
        test_schema='tezt'
    )

    # assert
    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table'),
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table_expected'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.schema_table LIKE schema.table'),
        mocker.call('DESC tezt.schema_table'),
        mocker.call("INSERT INTO TABLE tezt.schema_table SELECT '0', '0' "
                    "FROM tezt.dummy UNION ALL SELECT '1', '1' FROM tezt.dummy"),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.schema_table LIKE schema.table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.schema_table_expected LIKE schema.table'),
        mocker.call('ALTER TABLE tezt.schema_table_expected ADD COLUMNS (`test_case_comment` STRING)'),
        mocker.call('DESC tezt.schema_table_expected'),
        mocker.call('INSERT INTO TABLE tezt.schema_table_expected SELECT \'0\', \'0\' FROM tezt.dummy ' +
                    'UNION ALL SELECT \'1\', \'1\' FROM tezt.dummy'),
        mocker.call('select 1'),
        mocker.call('SELECT * FROM tezt.schema_table'),
        mocker.call('SELECT * FROM tezt.schema_table_expected'),
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table'),
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table_expected'),
    ]


def test_partitioned_table_queries(mocker, hive_runner, hive_cursor):
    # arrange
    hive_cursor.fetchall.return_value = [
        ('field1', 'int', ''),
        ('field2', 'string', ''),
        ('# Partition Information', None, None),
        ('# col_name', None, None),
        ('field2', 'string', ''),
    ]
    mocker.patch(
        'sqlep.runners.hive.pd.read_csv',
        return_value=pd.DataFrame(dict(field1=range(4), field2=list(map(str, [0, 0, 1, 1]))))
    )

    # act
    run_test_query(
        query='select 1',
        tables={'schema.table': 'table.csv'},
        expected=dict(),
        runner=hive_runner,
        test_schema='tezt',
    )

    # assert
    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.schema_table LIKE schema.table'),
        mocker.call('DESC tezt.schema_table'),
        mocker.call('INSERT INTO TABLE tezt.schema_table PARTITION (`field2`=\'0\') SELECT 0 ' +
                    'FROM tezt.dummy UNION ALL SELECT 1 FROM tezt.dummy'),
        mocker.call('INSERT INTO TABLE tezt.schema_table PARTITION (`field2`=\'1\') SELECT 2 ' +
                    'FROM tezt.dummy UNION ALL SELECT 3 FROM tezt.dummy'),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table'),
    ]


# fixme
@pytest.mark.parametrize('field_type, csv_line, projection', [
    ('array<string>', '\'"1","2","3"\'', 'array("1","2","3")'),
    ('array<string>', '\'\'', 'array()'),
    ('boolean', 'false', 'false'),
    ('boolean', 'true', 'true'),
    ('int', '10', 10),
    ('double', '0.1', 0.1),
    ('string', 'text', '\'text\''),
    ('varchar', 'text', '\'text\''),
    ('varchar(50)', 'text', '\'text\''),
    ('map<varchar,varchar>', '\'"a","1","b","3"\'', 'map("a","1","b","3")')
])
def test_types_queries(mocker, hive_cursor, hive_runner, field_type, csv_line, projection):
    # arrange
    hive_cursor.fetchall.return_value = [
        ('field', field_type, ''),
    ]
    mocker.patch(
        'sqlep.runners.hive.pd.read_csv',
        return_value=pd.read_csv(
            StringIO(csv_line),
            names=['field'],
            **READ_CSV_KWARGS
        )
    )

    # act
    run_test_query(
        query='select 1',
        tables={'schema.table': 'table.csv'},
        expected=dict(),
        runner=hive_runner,
        test_schema='tezt'
    )

    # assert
    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.schema_table LIKE schema.table'),
        mocker.call('DESC tezt.schema_table'),
        mocker.call(f'INSERT INTO TABLE tezt.schema_table SELECT {projection} FROM tezt.dummy'),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table')
    ]


@pytest.mark.parametrize('partition_type, csv_line, part', [
    ('string', '1,1', '\'1\''),
    ('boolean', '1,false', 'false'),
    ('boolean', '1,true', 'true'),
    ('int', '1,1', '1'),
    ('date', '1,2019-01-01', '\'2019-01-01\''),
    ('string', '1,06', '\'06\'')
])
def test_partition_types_queries(mocker, hive_cursor, partition_type, csv_line, part, hive_runner):
    # arrange
    hive_cursor.fetchall.return_value = [
        ('field1', 'string', ''),
        ('field2', partition_type, ''),
        ('# Partition Information', None, None),
        ('# col_name', None, None),
        ('field2', partition_type, ''),
    ]
    mocker.patch(
        'sqlep.runners.hive.pd.read_csv',
        return_value=pd.read_csv(
            StringIO(csv_line),
            names=['field1', 'field2'],
            **READ_CSV_KWARGS
        )
    )

    # act
    run_test_query(
        query='select 1',
        tables={'schema.table': 'table.csv'},
        expected=dict(),
        runner=hive_runner,
        test_schema='tezt'
    )

    # assert
    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.schema_table LIKE schema.table'),
        mocker.call('DESC tezt.schema_table'),
        mocker.call(f'INSERT INTO TABLE tezt.schema_table PARTITION (`field2`={part}) SELECT \'1\' FROM tezt.dummy'),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.schema_table'),
    ]


def test_df_order(hive_cursor, hive_runner):
    # arrange
    hive_cursor.fetchall.side_effect = [
        [('a', 'string', ''), ('b', 'integer', '')],
        [(0, '0'), (1, '1'), (2, '2')],
        [(0, '0'), (2, '2'), (1, '1')],
    ]
    hive_cursor.description = [('a',), ('b',)]

    # act & assert
    run_test_query(
        query='select 1',
        tables=dict(),
        expected={'schema.expected': csv_path('test_order.csv')},
        runner=hive_runner,
        test_schema='tezt'
    )


def test_unicode_in_source_table(tmpdir, hive_cursor, mocker, hive_runner):
    # arrange
    hive_cursor.fetchall.side_effect = [
        [('field', 'string', '')],
        [(u'Юникод')],
    ]

    test_file = tmpdir.join('test.csv')
    test_file.write_binary(u'field\nЮникод'.encode('utf8'))

    # act
    run_test_query(
        query='select 1',
        tables={'source.table': test_file},
        expected={},
        runner=hive_runner,
        test_schema='tezt'
    )

    # assert
    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.source_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.source_table LIKE source.table'),
        mocker.call('DESC tezt.source_table'),
        mocker.call(u'INSERT INTO TABLE tezt.source_table SELECT \'\u042e\u043d\u0438\u043a\u043e\u0434\' ' +
                    'FROM tezt.dummy'),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.source_table'),
    ]


def test_unicode_in_source_table_partitioned(tmpdir, hive_cursor, mocker, hive_runner):
    # arrange
    hive_cursor.fetchall.side_effect = [
        [
            ('field1', 'string', ''),
            ('field2', 'int', ''),
            ('# Partition Information', None, None),
            ('# col_name', None, None),
            ('field2', 'int', ''),
        ],
        [(u'Юникод', 1)],
    ]

    test_file = tmpdir.join('test.csv')
    test_file.write_binary(u'field1,field2\nЮникод,1'.encode('utf8'))

    # act
    run_test_query(
        query='select 1',
        tables={'source.table': test_file},
        expected={},
        runner=hive_runner,
        test_schema='tezt'
    )

    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.source_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.source_table LIKE source.table'),
        mocker.call('DESC tezt.source_table'),
        mocker.call('INSERT INTO TABLE tezt.source_table PARTITION (`field2`=1) SELECT ' +
                    u'\'\u042e\u043d\u0438\u043a\u043e\u0434\' FROM tezt.dummy'),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.source_table')
    ]


def test_unicode_in_expected_table(tmpdir, hive_cursor, hive_runner):
    # arrange
    hive_cursor.fetchall.side_effect = [
        [('a', 'string', ''), ('b', 'int', '')],
        [(u'Юникод', 1)],
        [(u'Юникод', 1)],
    ]
    hive_cursor.description = [('a',), ('b',)]

    test_file = tmpdir.join('test_csv')
    test_file.write(u'a,b\nЮникод,1'.encode('utf8'), mode='wb')

    # act & assert
    run_test_query(
        query='select 1',
        tables={},
        expected={'expected.table': test_file},
        runner=hive_runner,
        test_schema='tezt'
    )


@pytest.mark.parametrize('field_type', ['int', 'string', 'date', 'timestamp', 'interval', 'bigint', 'decimal',
                                        'double', 'float'])
def test_write_default_values(mocker, tmpdir, hive_cursor, field_type, hive_runner):
    # arrange
    hive_cursor.fetchall.return_value = [
        ('field1', 'int', ''),
        ('field2', field_type, ''),
        ('field3', 'string', '')
    ]

    test_file = tmpdir.join('test.csv')
    test_file.write('field1,field3\n1,string')

    # act
    run_test_query(
        query='select 1',
        expected={},
        tables={'expected.table': test_file},
        runner=hive_runner,
        test_schema='tezt'
    )

    # assert
    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.expected_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.expected_table LIKE expected.table'),
        mocker.call('DESC tezt.expected_table'),
        mocker.call('INSERT INTO TABLE tezt.expected_table SELECT 1, NULL, \'string\' FROM tezt.dummy'),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.expected_table')
    ]


@pytest.mark.parametrize('field_type, csv_line, projection1, projection2', [
    ('array<string>', '1,\'""\'\n2,\'"1","2","3"\'', '1, array("")', '2, array("1","2","3")'),
    ('array<string>', '1,\'\'\n2,\'"1","2","3"\'', '1, array()', '2, array("1","2","3")'),
    ('string', '1,NULL\n2,\'string\'', '1, NULL', '2, \'string\''),
    ('int', '1,NULL\n2,8', '1, NULL', '2, 8'),
    ('double', '1,NULL\n2,1.598', '1, NULL', '2, 1.598'),
    ('date', '1,NULL\n2,\'2019-01-01\'', '1, NULL', '2, \'2019-01-01\''),
    ('boolean', '1,NULL\n2,true', '1, NULL', '2, true'),
    ('map<varchar,varchar>', '1,\'\'\n2,\'"1","2"\'', '1, map()', '2, map("1","2")'),
    ('map<varchar,varchar>', '1,NULL\n2,\'"1","2"\'', '1, map()', '2, map("1","2")')
])
def test_write_null_values_in_expected(mocker, tmpdir, hive_cursor, field_type, csv_line, projection1, projection2,
                                       hive_runner):
    # arrange
    hive_cursor.fetchall.return_value = [
        ('field1', 'int', ''),
        ('field2', field_type, '')
    ]

    test_file = tmpdir.join('test.csv')
    test_file.write('field1,field2\n{}'.format(csv_line))

    # act
    run_test_query(
        query='select 1',
        tables={'expected.table': test_file},
        expected=dict(),
        test_schema='tezt',
        runner=hive_runner,
    )

    # assert
    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.expected_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.expected_table LIKE expected.table'),
        mocker.call('DESC tezt.expected_table'),
        mocker.call('INSERT INTO TABLE tezt.expected_table SELECT {} FROM tezt.dummy '
                    'UNION ALL SELECT {} FROM tezt.dummy'.format(projection1, projection2)),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.expected_table')
    ]


@pytest.mark.parametrize('field_type, csv_line, projection1, projection2', [
    ('array<string>', '1,\'""\'\n2,\'"1","2","3"\'', '1, array("")', '2, array("1","2","3")'),
    ('array<string>', '1,\'\'\n2,\'"1","2","3"\'', '1, array()', '2, array("1","2","3")'),
    ('string', '1,NULL\n2,\'string\'', '1, NULL', '2, \'string\''),
    ('int', '1,NULL\n2,8', '1, NULL', '2, 8'),
    ('double', '1,NULL\n2,1.598', '1, NULL', '2, 1.598'),
    ('date', '1,NULL\n2,\'2019-01-01\'', '1, NULL', '2, \'2019-01-01\''),
    ('boolean', '1,NULL\n2,true', '1, NULL', '2, true'),
])
def test_write_null_values_in_source(mocker, tmpdir, hive_cursor, field_type, csv_line, projection1, projection2,
                                     hive_runner):
    # arrange
    hive_cursor.fetchall.return_value = [
        ('field1', 'int', ''),
        ('field2', field_type, '')
    ]

    test_file = tmpdir.join('test.csv')
    test_file.write('field1,field2\n{}'.format(csv_line))

    # act
    run_test_query(
        query='select 1',
        tables={'source.table': test_file},
        expected=dict(),
        test_schema='tezt',
        runner=hive_runner,
    )

    # assert
    assert hive_cursor.execute.mock_calls == [
        mocker.call('DROP TABLE IF EXISTS tezt.source_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.source_table LIKE source.table'),
        mocker.call('DESC tezt.source_table'),
        mocker.call('INSERT INTO TABLE tezt.source_table SELECT {} FROM tezt.dummy '
                    'UNION ALL SELECT {} FROM tezt.dummy'.format(projection1, projection2)),
        mocker.call('select 1'),
        mocker.call('DROP TABLE IF EXISTS tezt.source_table')
    ]


def test_unicode_in_array(mocker, tmpdir, hive_cursor, hive_runner):
    # arrange
    hive_cursor.fetchall.return_value = [('field1', 'array<string>', '')]

    test_file = tmpdir.join('test.csv')
    test_file.write(u'field1\n\'"Юникод1","Юникод2"\''.encode('utf8'), mode='wb')

    calls = [
        mocker.call('DROP TABLE IF EXISTS tezt.source_table'),
        mocker.call('CREATE TABLE IF NOT EXISTS tezt.source_table LIKE source.table'),
        mocker.call('DESC tezt.source_table'),
        mocker.call(
            u'INSERT INTO TABLE tezt.source_table SELECT '
            u'array("\u042e\u043d\u0438\u043a\u043e\u04341","\u042e\u043d\u0438\u043a\u043e\u04342") FROM tezt.dummy'
        ),
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
        mocker.call(
            u'INSERT INTO TABLE tezt.source_table SELECT map("key1","\u042e\u043d\u0438\u043a\u043e\u04341","key2","\u042e\u043d\u0438\u043a\u043e\u04342") FROM tezt.dummy'),
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
