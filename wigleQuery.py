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
if args.lat:
    lati = float(args.lat)
    long = float(args.long)
    distance = float(args.distance)
elif args.lat == None:
    lati = 39.7392
    long = -104.9903
range = args.range
googleMapAPI = args.googleAPI

creds = wigle_username + wigle_password
creds_bytes = creds.encode('ascii')

clrs = ["red", "yellow", "blue", "orange", "purple", "green", "black", "white", "pink", "brown", "lightgreen", "lightblue"]

#setup map in AoI
gmap = gmplot.GoogleMapPlotter(lati, long, 14)
gmap.apikey = googleMapAPI

lat_list = [] 
lon_list = [] 

count = 0

def userStats(api_key, username, password):
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

def searchBSSID(BSSID, color, output_file):
    payload = {'netid': BSSID}
    try:
        response = requests.get(url='https://api.wigle.net/api/v2/network/search', 
                                params=payload, 
                                auth=HTTPBasicAuth(wigle_username, wigle_password))
        response.raise_for_status()
        results = response.json()
        
        print(f"Query Success: {results['success']} \n")

        if not results['success']:
            print(f"Fail Reason: {results['message']} \n")
            return

        print(f"Total Results: {results['totalResults']}")

        for result in results['results']:
            lat = float(result.get('trilat', 0))
            lon = float(result.get('trilong', 0))

            if not result.get('netid'):
                print(f"BSSID: {BSSID} not found!")
                return

            data = format_data(result)
            print(f"FOUND: {data}")
            gmap.marker(lat, lon, color=color, title=data)
            print(f"\nPopulating {output_file}...\n")
            print("Total Results: %s" % results['totalResults'])
            gmap.draw(output_file)

    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def format_data(result):
    ssid = result.get('ssid')
    ssid = "---HIDDEN---" if ssid is None else ssid
    netid = result.get('netid', '')
    encryption = result.get('encryption', '')
    channel = str(result.get('channel', ''))
    lastupdt = result.get('lastupdt', '')
    
    return f"{ssid},{netid},{encryption},{channel},{lastupdt}"

def process_results(results, color):
    totalCount = 0
    for result in results['results']:
        totalCount += 1
        lat = float(result['trilat'])
        lon = float(result['trilong'])
        data = format_data(result)
        print("FOUND: " + data)
        gmap.marker(lat, lon, color=color, title=data)
    return totalCount

def searchESSID(essid, color, output_file):
    payload = {'ssid': essid}
    try:
        response = requests.get(url='https://api.wigle.net/api/v2/network/search', 
                                params=payload, 
                                auth=HTTPBasicAuth(wigle_username, wigle_password))
        response.raise_for_status()
        results = response.json()

        print(f"Query Success: {results['success']} \n")
        
        if not results['success']:
            print(f"Fail Reason: {results['message']} \n")
            return

        total_results = results['totalResults']
        print(f"Total Results: {total_results}")

        markers(essid, total_results, color)

        print(f"{total_results} total results discovered!")
        print(f"\nPopulating {output_file}...\n")
        print("Total Results: %s" % results['totalResults'])
        gmap.draw(output_file)

    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


def markers(essid, totalResults, color):
    if args.distance:
        distance = args.distance
    if args.lat:
        lati = args.lat
    if args.long:
        long = args.long
    pageCount = 0
    print("Creating markers...")
    totalCount = 0
    if totalResults > 10000:
        print("Only plotting top 10,000 results")
        while pageCount < 9999:
            if args.lat:
                if len(essid) < 1:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'first': pageCount}
                elif args.ESSID or args.ESSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'ssid': ssid, 'first': pageCount}
                elif args.BSSID or args.BSSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'netid': ssid, 'first': pageCount}
            else:
                payload = {'ssid': essid, 'first': pageCount}
            results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
            print("Plotting results %d - %d..." % (pageCount,pageCount+100))
            for result in results['results']:
                totalCount += 1
                lat = float(result['trilat'])
                lon = float(result['trilong'])
                #drop marker for each point
                data = format_data(result)
                print("FOUND: " + data)
                gmap.marker(lat, lon, color=color, title=data)
            pageCount += 100
        print("%d results plotted on map!" % totalCount)
        return
    elif totalResults > 100 and totalResults < 10000:
        #determine amount of loops to iterate through all pages
        loops = int(totalResults / 100)
        leftovers = totalResults - (loops * 100)
        finalPageFirstNum = totalResults - leftovers
        while pageCount < (loops*100)-1:
            if args.lat:
                if len(essid) < 1:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'first': pageCount}
                elif args.ESSID or args.ESSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'ssid': ssid, 'first': pageCount}
                elif args.BSSID or args.BSSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'netid': ssid, 'first': pageCount}
            else:
                payload = {'ssid': essid, 'first': pageCount}
            results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
            print("Plotting results %d - %d..." % (pageCount,pageCount+100))
            for result in results['results']:
                totalCount += 1
                lat = float(result['trilat'])
                lon = float(result['trilong'])
                #drop marker for each point
                data = format_data(result)
                print("FOUND: " + data)
                gmap.marker(lat, lon, color=color, title=data)
            pageCount += 100
        if args.lat:
                if len(essid) < 1:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'first': finalPageFirstNum}
                elif args.ESSID or args.ESSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'ssid': ssid, 'first': finalPageFirstNum}
                elif args.BSSID or args.BSSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'netid': ssid, 'first': finalPageFirstNum}
        else:
            payload = {'ssid': essid, 'first': finalPageFirstNum}
        results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
        print("Last page %d - %d" % (finalPageFirstNum,totalResults))
        for result in results['results']:
            totalCount += 1
            lat = float(result['trilat'])
            lon = float(result['trilong'])
            #drop marker for each point
            data = format_data(result)
            print("FOUND: " + data)
            gmap.marker(lat, lon, color=color, title=data)
        print("%d results plotted on map!" % totalCount)
        return
    elif totalResults <= 100 and totalResults > 0:
        if args.lat:
                if len(essid) < 1:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance}
                elif args.ESSID or args.ESSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance,  'ssid': ssid}
                elif args.BSSID or args.BSSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance,  'netid': ssid}
        else:
            payload = {'ssid': essid}
        results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
        for result in results['results']:
            totalCount += 1
            lat = float(result['trilat'])
            lon = float(result['trilong'])
            #drop marker for each point
            data = format_data(result)
            print("FOUND: " + data)
            gmap.marker(lat, lon, color=color, title=data)
        print("%d results plotted on map!" % totalCount)
        return
    elif totalResults < 1:
        print("Sorry, No results for your query. Try a different ESSID\n")
        return

