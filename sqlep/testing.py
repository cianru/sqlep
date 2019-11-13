import logging
from typing import Dict

from sqlep.config import (
    COMMENT_COLUMN,
)
from sqlep.runners import QueryRunner

from sqlep.utils import (
    _get_test_table,
    _get_expected_table,
    _patch_query,
    _get_actual_and_expected_difference,
    _raise_exception,
    _cleanup,
)


def run_test_query(
        *,
        query: str,
        runner: QueryRunner,
        tables: Dict[str, str],
        expected: Dict[str, str],
        test_schema: str,
        debug: bool = False
):
    runner.set_debug(debug)

    def cleanup():
        _cleanup(runner=runner, tables=tables, expected=expected, test_schema=test_schema)

    _query = _patch_query(query=query, test_schema=test_schema)

    cleanup()

    for table, csv_filename in tables.items():
        target_table = _get_test_table(table=table, test_schema=test_schema)

        runner.create_table_like(
            new_table=target_table,
            origin_table=table,
        )

        runner.fill_table_from_csv(
            table=target_table,
            csv_filename=csv_filename,
        )

    for table, csv_filename in expected.items():
        runner.create_table_like(
            new_table=_get_test_table(table=table, test_schema=test_schema),
            origin_table=table,
        )

        target_table = _get_expected_table(table=table, test_schema=test_schema)

        runner.create_table_like(
            new_table=target_table,
            origin_table=table,
        )
        runner.add_column(
            table=target_table,
            column_name=COMMENT_COLUMN,
            column_type='STRING'  # TODO: in some db there'no string
        )

        runner.fill_table_from_csv(
            table=target_table,
            csv_filename=csv_filename
        )

    if debug:
        logging.info(query)

    runner.execute(query=_query)

    actual_df, expected_df = _get_actual_and_expected_difference(
        runner=runner,
        expected=expected,
        test_schema=test_schema,
    )

    if not debug:
        cleanup()

    _raise_exception(actual_df=actual_df, expected_df=expected_df)
