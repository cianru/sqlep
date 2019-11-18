from collections import OrderedDict
from typing import Optional, Any, Dict

import pandas as pd
from pyhive import hive
from pyhive.hive import Connection

from sqlep.settings import READ_CSV_KWARGS
from sqlep.runners.query_runner import QueryRunner

HIVE_STRING_TIME_DATA_TYPES = (
    'timestamp',
    'date',
    'interval',
    'char',
    'string',
    'varchar',
)


def _format_value(column_type: str, value: Any) -> str:
    if value == 'NULL':
        if column_type.startswith('array'):
            return 'array()'
        if column_type.startswith('map'):
            return 'map()'
        return value

    if column_type == 'boolean':
        return str(value).lower()

    if any(column_type.startswith(col) for col in HIVE_STRING_TIME_DATA_TYPES):
        return u'\'{}\''.format(value)

    if column_type.startswith('array'):
        return u'array({})'.format(value)

    if column_type.startswith('map'):
        return u'map({})'.format(value)

    return str(value)


def _get_projection(*, df: pd.DataFrame, part_names, info: Dict[str, Dict[str, Any]], test_schema: str) -> str:
    selects = []

    for _, row in df.iterrows():
        columns = []
        for col in info.keys():
            if col not in part_names:
                value = row[col] if col in row else 'NULL'
                columns.append(_format_value(info[col]['type'], value))

        selects.append(u'SELECT {} FROM {}.dummy'.format(
            ', '.join(columns),
            test_schema
        ))

    return ' UNION ALL '.join(selects)


class HiveRunner(QueryRunner):
    _drop_table_if_exists_template = 'DROP TABLE IF EXISTS {table_name}'
    _create_table_like_template = 'CREATE TABLE IF NOT EXISTS {new_table} LIKE {origin_table}'
    _add_column_template = 'ALTER TABLE {table_name} ADD COLUMNS (`{column_name}` {column_type})'

    def connect(self, *args, **kwargs) -> Connection:
        return hive.connect(*args, **kwargs)

    def _get_table_info(self, *, table_name: str):
        result = OrderedDict()
        flag = False

        table_description = self.execute(
            query=f'DESC {table_name}',
            fetch=True
        )

        for colname, datatype, _ in table_description:
            if not colname:
                continue
            elif colname.startswith("#"):
                flag = True
            elif flag:
                result[colname]['is_partition'] = True
            else:
                result[colname] = {
                    'type': datatype,
                    'is_partition': False
                }

        return result

    def fill_table_from_csv(self, *, table_name: str, csv_filename: str) -> None:
        schema = table_name.split('.')[0]
        info = self._get_table_info(table_name=table_name)
        part_names = list(filter(lambda k: info[k]['is_partition'], info.keys()))
        df = pd.read_csv(csv_filename, **READ_CSV_KWARGS)
        if part_names:
            for parts, rows in df.groupby(part_names):

                if not isinstance(parts, tuple):
                    parts = (parts,)

                parts_ = []

                for name, value in zip(part_names, parts):
                    parts_.append('`{}`={}'.format(name, _format_value(info[name]['type'], value)))
                query = u'INSERT INTO TABLE {} PARTITION ({}) {}'.format(
                    table_name,
                    ', '.join(parts_),
                    _get_projection(df=rows, part_names=part_names, info=info, test_schema=schema)
                )
                self.execute(query=query)

        else:
            query = u'INSERT INTO TABLE {} {}'.format(
                table_name,
                _get_projection(df=df, part_names=part_names, info=info, test_schema=schema)
            )
            self.execute(query=query)

    def _execute(self, *, query: str, fetch: bool = False, convert_to_pandas=False) -> Optional[pd.DataFrame]:
        with self._connection.cursor() as cursor:
            cursor.execute(query)
            if fetch:
                fetched = cursor.fetchall()
                if convert_to_pandas:
                    return pd.DataFrame(
                        fetched,
                        columns=[t[0].split('.')[-1] for t in cursor.description]
                    )
                else:
                    return fetched
