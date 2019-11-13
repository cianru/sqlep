READ_CSV_KWARGS = {
    'dtype': 'str',
    'quotechar': '\'',
    'keep_default_na': False,
    'encoding': 'utf8',
}
HIVE_STRING_TIME_DATA_TYPES = [  # todo
    'timestamp',
    'date',
    'interval',
    'char',
    'string',
    'varchar',
]
COMMENT_COLUMN = 'test_case_comment'
MERGE_COLUMN = '__merge'
ACTUAL_MERGE_COLUMN = MERGE_COLUMN + '_actual'
EXPECTED_MERGE_COLUMN = MERGE_COLUMN + '_expected'
SEP_LENGTH = 40
MAIN_SEP = '\n' + '#' * SEP_LENGTH + '\n'
ROW_SEP = '\n' + '-' * SEP_LENGTH + '\n'
PREFIX_SEP = '\n' + '=' * SEP_LENGTH + '\n'
COMMENT_SEP = '\n' + '.' * SEP_LENGTH + '\n'
ACTUAL_ERROR_PREFIX = 'Actual rows that are different:' + PREFIX_SEP
ASSERT_PREFIX = 'Tables are different:' + MAIN_SEP
EXPECTED_ERROR_PREFIX = 'Expected rows that are different:' + PREFIX_SEP
