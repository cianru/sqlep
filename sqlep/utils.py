import re
from typing import Dict, Callable, List, Generator, Iterator

import pandas as pd
import numpy as np

from sqlep.settings import (
    ACTUAL_MERGE_COLUMN,
    EXPECTED_MERGE_COLUMN,
    MERGE_COLUMN,
    ASSERT_PREFIX,
    ACTUAL_ERROR_PREFIX,
    COMMENT_COLUMN,
    ROW_SEP,
    MAIN_SEP,
    EXPECTED_ERROR_PREFIX,
    COMMENT_SEP,
)
from sqlep.runners.query_runner import QueryRunner


def _get_test_table(*, table: str, test_schema: str) -> str:
    return '{}.{}'.format(test_schema, table.replace('.', '_'))


def _get_expected_table(*, table: str, test_schema: str) -> str:
    return _get_test_table(table=table, test_schema=test_schema) + '_expected'


def _patch_query(*, query: str, test_schema: str) -> str:
    replaces = set(re.findall(r'FROM\s+(\w+\.\w+)', query))
    replaces.update(re.findall(r'TABLE\s+(\w+\.\w+)', query))
    replaces.update(re.findall(r'JOIN\s+(\w+\.\w+)', query))

    result = query

    for s in replaces:
        result = result.replace(
            s, '{}.{}'.format(
                test_schema,
                s.replace('.', '_')
            )
        )

    return result


def _split_query(*, query: str) -> Iterator[str]:
    for q in query.split(';'):
        stripped = q.strip()
        if stripped:
            yield stripped


def _prepare_df(*, df: pd.DataFrame) -> pd.DataFrame:
    floating_columns = df.select_dtypes(np.floating).columns.tolist()
    df = df.round({col: 5 for col in floating_columns})
    df[MERGE_COLUMN] = 1
    return df


def _drop_df_columns(*, df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[ACTUAL_MERGE_COLUMN, EXPECTED_MERGE_COLUMN])


def _get_actual_and_expected_difference(
        *,
        runner: QueryRunner,
        expected: Dict[str, str],
        test_schema: str
) -> (pd.DataFrame, pd.DataFrame):
    actual_df = pd.DataFrame()
    expected_df = pd.DataFrame()

    def read_table(*, table_name: str, func: Callable[[str, str], str]) -> pd.DataFrame:
        return _prepare_df(
            df=runner.read_table(
                table_name=func(table=table_name, test_schema=test_schema)
            )
        )

    for table, csv_filename in expected.items():
        actual_df = read_table(table_name=table, func=_get_test_table)
        expected_df = read_table(table_name=table, func=_get_expected_table)

        on = [col for col in actual_df.columns.tolist() if col != MERGE_COLUMN]
        join = pd.merge(actual_df, expected_df, how='outer', on=on, suffixes=('_actual', '_expected'))
        expected_df = _drop_df_columns(df=join.loc[join[ACTUAL_MERGE_COLUMN].isnull(), :])
        actual_df = _drop_df_columns(df=join.loc[join[EXPECTED_MERGE_COLUMN].isnull(), :])

    return actual_df, expected_df


def _raise_exception(*, actual_df: pd.DataFrame, expected_df: pd.DataFrame) -> None:
    if not actual_df.empty or not expected_df.empty:
        msg = ASSERT_PREFIX

        msg += ACTUAL_ERROR_PREFIX
        for _, row in actual_df.iterrows():
            row.drop(labels=COMMENT_COLUMN, inplace=True)
            msg += str(row)
            msg += ROW_SEP

        msg += MAIN_SEP

        msg += EXPECTED_ERROR_PREFIX
        for _, row in expected_df.iterrows():
            comment = row.pop(COMMENT_COLUMN)
            msg += str(row)
            msg += COMMENT_SEP
            msg += comment or 'No comment'
            msg += ROW_SEP

        raise AssertionError(msg)


def _cleanup(*, runner: QueryRunner, tables: Dict[str, str], expected: Dict[str, str], test_schema: str) -> None:
    for name in sorted(set(tables) | set(expected)):
        runner.drop_table_if_exists(
            table_name=_get_test_table(table=name, test_schema=test_schema)
        )

    for name in expected:
        runner.drop_table_if_exists(
            table_name=_get_expected_table(table=name, test_schema=test_schema)
        )
