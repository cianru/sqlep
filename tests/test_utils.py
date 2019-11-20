from sqlep.utils import _patch_query


def test__patch_query__create_table():
    # arrange
    query = '''
    CREATE TABLE IF NOT EXISTS sch.tbl(
    a int);
    '''
    expected_query = '''
    CREATE TABLE IF NOT EXISTS tezt.sch_tbl(
    a int);
    '''

    # act
    patched_query = _patch_query(query=query, test_schema='tezt')

    # assert
    assert expected_query == patched_query


def test__patch_query__drop_table():
    # arrange
    query = '''
    DROP TABLE sch.tbl;
    '''
    expected_query = '''
    DROP TABLE tezt.sch_tbl;
    '''

    # act
    patched_query = _patch_query(query=query, test_schema='tezt')

    # assert
    assert expected_query == patched_query
