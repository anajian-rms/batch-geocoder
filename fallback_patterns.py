import sys
import pyodbc
import pandas as pd
import re
import json


CREDENTIALS = r'\config\credentials.json'
database_name = 'AIG_TEST_EDM'


def read_address_table(database):
    """
    This functions reads dbo.Address table from the EDM
    :param database: name of the EDM
    :return: pandas dataframe
    """
    with open(CREDENTIALS) as f:
        dbserver = json.load(f)
        connection_string = 'DRIVER='+dbserver["driver"]+';SERVER='+dbserver["server"]+';DATABASE='+database+';UID='+dbserver["username"]+';PWD='+dbserver["password"]
        query = 'SELECT * FROM [' + database + '].[dbo].[Address]'

    with pyodbc.connect(connection_string) as cnxn:
        cursor = cnxn.cursor()
        cursor.execute(query)

    return pd.DataFrame(data=cursor.fetchall())


def extract_patterns(datafrmae):
    """
    Thisd function extracts all patterns in the last two parts of
    the [GeoLocationCode] field from the Address table.
    :param datafrmae: pandas dataframe version of the Address tyable
    :return: ???
    """
    pass


if __name__ == '__main__':

    database_name = sys.argv[0]
    df = read_address_table(database=database_name)
    extract_patterns(df)
