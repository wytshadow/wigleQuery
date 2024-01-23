#!/usr/bin/python

from gmplot import gmplot
import requests
import json
from base64 import urlsafe_b64encode
from requests.auth import HTTPBasicAuth
import argparse

parser = argparse.ArgumentParser(description='A command line tool for querying wigle.net and displaying results on Google Maps.')
parser.add_argument('-b', metavar='AA:BB:CC:DD:EE:FF', dest='BSSID', action='store', help='Search for single BSSID\n', required=False)
parser.add_argument('-B', metavar='ssids.txt', dest='BSSIDs', action='store', help='Search for list of BSSIDs\n', required=False)
parser.add_argument('-e', metavar='Home-Wifi', dest='ESSID', action='store', help='Search for single ESSID\n', required=False)
parser.add_argument('-E', metavar='wifiNetworks.txt', dest='ESSIDs', action='store', help='Search for list of ESSIDs\n', required=False)
parser.add_argument('-btb', metavar='AA:BB:CC:DD:EE:FF', dest='BTBSSID', action='store', help='Search for single BT MAC Address\n', required=False)
parser.add_argument('-btB', metavar='btBSSIDs.txt', dest='BTBSSIDs', action='store', help='Search for list of BT MAC Addresses\n', required=False)
parser.add_argument('-bte', metavar='BT-Device', dest='BT_ESSID', action='store', help='Search for single BT Device names\n', required=False)
parser.add_argument('-btE', metavar='btDevices.txt', dest='BT_ESSIDs', action='store', help='Search for list of BT Device names\n', required=False)
parser.add_argument('-lat', metavar='47.25264', dest='lat', action='store', help='Latitude\n', required=False)
parser.add_argument('-long', metavar='-87.256243', dest='long', action='store', help='Longitude\n', required=False)
parser.add_argument('-dist', metavar='0.010', dest='distance', action='store', help='Value must be between 0.001 and 0.2.\n', required=False)
parser.add_argument('-range', metavar='y', dest='range', action='store', help='Show circle on map for Lat/Long query\n', required=False)
parser.add_argument('-wA', metavar='WigleAPIName', dest='wigleAPI', action='store', help='Wigle API Name from wigle.net\n', required=True)
parser.add_argument('-wT', metavar='WigleAPIToken', dest='wigleToken', action='store', help='Wigle API Token from wigle.net\n', required=True)
parser.add_argument('-g',  metavar='GoogleMapsAPI', dest='googleAPI', action='store', help='Google Maps API key\n', required=True)
parser.add_argument('-o', '--output', metavar='output.html', dest='output_file', action='store', default='wiglemap.html', help='Output filename for the map', required=False)
args = parser.parse_args()

wigle_username = args.wigleAPI
wigle_password = args.wigleToken
BSSID = args.BSSID
ESSID = args.ESSID
ESSIDs = args.ESSIDs
BSSIDs = args.BSSIDs
BTBSSID = args.BTBSSID
BTBSSIDs = args.BTBSSIDs
BT_ESSID = args.BT_ESSID
BT_ESSIDs = args.BT_ESSIDs
if args.lat:
    lati = float(args.lat)
    long = float(args.long)
    distance = float(args.distance)
elif args.lat == None:
    lati = 39.7392
    long = -104.9903
range = args.range
googleMapAPI = args.googleAPI

clrs = ["red", "yellow", "blue", "orange", "purple", "green", "black", "white", "pink", "brown", "lightgreen", "lightblue"]

# setup map in AoI
gmap = gmplot.GoogleMapPlotter(lati, long, 14)
gmap.apikey = googleMapAPI

lat_list = [] 
lon_list = [] 

count = 0


