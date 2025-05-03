import pandas as pd
from sqlalchemy import create_engine


def read_sql(database: str, table: str, use_dtype=False, db_type='sqlite', query=None):
    dtype = None

    engine = create_engine('sqlite:///{}.db'.format(database), echo=False)

    sql = query if query else 'SELECT * FROM {}'.format(table)
    if use_dtype:
        dtype = {'NationalCode': str, 'Interest': str}

    file = pd.read_sql_query(sql=sql, con=engine, dtype=dtype)
    return file


class BColors:
    purple = '\033[95m'
    orange = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    UNDERLINE = '\033[4m'


def cprint(string, color: str):
    color_dict = {'c': BColors.cyan, 'g': BColors.green, 'y': BColors.yellow, 'r': BColors.red, 'p': BColors.purple}
    try:
        print(f'{color_dict[color]}{string}{BColors.end}')
    except KeyError:
        cprint(f'"{color}" not in acceptable colors', 'r')