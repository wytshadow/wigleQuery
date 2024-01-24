#!/usr/bin/python

from gmplot import gmplot
import requests
import json
from base64 import urlsafe_b64encode
from requests.auth import HTTPBasicAuth
import argparse
import random
import csv
import time
import os
from datetime import datetime


parser = argparse.ArgumentParser(description='A command line tool for querying wigle.net and displaying results on Google Maps and outputting to a CSV file.')
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
parser.add_argument('-c', '--case_sensitive', action='store_true', help='Enable case-sensitive search for SSIDs', required=False)
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output', required=False)
parser.add_argument('-o', '--output', metavar='output.html', dest='output_file', action='store', default='wiglemap.html', help='Output filename for the map and csv files', required=False)
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

# setup map in AoI
gmap = gmplot.GoogleMapPlotter(lati, long, 14, apikey=googleMapAPI)

lat_list = [] 
lon_list = [] 

count = 0

# Hardcoded list of colors
COLORS = [
    "#000000", "#000080", "#00008B", "#0000CD", "#0000FF", "#006400", "#008000", "#008080", "#008B8B", "#00BFFF", 
    "#00CED1", "#00FA9A", "#00FF00", "#00FF7F", "#00FFFF", "#191970", "#1E90FF", "#20B2AA", "#228B22", "#2E8B57", 
    "#2F4F4F", "#32CD32", "#3CB371", "#40E0D0", "#4169E1", "#4682B4", "#483D8B", "#48D1CC", "#4B0082", "#556B2F", 
    "#5F9EA0", "#6495ED", "#66CDAA", "#696969", "#6A5ACD", "#6B8E23", "#708090", "#778899", "#7B68EE", "#7CFC00", 
    "#7FFF00", "#7FFFD4", "#800000", "#800080", "#808000", "#808080", "#87CEEB", "#87CEFA", "#8A2BE2", "#8B0000", 
    "#8B008B", "#8B4513", "#8FBC8F", "#90EE90", "#9370DB", "#9400D3", "#98FB98", "#9932CC", "#9ACD32", "#A0522D", 
    "#A52A2A", "#A9A9A9", "#ADD8E6", "#ADFF2F", "#AFEEEE", "#B0C4DE", "#B0E0E6", "#B22222", "#B8860B", "#BA55D3", 
    "#BC8F8F", "#BDB76B", "#C0C0C0", "#C71585", "#CD5C5C", "#CD853F", "#D2691E", "#D2B48C", "#D3D3D3", "#D8BFD8", 
    "#DA70D6", "#DAA520", "#DB7093", "#DC143C", "#DCDCDC", "#DDA0DD", "#DEB887", "#E0FFFF", "#E6E6FA", "#E9967A", 
    "#EE82EE", "#EEE8AA", "#F08080", "#F0E68C", "#F0F8FF", "#F0FFF0", "#F0FFFF", "#F4A460", "#F5DEB3", "#F5F5DC", 
    "#F5F5F5", "#F5FFFA", "#F8F8FF", "#FA8072", "#FAEBD7", "#FAF0E6", "#FAFAD2", "#FDF5E6", "#FF0000", "#FF00FF", 
    "#FF1493", "#FF4500", "#FF6347", "#FF69B4", "#FF7F50", "#FF8C00", "#FFA07A", "#FFA500", "#FFB6C1", "#FFC0CB", 
    "#FFD700", "#FFDAB9", "#FFDEAD", "#FFE4B5", "#FFE4C4", "#FFE4E1", "#FFEBCD", "#FFEFD5", "#FFF0F5", "#FFF5EE", 
    "#FFF8DC", "#FFFACD", "#FFFAF0", "#FFFAFA", "#FFFF00", "#FFFFE0", "#FFFFF0", "#FFFFFF"
]

last_color = None

def generate_color_for_id(id, id_color_map):
    if id not in id_color_map:
        id_color_map[id] = random.choice(COLORS)
    return id_color_map[id]

# Function to retrieve user statistics
def userStats(username, password):
    try:
        response = requests.get(url='https://api.wigle.net/api/v2/stats/user', auth=HTTPBasicAuth(username, password))
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

