"""
Batch geocoding of addresses using the Google Maps Geocoding API.

This script utilizes Google Maps' Geocoding API to allow batch geocoding. A CSV
file is expected with columns:

| Index | Address | Latitude | Longitude |

Note: if the data contains a header row, use the --header switch

An API key is needed to use the script, and the key must be exported as an
environment variable. See README.md for instructions for authentication.

If an address is missing it will be geocoded as (0.0, 0.0) in the output file.
"""

import argparse
import googlemaps
import logging
import os
import pandas as pd
from tqdm.tqdm import tqdm


def check_auth():
    """
    Check for a Google Maps Geocoding API key.

    For authentication to work you must have a Google Maps Geocoding API key
    and the GOOGLE_API_KEY environment variable must be exported:

     "">>> export GOOGLE_API_KEY=AI...

    :return: Google Maps Geocoding API key
    :rtype: string
    """
    api_key = os.environ["GOOGLE_API_KEY"]
    try:
        gmaps = googlemaps.Client(key=api_key)
        gmaps.geocode('San Francisco, CA')
    except ValueError:
        if not api_key:
            logging.error('GOOGLE_API_KEY not set.')
        else:
            logging.error('GOOGLE_API_KEY rejected by the server.')
    return api_key


def normalize_row(row):
    """
    Normalize input address data
    :param row: single row from a address Dataframe
    :type: List

    :return: id: input unique identifier DIM_LOC_ID
    :rtype: String
    :return: address: full address text
    :rtype: String
    """
    result = ''
    # Street address
    if row['Address Line 1'] != '':
        result += str(row['Address Line 1'])
    # City name
    if row['CTY_NM'] != '':
        result += ', ' + str(row['CTY_NM']) if len(result) else str(row['CTY_NM'])
    # State
    if row['State'] != '':
        result += ', ' + str(row['State']) if len(result) else str(row['State'])
    # Zipcode
    if row['POSTAL_CD'] != '':
        result += ' ' + str(row['POSTAL_CD']).split('-')[0] if len(result) else str(row['POSTAL_CD']).split('-')[0]
    # Country
    if row['ISO_CNTRY_NM'] != '':
        result += ', ' + str(row['ISO_CNTRY_NM']) if len(result) else str(row['ISO_CNTRY_NM'])
    return result


def standardize_address(filename):
    """
    Standardize input addresses
    :param filename: Filename of the original CSV with columns:
                     | DIM_LOC_ID | SRC_KY | LOC_NO | LOC_NM | TIV_RC | State | County | Address Line 1 | POSTAL_CD \n
                     | CTY_NM | ISO_CNTRY_CD | ISO_CNTRY_NM |
    :type filename: string

    :return: address_dataframe containing standardized addresses, with columns
                     | Address_Text | Latitude | Longitude |
    :rtype: DataFrame
    """
    # Check for empty CSV by reading in a single row
    try:
        cols = pd.read_csv(filename, nrows=1).columns
    except pd.io.common.EmptyDataError as err:
        logging.error(err)

    # load original data
    input_dataframe = pd.read_csv(filename, header='infer', dtype='str', na_values='null', keep_default_na=False)

    # create new dataframe
    address_dataframe = pd.DataFrame(data=None, columns=['Address_ID', 'Address_Text', 'Latitude', 'Longitude'])

    # load normalized address data
    address_dataframe['Address_ID'] = input_dataframe['DIM_LOC_ID']
    address_dataframe['Address_Text'] = input_dataframe.apply(lambda x: normalize_row(x), axis=1)

    return address_dataframe


def geocode_addresses(address_df, address_limit, api_key):
    """
    Geocode addresses in a DataFrame.

    :param address_df: DataFrame with columns either:
                       | Address_ID | Address_Text |
    :type address_df: DataFrame

    :param api_key: Google Maps Geocoding API key
    :type api_key: string

    :return: DataFrame updated with geocoded addresses
    :rtype: DataFrame
    """
    # Start API client
    gmaps = googlemaps.Client(key=api_key)

    # Create address list, truncate if limit argument specified
    address_list = address_df['Address_Text'].tolist()
    # print(address_df.loc[:, ['Address_ID', 'Address_Text']])
    if address_limit:
        address_list = address_list[:address_limit]

    # <-- Geocoding loop -->
    for address_id, address in enumerate(tqdm(address_list)):
        geocode_result = []
        # Address NaN -> don't geocode and set to default
        if pd.isnull(address_list[address_id]):
            latitude, longitude = 0, 0
        else:
            geocode_result = gmaps.geocode(address)
        # Geocode_results empty -> latitude, longitude == 0,0
        if geocode_result:
            latitude = geocode_result[0]['geometry']['location']['lat']
            longitude = geocode_result[0]['geometry']['location']['lng']
        address_df.at[address_id, 'Latitude'] = latitude
        address_df.at[address_id, 'Longitude'] = longitude

    return address_df


if __name__ == '__main__':
    # <-- Logger -->
    logging.basicConfig(format='%(levelname)s: %(message)s \n',
                        level=logging.WARNING)

    # <-- Argument parser -->
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input file")
    parser.add_argument("-o", help="output file")
    parser.add_argument("--limit",
                        type=int,
                        help="Limit the number of geocodes")
    header_parser = parser.add_mutually_exclusive_group(required=True)
    header_parser.add_argument("--header",
                               dest='header',
                               action='store_true',
                               help="Data has header row with column names")
    header_parser.add_argument("--no-header",
                               dest='header',
                               action='store_false',
                               help="Data has no header row with column names")
    parser.set_defaults(header=False)

    args = parser.parse_args()
    if args.i:
        filename = args.i
    else:
        logging.error('No input CSV file specified.')
        raise TypeError
    if args.o:
        output_file = args.o
    else:
        logging.error('No output CSV file specified.')
        raise TypeError
    if args.limit:
        address_limit = args.limit
    else:
        address_limit = None
    if args.header:
        header = True
    else:
        header = None

    # <-- Main -->
    api_key = check_auth()
    address_data = standardize_address(filename=filename)
    geolocation_df = geocode_addresses(address_data, address_limit, api_key)
    geolocation_df.to_csv(output_file, header=header)
