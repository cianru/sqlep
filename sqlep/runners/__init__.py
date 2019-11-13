import abc
from typing import Any, Dict

import pandas


class QueryRunner(metaclass=abc.ABCMeta):
    def __init__(self, config: Dict[str, Any], debug: bool):
        self.config = config
        self.debug = debug

    def set_debug(self, *, debug: bool):
        self.debug = debug

    @abc.abstractmethod
    def execute(self, *, query: str) -> None:
        pass

    @abc.abstractmethod
    def drop_table_if_exists(self, *, table: str) -> None:
        pass

    @abc.abstractmethod
    def create_table_like(self, *, new_table: str, origin_table: str) -> None:
        pass

    @abc.abstractmethod
    def fill_table_from_csv(self, *, table: str, csv_filename: str) -> None:
        pass

    @abc.abstractmethod
    def add_column(self, *, table: str, column_name: str, column_type: str):
        pass

    @abc.abstractmethod
    def read_table(self, *, table_name: str) -> pandas.DataFrame:
        pass