# Function to format data for printing
def format_data(result):
    ssid = result.get('ssid', '---')
    netid = result.get('netid', '')
    encryption = result.get('encryption', '')
    channel = str(result.get('channel', ''))
    lastupdt = result.get('lastupdt', '')
    lat = float(result.get('trilat', 0))
    lon = float(result.get('trilong', 0))
    return f"{ssid},{netid},{encryption},{channel},{lastupdt},{lat},{lon}"

# Function to search network and plot on the map
def search_network(endpoint, payload, gmap, output_csv, output_html, is_bssid=False, case_sensitive=False, verbose=False):
    total_plotted = 0
    search_after = None
    id_color_map = {}  # Dictionary to store color for each unique ID (BSSID/ESSID)
    ssid_counts = {}  # Dictionary to count SSIDs
    results_found = False
    page_count = 0 

    # Update payload with latitude, longitude, and variance if provided
    if args.lat and args.long and args.distance:
        payload.update({
            'latrange1': args.lat,
            'latrange2': args.lat,
            'longrange1': args.long,
            'longrange2': args.long,
            'variance': args.distance
        })

    # Check if the file exists and open in append mode if it does
    file_exists = os.path.isfile(output_csv)
    with open(output_csv, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['SSID', 'NetID', 'Encryption', 'Channel', 'Last Update', 'Latitude', 'Longitude']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file did not exist
        if not file_exists:
            writer.writeheader()

        while True:
            if search_after:
                payload['searchAfter'] = search_after

            try:
                response = requests.get(url=endpoint, params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password))
                response.raise_for_status()
                results = response.json()

                if not results.get('success'):
                    print("\nAPI call unsuccessful. Check the payload and API credentials.")
                    break

                if not results.get('results'):
                    if total_plotted == 0:
                        print("\nNo results found.")
                    break

                results_found = True
                page_count += 1 
                for result in results['results']:
                    if not is_bssid and case_sensitive and result['ssid'] != payload['ssid']:
                        continue
                    ssid = result['ssid']
                    data = format_data(result)
                    if not case_sensitive:
                        ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1
                    if verbose:
                        print(f"FOUND: {data}")
                    if is_bssid:
                        color = generate_color_for_id(result['netid'], id_color_map)
                    else:
                        color = generate_color_for_id(result['ssid'], id_color_map)
                    writer.writerow({
                        'SSID': result['ssid'],
                        'NetID': result['netid'],
                        'Encryption': result['encryption'],
                        'Channel': result['channel'],
                        'Last Update': result['lastupdt'],
                        'Latitude': result['trilat'],
                        'Longitude': result['trilong']
                    })
                    total_plotted += 1

                    # Add a marker for the network on the map
                    gmap.marker(result['trilat'], result['trilong'], title=result['ssid'], color=color)

                search_after = results.get('searchAfter')
                if not search_after:
                    break

            except requests.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                break
            except Exception as err:
                print(f'Other error occurred: {err}')
                break

    # After processing all results
    if results_found:
        print(f"\nSearch for {payload.get('ssid', payload.get('netid', ''))} Success!")
        print(f"Total Found: {total_plotted}")

        if not case_sensitive:
            print("\nSSID Counts:")
            for ssid, count in ssid_counts.items():
                print(f"{ssid} {count}")

    # Print dots with delay, reflecting pages processed
    for _ in __builtins__.range(page_count):
        time.sleep(1)
        print(".", end="", flush=True)

    if total_plotted > 0:
        print("\nAll results have been plotted.")

    # Plotting on the HTML file
    gmap.draw(output_html)



# Functions for different search types
def searchBSSID(BSSID, gmap, output_html, output_csv, verbose=False):
    payload = {'netid': BSSID}
    if args.lat and args.long and args.distance:
        payload.update({
            'latrange1': args.lat - args.distance,
            'latrange2': args.lat + args.distance,
            'longrange1': args.long - args.distance,
            'longrange2': args.long + args.distance,
            'variance': args.distance
        })
    endpoint = 'https://api.wigle.net/api/v2/network/search'
    search_network(endpoint, payload, gmap, output_csv, output_html, is_bssid=True, verbose=verbose)

