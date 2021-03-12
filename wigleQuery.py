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

def userStats():
    payload = {'api_key': urlsafe_b64encode(creds_bytes)}
    results = requests.get(url='https://api.wigle.net/api/v2/stats/user', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()

    print("\nUser: %s " % results['statistics']['userName'])
    print("Rank: %s " % results['statistics']['rank'])
    print("Discovered Wifi+GPS: %s " % results['statistics']['discoveredWiFiGPS'])
    print("Last Upload: %s \n" % results['statistics']['last'])

def searchBSSID(BSSID, color):
    payload = {'netid': BSSID, 'api_key': urlsafe_b64encode(creds_bytes)}
    results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
    print("Query Success: %s \n" % results['success'])

    if results['success'] == False:
        print("Fail Reason: " + results['message']+ "\n")
        return

    print("Total Results: %s" % results['totalResults'])

    for result in results['results']:
        lat = float(result['trilat'])
        lon = float(result['trilong'])
    try:
        if not result['netid']:
            #no results for bssid
            return
    except:
        print("BSSID: " + BSSID + " not found!")
        return

    data = ""
    if result['ssid'] == None:
        data += "---HIDDEN---,"
    else:
        data += result['ssid'] + ","
    data += result['netid'] + ","
    data += result['encryption'] + ","
    data += str(result['channel']) + ","
    data += result['lastupdt']
    print("FOUND: " + data)
    gmap.marker(lat, lon, color=color, title=data)
    #totalCount = observations(BSSID, color)
    #print("%d total observations!" % totalCount)
    print("Populating wiglemap.html...\n")
    gmap.draw("wiglemap.html")

# def observations(BSSID, color):
#     #detail search aka every observation
#     payload = {'netid': BSSID, 'api_key': urlsafe_b64encode(creds_bytes)}
#     results = requests.get(url='https://api.wigle.net/api/v2/network/detail', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password))
#     json_data = json.loads(results.text)

#     print("Creating markers for every observation...")
#     totalCount = 0
#     for x in json_data[u'results']:
#         for y in x[u'locationData']:
#             #drop marker
#             lat_list.append(y[u'latitude'])
#             lon_list.append(y[u'longitude'])
#             gmap.scatter(lat_list, lon_list, color, size=0.1, marker=False)
#             #gmap.polygon(lat_list, lon_list, color=color)
#             totalCount += 1
#     return totalCount

def searchESSID(essid, color):
    payload = {'ssid': essid, 'api_key': urlsafe_b64encode(creds_bytes)}
    results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
    print("Query Success: %s \n" % results['success'])

    if results['success'] == False:
        print("Fail Reason: " + results['message']+ "\n")
        return

    print("Total Results: %s" % results['totalResults'])

    markers(essid, results['totalResults'], color)

    print("%d total results discovered!" % results['totalResults'])
    print("\nPopulating wiglemap.html...\n")
    gmap.draw("wiglemap.html")

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
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'first': pageCount}
                elif args.ESSID or args.ESSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'ssid': ssid, 'first': pageCount}
                elif args.BSSID or args.BSSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'netid': ssid, 'first': pageCount}
            else:
                payload = {'ssid': essid, 'api_key': urlsafe_b64encode(creds_bytes), 'first': pageCount}
            results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
            print("Plotting results %d - %d..." % (pageCount,pageCount+100))
            for result in results['results']:
                totalCount += 1
                lat = float(result['trilat'])
                lon = float(result['trilong'])
                #drop marker for each point
                data = ""
                data += result['ssid'] + ","
                data += result['netid'] + ","
                data += result['encryption'] + ","
                data += str(result['channel']) + ","
                data += result['lastupdt']
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
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'first': pageCount}
                elif args.ESSID or args.ESSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'ssid': ssid, 'first': pageCount}
                elif args.BSSID or args.BSSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'netid': ssid, 'first': pageCount}
            else:
                payload = {'ssid': essid, 'api_key': urlsafe_b64encode(creds_bytes), 'first': pageCount}
            results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
            print("Plotting results %d - %d..." % (pageCount,pageCount+100))
            for result in results['results']:
                totalCount += 1
                lat = float(result['trilat'])
                lon = float(result['trilong'])
                #drop marker for each point
                data = ""
                data += result['ssid'] + ","
                data += result['netid'] + ","
                data += result['encryption'] + ","
                data += str(result['channel']) + ","
                data += result['lastupdt']
                print("FOUND: " + data)
                gmap.marker(lat, lon, color=color, title=data)
            pageCount += 100
        if args.lat:
                if len(essid) < 1:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'first': finalPageFirstNum}
                elif args.ESSID or args.ESSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'ssid': ssid, 'first': finalPageFirstNum}
                elif args.BSSID or args.BSSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'netid': ssid, 'first': finalPageFirstNum}
        else:
            payload = {'ssid': essid, 'api_key': urlsafe_b64encode(creds_bytes), 'first': finalPageFirstNum}
        results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
        print("Last page %d - %d" % (finalPageFirstNum,totalResults))
        for result in results['results']:
            totalCount += 1
            lat = float(result['trilat'])
            lon = float(result['trilong'])
            #drop marker for each point
            data = ""
            data += result['ssid'] + ","
            data += result['netid'] + ","
            data += result['encryption'] + ","
            data += str(result['channel']) + ","
            data += result['lastupdt']
            print("FOUND: " + data)
            gmap.marker(lat, lon, color=color, title=data)
        print("%d results plotted on map!" % totalCount)
        return
    elif totalResults <= 100 and totalResults > 0:
        if args.lat:
                if len(essid) < 1:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes)}
                elif args.ESSID or args.ESSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'ssid': ssid}
                elif args.BSSID or args.BSSIDs:
                    payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'netid': ssid}
        else:
            payload = {'ssid': essid, 'api_key': urlsafe_b64encode(creds_bytes)}
        results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
        for result in results['results']:
            totalCount += 1
            lat = float(result['trilat'])
            lon = float(result['trilong'])
            #drop marker for each point
            data = ""
            data += result['ssid'] + ","
            data += result['netid'] + ","
            data += result['encryption'] + ","
            data += str(result['channel']) + ","
            data += result['lastupdt']
            print("FOUND: " + data)
            gmap.marker(lat, lon, color=color, title=data)
        print("%d results plotted on map!" % totalCount)
        return
    elif totalResults < 1:
        print("Sorry, No results for your query. Try a different ESSID\n")
        return

