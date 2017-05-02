#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import googlemaps
import os
import pandas as pd
from tqdm import tqdm


def check_auth():
    """Check for a Google Maps Geocoding API key and authenticate.

    For authentication to work you must have a Google Maps Geocoding API key
    and the GOOGLE_API_KEY environment variable exported:

    >>> export GOOGLE_API_KEY=AI...

    :rtype: gmaps object (done here so that we only create one Client session)
    """
    api_key = os.environ["GOOGLE_API_KEY"]
    gmaps = googlemaps.Client(key=api_key)
    return gmaps


def load_addresses(input_file):
    """Load addresses from CSV.

    :param input_file: A CSV file with two columns: index, address
    :type input_file: string

    :rtype: address dataFrame (so we don't have to reconstruct it later)
    """
    address_df = pd.read_csv(input_file, usecols=[1], names=['Address'])
    address_list = address_df['Address'].tolist()
    return address_df, address_list


def geocode_addresses(address_df,
                      address_list,
                      initial_address,
                      final_address,
                      gmaps):
    """Geocode addresses, add latitude/longitude columns to dataFrame.

    :param address_df: A dataFrame with two columns: index, address
    :type address_df: dataFrame

    :param address_list: A list of addresses to geocode
    :type address_list: list

    :param initial_address: The address to start at in the address list
    :type initial_address: int

    :param final_address: The address to end at in the address list
    :type final_address: int

    :param gmaps: Provides the geocode function which is used to turn the
    address list into a detailed geocoded JSON file
    :type gmaps: gmaps object

    :rtype: address dataFrame (contains new Latitude and Longitude columns)
    """
    address_list = address_list[initial_address:final_address]
    print address_list
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
    gmaps = check_auth()
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
                                   gmaps)
    output_file = args.o
    address_df.to_csv(output_file)
