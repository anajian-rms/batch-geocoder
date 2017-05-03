"""
Batch geocoding of addresses using the Google Maps Geocoding API.

This script utilizes the Google's Geocoding API to allow batch geocoding. A CSV
file is expected with columns:
| Index | Address |
or optionally (e.g. if some addresses are already geocoded):
| Index | Address | Latitude | Longitude |

An API key is needed to use the script, and the key must be exported as an
environment variable. See README.md for instructions for authentication.

If an address is missing it will be geocoded as (0.0, 0.0) in the output file.
"""

import argparse
import googlemaps
import logging
import numpy as np
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


def load_data(filename):
    """Load geolocation data from a CSV file.

    :param filename: Filename of CSV with columns either:
                     | Index | Address |
                     or optionally:
                     | Index | Address | Latitude | Longitude |
    :type filename: string

    :return: DataFrame containing addresses, possibly with some geocoded
    :rtype: dataFrame
    """
    # Check for empty CSV
    try:
        cols = pd.read_csv(filename, nrows=1).columns
    except pd.io.common.EmptyDataError as err:
        logging.error(err)

    # Two column CSV format
    if len(cols) == 2:
        names = ['Address']
        logging.info('No Latitude/Longitude columns found. Adding them.')

    # Four column CSV format
    elif len(cols) == 4:
        names = ['Address', 'Latitude', 'Longitude']
    else:
        logging.error('The number of CSV columns is incorrect.')
        raise TypeError
    address_df = pd.read_csv(filename,
                             names=names)

    # Convert two column format to four column format
    if len(cols) == 2:
        address_df = address_df.assign(Latitude=np.nan, Longitude=np.nan)

    return address_df


def geocode_addresses(address_df, address_limit, api_key):
    """Geocode addresses in a dataFrame.

    :param address_df: DataFrame with columns either:
                       | Index | Address |
                       or optionally:
                       | Index | Address | Latitude | Longitude |
    :type address_df: dataFrame

    :param api_key: Google Maps Geocoding API key
    :type api_key: string

    :return: DataFrame updated with geocoded addresses
    :rtype: dataFrame
    """
    # Start API client
    gmaps = googlemaps.Client(key=api_key)

    # Create address list, truncate if limit argument specified
    address_list = address_df['Address'].tolist()
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

    # <-- Main -->
    api_key = check_auth()
    data = load_data(filename)
    geolocation_df = geocode_addresses(data, address_limit, api_key)
    geolocation_df.to_csv(output_file)