def searchESSID(essid, gmap, output_html, output_csv, case_sensitive, verbose=False):
    payload = {'ssid': essid}
    if args.lat and args.long and args.distance:
        payload.update({
            'latrange1': args.lat - args.distance,
            'latrange2': args.lat + args.distance,
            'longrange1': args.long - args.distance,
            'longrange2': args.long + args.distance,
            'variance': args.distance
        })
    endpoint = 'https://api.wigle.net/api/v2/network/search'
    search_network(endpoint, payload, gmap, output_csv, output_html, is_bssid=False, case_sensitive=case_sensitive, verbose=verbose)

def searchBSSIDs(file, gmap, output_html, output_csv, verbose=False):
    with open(file, "r") as f:
        lines = f.readlines()
    for bssid in lines:
        searchBSSID(bssid.strip(), gmap, output_html, output_csv, verbose=verbose)

def searchESSIDs(file, gmap, output_html, output_csv, case_sensitive, verbose=False):
    with open(file, "r") as f:
        lines = f.readlines()
    for essid in lines:
        searchESSID(essid.strip(), gmap, output_html, output_csv, case_sensitive, verbose=verbose)

def searchBT(name, gmap, output_html, output_csv, is_bssid, verbose=False):
    endpoint = 'https://api.wigle.net/api/v2/bluetooth/search'
    payload = {'netid': name} if is_bssid else {'name': name}
    search_network(endpoint, payload, gmap, output_csv, output_html, is_bssid=is_bssid, verbose=verbose)


def searchArea(lat, long, distance, gmap, output_html, output_csv, verbose=False):
    payload = {
        'latrange1': lat - distance,
        'latrange2': lat + distance,
        'longrange1': long - distance,
        'longrange2': long + distance,
        'variance': distance
    }
    endpoint = 'https://api.wigle.net/api/v2/network/search'
    search_network(endpoint, payload, gmap, output_csv, output_html, is_bssid=False, case_sensitive=False, verbose=verbose)



if __name__ == "__main__":
    userStats(wigle_username, wigle_password)
    verbose_mode = args.verbose

    # Generate a timestamp
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Extract the base filename without the extension
    base_output_file = os.path.splitext(args.output_file)[0]

    # Append the timestamp to the filenames
    output_html = f"{base_output_file}-{current_time}.html"
    output_csv = f"{base_output_file}-{current_time}.csv"

    if BTBSSID:
        searchBT(BTBSSID, gmap, output_html, output_csv, is_bssid=True, verbose=verbose_mode)
    elif BTBSSIDs:
        with open(BTBSSIDs, "r") as file:
            for line in file:
                searchBT(line.strip(), gmap, output_html, output_csv, is_bssid=True, verbose=verbose_mode)
    elif BT_ESSID:
        searchBT(BT_ESSID, gmap, output_html, output_csv, is_bssid=False, verbose=verbose_mode)
    elif BT_ESSIDs:
        with open(BT_ESSIDs, "r") as file:
            for line in file:
                searchBT(line.strip(), gmap, output_html, output_csv, is_bssid=False, verbose=verbose_mode)
    elif args.BSSID and not args.lat:
        searchBSSID(BSSID, gmap, output_html, output_csv, verbose=verbose_mode)
    elif args.ESSID and not args.lat:
        searchESSID(ESSID, gmap, output_html, output_csv, args.case_sensitive, verbose=verbose_mode)
    elif args.ESSIDs and not args.lat:
        searchESSIDs(args.ESSIDs, gmap, output_html, output_csv, args.case_sensitive, verbose=verbose_mode)
    elif args.BSSIDs and not args.lat:
        searchBSSIDs(BSSIDs, gmap, output_html, output_csv, verbose=verbose_mode)
    elif args.lat and not (args.ESSID or args.BSSID or args.ESSIDs or args.BSSIDs):
        # Latitude and Longitude are provided but no specific SSID/BSSID
        searchArea(lati, long, distance, gmap, output_html, output_csv, verbose=verbose_mode)
    else:
        print(parser.print_help())
