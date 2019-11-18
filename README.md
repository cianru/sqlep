# SQLEP - a tool for testing SQL-queries


```python
from sqlep import run_test_query
from sqlep.runners import HiveRunner

hive_runner = HiveRunner(
        config={
            'host': 'localhost',
            'username': 'anonymous',
            'configuration': {
                'tez.queue.name': 'default',
            }
        }
)


run_test_query(
    # query for testing
    query='insert overwrite table schema.table2 select * from schema.table1',
    # csv for mocking source tables 
    tables={'schema.table1': 'table1.csv'},
    # csv for expected results 
    expected={'schema.table2': 'table2.csv'},
    # setup engine for running queries
    runner=hive_runner,
    # schema for mock data and computing queries 
    test_schema='tezt'
)
```