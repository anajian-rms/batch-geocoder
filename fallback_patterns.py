import os
import sys
import json
import pyodbc
import pandas as pd
import pandas.io.sql


CREDENTIALS = 'config\credentials.json'
DATABASE_NAME = str(sys.argv[1]) if len(sys.argv) > 1 else 'AIG_TEST_EDM'


def read_address_table(database):
    """
    This functions reads dbo.Address table from the EDM
    :param database: name of the EDM
    :return: df
    :rtype pandas dataframe
    """
    with open(CREDENTIALS) as f:
        dbserver = json.load(f)["MSSQL"]
        connection_string = 'DRIVER=' + dbserver["driver"] + ';SERVER=' + dbserver["server"] + ';DATABASE=' + database + \
                            ';UID=' + dbserver["username"] + ';PWD=' + dbserver["password"]
    query = 'SELECT * FROM [' + database + '].[dbo].[Address]'

    with pyodbc.connect(connection_string) as conn:
        df = pd.io.sql.read_sql(query, conn)
    return df


def extract_patterns(dataframe):
    """
    This function extracts all patterns in the last two parts of
    the [GeoLocationCode] field from the Address table.
    :param dataframe: pandas dataframe version of the Address table
    :return: table of frequencies of extracted patterns
    :rtype: pandas series
    """
    seq = dataframe["GeoLocationCode"].apply(lambda x: '-'.join([str(s) for s in x.split('-')[2:]]))
    return pd.DataFrame(data=Address_df.groupby(seq).size())


if __name__ == '__main__':
    Address_df = read_address_table(database=DATABASE_NAME)
    patterns_df = extract_patterns(Address_df)
    # write results to csv
    patterns_df.to_csv(os.getcwd()+'\patterns_df.csv', sep=',', header=['Count'])