def userStats(username, password):
    try:
        response = requests.get(url='https://api.wigle.net/api/v2/stats/user',  
                                auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        results = response.json()
        
        print(f"\nUser: {results['statistics']['userName']}")
        print(f"Rank: {results['statistics']['rank']}")
        print(f"Discovered Wifi+GPS: {results['statistics']['discoveredWiFiGPS']}")
        print(f"Last Upload: {results['statistics']['last']} \n")
        
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def format_data(result):
    ssid = result.get('ssid', '---')
    netid = result.get('netid', '')
    encryption = result.get('encryption', '')
    channel = str(result.get('channel', ''))
    lastupdt = result.get('lastupdt', '')
    lat = float(result.get('trilat', 0))
    lon = float(result.get('trilong', 0))
    
    return f"{ssid},{netid},{encryption},{channel},{lastupdt},{lat},{lon}"

def search_network(endpoint, payload, color, output_file):
    total_plotted = 0
    search_after = None

    while True:
        if search_after:
            payload['searchAfter'] = search_after

        try:
            response = requests.get(url=endpoint, params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password))
            response.raise_for_status()
            results = response.json()

            if not results.get('success'):
                print("API call unsuccessful. Check the payload and API credentials.")
                break

            if not results.get('results'):
                print("No more results.")
                break

            for result in results['results']:
                data = format_data(result)
                print(f"FOUND: {data}")
                gmap.marker(result['trilat'], result['trilong'], color=color, title=data)
                total_plotted += 1

            search_after = results.get('searchAfter')
            if not search_after or total_plotted >= results.get('totalResults', 0):
                print("Fetched all available results.")
                break

        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            break
        except Exception as err:
            print(f'Other error occurred: {err}')
            break

    print(f"\nPopulating {output_file} with {total_plotted} results...\n")
    gmap.draw(output_file)


def searchBSSID(BSSID, color, output_file):
    payload = {'netid': BSSID}
    endpoint = 'https://api.wigle.net/api/v2/network/search'
    search_network(endpoint, payload, color, output_file)

def searchESSID(essid, color, output_file):
    payload = {'ssid': essid}
    endpoint = 'https://api.wigle.net/api/v2/network/search'
    search_network(endpoint, payload, color, output_file)

def searchBSSIDs(file):
    with open(file, "r") as f:
        lines = f.readlines()

    for count, bssid in enumerate(lines):
        colour = clrs[count % len(clrs)]
        print(f"\nQuerying for BSSID: {bssid.strip()}")
        searchBSSID(bssid.strip(), colour, args.output_file)

def searchESSIDs(file):
    with open(file, "r") as f:
        lines = f.readlines()

    for count, essid in enumerate(lines):
        colour = clrs[count % len(clrs)]
        print(f"\nQuerying for ESSID: {essid.strip()}")
        searchESSID(essid.strip(), colour, args.output_file)

def searchBT(name, color, output_file, is_bssid=False):
    endpoint = 'https://api.wigle.net/api/v2/bluetooth/search'
    payload = {'netid': name} if is_bssid else {'name': name}
    search_network(endpoint, payload, color, output_file)

if __name__ == "__main__":
    userStats(wigle_username, wigle_password)

    if BTBSSID:
        searchBT(BTBSSID, clrs[0], args.output_file, is_bssid=True)
    elif BTBSSIDs:
        with open(BTBSSIDs, "r") as file:
            for line in file:
                searchBT(line.strip(), clrs[0], args.output_file, is_bssid=True)
    elif BT_ESSID:
        searchBT(BT_ESSID, clrs[0], args.output_file)
    elif BT_ESSIDs:
        with open(BT_ESSIDs, "r") as file:
            for line in file:
                searchBT(line.strip(), clrs[0], args.output_file)
    elif args.BSSID and not args.lat:
        searchBSSID(BSSID, clrs[0], args.output_file)
    elif args.ESSID and not args.lat:
        searchESSID(ESSID, clrs[0], args.output_file)
    elif args.ESSIDs and not args.lat:
        searchESSIDs(ESSIDs)
    elif args.BSSIDs and not args.lat:
        searchBSSIDs(BSSIDs)
    elif args.lat:
        handle_lat_conditions()
    else:
        print(parser.print_help())
