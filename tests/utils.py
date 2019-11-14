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


if __name__ == '__main__':
    print(is_subseq([1,2,3], [2,3,4]))
    print(is_subseq([1,2,3], [2,3,4]))
    print(is_subseq([1,3], [2,3,4]))
    print(is_subseq([2, 3], [2, 3, 4]))
    print(is_subseq([2, 4], [2, 3, 4]))
    print(is_subseq([3, 2], [2, 3, 4]))
