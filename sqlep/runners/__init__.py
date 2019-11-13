import abc
import logging
from typing import Dict, Any, Callable, Optional

import pandas as pd


class QueryRunner:
    _read_table_template: str = 'SELECT * FROM {table_name}'

    def __init__(self, config: Dict[str, Any], debug: bool = False):
        self.debug = debug
        self._connection = self.connect(**config)

    @property
    @abc.abstractmethod
    def _drop_table_if_exists_template(self):
        pass

    @property
    @abc.abstractmethod
    def _create_table_like_template(self):
        pass

    @property
    @abc.abstractmethod
    def _add_column_template(self):
        pass

    def drop_table_if_exists(self, table_name: str) -> None:
        self.execute(
            query=self._drop_table_if_exists_template.format(
                table_name=table_name
            )
        )

    def read_table(self, table_name: str) -> pd.DataFrame:
        return self.execute(
            query=self._read_table_template.format(table_name=table_name),
            fetch=True,
            convert_to_pandas=True,
        )

    def create_table_like(self, new_table: str, origin_table: str) -> None:
        self.execute(
            query=self._create_table_like_template.format(
                new_table=new_table,
                origin_table=origin_table
            )
        )

    # TODO: in some db there'no string
    def add_column(self, table_name: str, column_name: str, column_type: str = 'STRING') -> None:
        self.execute(
            query=self._add_column_template.format(
                table_name=table_name,
                column_name=column_name,
                column_type=column_type
            )
        )

    @abc.abstractmethod
    def connect(self, *args, **kwargs) -> Any:
        pass

    def set_debug(self, *, debug: bool) -> None:
        self.debug = debug

    @abc.abstractmethod
    def fill_table_from_csv(self, *, table_name: str, csv_filename: str) -> None:
        pass

    @abc.abstractmethod
    def _execute(self, *, query: str, fetch: bool = False, convert_to_pandas=False):
        pass

    def execute(self, *, query: str, fetch: bool = False, convert_to_pandas=False) -> Optional[pd.DataFrame]:
        if self.debug:
            logging.info(query)
        return self._execute(query=query, fetch=fetch, convert_to_pandas=convert_to_pandas)
