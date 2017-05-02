"""
Batch geocoding of addresses using the Google Maps Geocoding API.

This script utilizes the Google's Geocoding API to allow batch geocoding. A CSV
file is expected as input, containing an index column and an address column.
The output is a CSV file with the additional columns latitude and longitude.

An API key is needed to use the script, and the key must be exported as an
environment variable. See README.md for instructions for authentication.

If an address is missing it will be geocoded as (0.0, 0.0) in the output file.
"""

import argparse
import googlemaps
import logging
import os
import pandas as pd
from tqdm import tqdm


def check_auth():
    """Check for a Google Maps Geocoding API key.

    For authentication to work you must have a Google Maps Geocoding API key
    and the GOOGLE_API_KEY environment variable must be exported:

    >>> export GOOGLE_API_KEY=AI...

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


def load_addresses(input_file):
    """Load addresses from CSV.

    :param input_file: Filename of CSV with two columns (index, address)
    :type input_file: string

    :return: Address dataFrame and address list
    :rtype: dataFrame, list
    """
    address_df = pd.read_csv(input_file, usecols=[1], names=['Address'])
    address_list = address_df['Address'].tolist()
    return address_df, address_list


def geocode_addresses(address_df,
                      address_list,
                      initial_address,
                      final_address,
                      api_key):
    """Geocode addresses, add latitude/longitude columns to dataFrame.

    :param address_df: DataFrame with two columns (index, address)
    :type address_df: dataFrame

    :param address_list: List of addresses to geocode
    :type address_list: list

    :param initial_address: Where to start in the address list
    :type initial_address: int

    :param final_address: Where to end in the address list
    :type final_address: int

    :param api_key: Google Maps Geocoding API key
    :type gmaps: string

    :return: Address dataFrame with new columns (Latitude, Longitude)
    :rtype: address dataFrame
    """
    gmaps = googlemaps.Client(key=api_key)
    address_list = address_list[initial_address:final_address]
    for address_id, address in enumerate(tqdm(address_list), initial_address):
        geocode_result = []
        latitude, longitude = 0, 0
        # address NaN -> don't geocode
        if not pd.isnull(address_list[address_id]):
            geocode_result = gmaps.geocode(address)
        # geocode_results empty -> latitude, longitude == 0,0
        if geocode_result:
            latitude = geocode_result[0]['geometry']['location']['lat']
            longitude = geocode_result[0]['geometry']['location']['lng']
        address_df.at[address_id, 'Latitude'] = latitude
        address_df.at[address_id, 'Longitude'] = longitude
    return address_df


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s \n',
                        level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input file")
    parser.add_argument("-o", help="output file")
    parser.add_argument("-n",
                        type=int,
                        help="number of CSV rows to geocode")
    parser.add_argument("--initial",
                        type=int,
                        help="CSV row to start geocoding at")
    parser.add_argument("--final",
                        type=int,
                        help="CSV row to stop geocoding at")
    args = parser.parse_args()
    api_key = check_auth()
    input_file = args.i
    data, address_list = load_addresses(input_file)
    if args.n:
        final_address = args.n
        initial_address = 0
    if args.initial:
        initial_address = args.initial
    else:
        initial_address = 0
    if args.final:
        final_address = args.final
    else:
        final_address = len(address_list)
    address_df = geocode_addresses(data,
                                   address_list,
                                   initial_address,
                                   final_address,
                                   api_key)
    output_file = args.o
    address_df.to_csv(output_file)
