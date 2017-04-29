Batch Geocoding with the Google Maps Geocoding API
====================================

Allows batch geocoding using [Google Maps Geocoding API][Geocoding API] calls.  

## Description

**Geocoding** is the process of turning an address like `1600 Amphitheatre Parkway, Mountain View, CA` into a latitude and longitude pair `(37.422388, -122.0841883)`.

It turns out that there is a lot of technical work that goes on behind the scenes to do this conversion. The upshot is that latitude and longitude are better to work with because they *uniquely determine a location on Earth*. This makes geocoded addresses great for creating heatmaps, for example.

Fortunately, there are a lot of geocoding services out there. Even better, Google Maps provides a high quality [Geocoding API].

## Requirements

 - Python 2.7 or later.
 - A Google Maps API key.
 - `pandas`, `googlemaps`, and `tqdm`

## API Key
If you do not have a Google Maps API key, follow the [instructions to get an API key].

```bash
$ export GOOGLE_API_KEY=AI...
```

## Usage Limits

The Google Maps Geocoding API has [usage limits]. At the time of this writing, the standard tier gives **2,500 free requests per day** at up to 50 requests per second. They have pay-as-you-go billing (must be manually enabled) $0.50 USD / 1000 additional requests, up to 100,000 daily.

## Usage

To batch geocode all addresses in `input_file.csv` to `output_file.csv`,
```bash
$ python batch_google_geocoder.py -i input_file.csv -o output_file.csv
```
To batch geocode addresses in rows `n` to `m`,
```bash
$ python batch_google_geocoder.py -i input_file.csv -o output_file.csv --initial n --final m
```

[Geocoding API]: https://developers.google.com/maps/documentation/geocoding/

[instructions to get an API key]:https://console.developers.google.com/flows/enableapi?apiid=maps_backend,geocoding_backend,directions_backend,distance_matrix_backend,elevation_backend&keyType=CLIENT_SIDE&reusekey=true

[usage limits]:https://developers.google.com/maps/documentation/geocoding/usage-limits