def searchBSSIDs(file):
    with open(file, "r") as f:
        lines = f.readlines()

    print("List of " + str(len(lines)) + " BSSIDs")

    for count, x in enumerate(lines):
        colour = clrs[count % len(clrs)]
        print("\nQuerying for " + x.strip())
        searchBSSID(x.strip(), colour, args.output_file)

    print("All BSSIDs processed.")

def searchESSIDs(file):
    with open(file, "r") as f:
        lines = f.readlines()

    print("List of " + str(len(lines)) + " ESSIDs")

    for count, x in enumerate(lines):
        colour = clrs[count % len(clrs)]
        print("\nQuerying for " + x.strip())
        searchESSID(x.strip(), colour, args.output_file)

    print("All ESSIDs processed.")
        
def latlong(lat, long, distance, ssid):
    global count
    first = 0  # Starting index for pagination

    while True:
        if len(ssid) < 1:
            payload = {'latrange1': lat, 'latrange2': lat, 'longrange1': long, 'longrange2': long, 'variance': distance, 'first': first}
        elif args.ESSID or args.ESSIDs:
            payload = {'latrange1': lat, 'latrange2': lat, 'longrange1': long, 'longrange2': long, 'variance': distance, 'ssid': ssid, 'first': first}
        elif args.BSSID or args.BSSIDs:
            payload = {'latrange1': lat, 'latrange2': lat, 'longrange1': long, 'longrange2': long, 'variance': distance, 'netid': ssid, 'first': first}

        results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
        
        print("Query Success: %s \n" % results['success'])

        if results['success'] == False:
            print("Fail Reason: " + results['message'] + "\n")
            break  # Exit the while loop if there's an error

        if results['totalResults'] == 0:
            print("NO RESULTS FOUND")
            break  # Exit the while loop if no results
        else:
            print("Total Results: %s" % results['totalResults'])

        for result in results['results']:
            colour = clrs[count]
            
            lat_res = float(result['trilat'])
            lon_res = float(result['trilong'])

            data = format_data(result)
            print("FOUND: " + data)
            gmap.marker(lat_res, lon_res, color=colour, title=data)
            if count == 11:
                count = 0
            else:
                count += 1

        # Check if there are more results to fetch. If not, break out of the loop.
        if len(results['results']) < 100:  # Assuming the API returns a max of 100 results per page
            break

        first += 100  # Fetch the next set of results
        
    print("\nPopulating output file...\n")
    print("Total Results: %s" % results['totalResults'])
    gmap.draw(args.output_file)

def handle_lat_conditions():
    if args.range:
        radius = distance * 150000
        gmap.circle(lati, long, radius, color="cyan", alpha=0.15)

    if args.ESSID:
        latlong(lati, long, distance, ESSID)
    elif args.ESSIDs or args.BSSIDs:
        ssid_file = ESSIDs if args.ESSIDs else BSSIDs
        with open(ssid_file, "r") as f:
            for ssid in f.readlines():
                latlong(lati, long, distance, ssid.strip())
    else:
        latlong(lati, long, distance, "")


if __name__ == "__main__":
    userStats(creds, wigle_username, wigle_password)

    if args.BSSID and not args.lat:
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
