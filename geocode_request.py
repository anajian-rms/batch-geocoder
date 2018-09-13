import json
import simplejson
from urllib import parse, request

filepath = r"D:\Python_Projects\googleapi\config\api_keys.json"
with open(filepath, 'r') as f:
    API_KEY = json.load(f)["API_KEY"]["Geocoding"]

# API_KEY = os.environ["GOOGLE_API_KEY"]
GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'


def geocode(address, **geo_args):
    geo_args.update({
        'address': address
    })

    url = GEOCODE_BASE_URL + '?' + parse.urlencode(geo_args) + '&key=' + API_KEY
    result = simplejson.load(request.urlopen(url))

    # print(simplejson.dumps([s['formatted_address'] for s in result['results']], indent=2))
    print(simplejson.dumps(["%s: %s" % (s['types'][0], s['long_name']) for s in result['results'][0]['address_components']], indent=2))


if __name__ == '__main__':
    geocode(address="1495+E+27th+Ave,+Vancouver,+BC+V5N+2W6,+Canada")
