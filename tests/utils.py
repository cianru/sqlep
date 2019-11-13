import os


def read_sql_file(filename):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sql', filename)

    with open(path, 'r') as f:
        return f.read()


def csv_path(filename):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'csv', filename)
