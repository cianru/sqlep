import os
from typing import List, Any


def read_sql_file(filename):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sql', filename)

    with open(path, 'r') as f:
        return f.read()


def csv_path(filename):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'csv', filename)


def is_subseq(x, y):
    """
   https://stackoverflow.com/questions/24017363/how-to-test-if-one-string-is-a-subsequence-of-another
   """
    it = iter(y)
    return all(any(c == ch for c in it) for ch in x)