def searchBSSIDs(file):
    f = open(file, "r")
    lines = f.readlines()
    count = 0
    print("List of " + str(len(lines)) + " BSSIDs")
    for x in lines:
        colour = clrs[count]
        print("\nQuerying for " + x)
        searchBSSID(x.strip(), colour)
        if count == 11:
            count = 0
        else:
            count += 1
    f.close()
    return

def searchESSIDs(file):
    f = open(file, "r")
    lines = f.readlines()
    count = 0
    print("List of " + str(len(lines)) + " ESSIDs")
    for x in lines:
        colour = clrs[count]
        print("\nQuerying for " + x)
        searchESSID(x.strip(), colour)
        if count == 11:
            count = 0
        else:
            count += 1 
    f.close()
    return

def latlong(lat, long, distance, ssid):
    global count
    if len(ssid) < 1:
        payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes)}
    elif args.ESSID or args.ESSIDs:
        payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'ssid': ssid}
    elif args.BSSID or args.BSSIDs:
        payload = {'latrange1': lati, 'latrange2': lati, 'longrange1': long, 'longrange2': long, 'variance': distance, 'api_key': urlsafe_b64encode(creds_bytes), 'netid': ssid}

    results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
    print("Query Success: %s \n" % results['success'])

    if results['success'] == False:
        print("Fail Reason: " + results['message']+ "\n")
        return

    if results['totalResults'] == 0:
        print("NO RESULTS FOUND")
    else:
        print("Total Results: %s" % results['totalResults'])
    
    if len(ssid) == 0:
        for result in results['results']:
            colour = clrs[count]
            
            lat = float(result['trilat'])
            lon = float(result['trilong'])

            data = ""
            if result['ssid'] == None:
                data += "---HIDDEN---,"
            else:
                data += result['ssid'] + ","
            data += result['netid'] + ","
            data += result['encryption'] + ","
            data += str(result['channel']) + ","
            data += result['lastupdt']
            print("FOUND: " + data)
            gmap.marker(lat, lon, color=colour, title=data)
            if count == 11:
                count = 0
            else:
                count += 1
    else:
        for result in results['results']:
            colour = clrs[count]
            
            lat = float(result['trilat'])
            lon = float(result['trilong'])

            data = ""
            if result['ssid'] == None:
                data += "---HIDDEN---,"
            else:
                data += result['ssid'] + ","
            data += result['netid'] + ","
            data += result['encryption'] + ","
            data += str(result['channel']) + ","
            data += result['lastupdt']
            print("FOUND: " + data)
            gmap.marker(lat, lon, color=colour, title=data)
            if ESSID:
                if count == 11:
                    count = 0
                else:
                    count += 1
        
    print("Populating wiglemap.html...\n")
    gmap.draw("wiglemap.html")
        

if __name__ == "__main__":
    userStats()
    if args.BSSID and not args.lat:
        searchBSSID(BSSID, clrs[0])
    elif args.ESSID and not args.lat:
        searchESSID(ESSID, clrs[0])
    elif args.ESSIDs and not args.lat:
        searchESSIDs(ESSIDs)
    elif args.BSSIDs and not args.lat:
        searchBSSIDs(BSSIDs)
    elif args.lat:
        if range:
            radius = (distance * 150000)
            gmap.circle(lati, long, radius, color="cyan", alpha=0.15)
        if args.ESSID:
            latlong(lati, long, distance, ESSID)
        elif args.ESSIDs:
            f = open(ESSIDs, "r")
            lines = f.readlines()
            for x in lines:
                latlong(lati, long, distance, x.strip())
                count += 1
        elif not args.ESSID and not args.ESSIDs and not args.BSSID and not args.BSSIDs:
                ESSID = ""
                latlong(lati, long, distance, ESSID)
        else:
            if args.BSSID:
                latlong(lati, long, distance, BSSID)
            elif args.BSSIDs:
                f = open(BSSIDs, "r")
                lines = f.readlines()
                for x in lines:
                    latlong(lati, long, distance, x.strip())
                    count += 1


    else:
        print(parser.print_help())
