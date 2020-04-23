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
parser.add_argument('-wA', metavar='WigleAPIName', dest='wigleAPI', action='store', help='Wigle API Name from wigle.net\n', required=True)
parser.add_argument('-wT', metavar='WigleAPIToken', dest='wigleToken', action='store', help='Wigle API Token from wigle.net\n', required=True)
parser.add_argument('-g',  metavar='GoogleMapsAPI', dest='googleAPI', action='store', help='Google Maps API key\n', required=True)
args = parser.parse_args()

wigle_username = args.wigleAPI
wigle_password = args.wigleToken
BSSID = args.BSSID
ESSID = args.ESSID
googleMapAPI = args.googleAPI

creds = wigle_username + wigle_password
creds_bytes = creds.encode('ascii')

def userStats():
    payload = {'api_key': urlsafe_b64encode(creds_bytes)}
    results = requests.get(url='https://api.wigle.net/api/v2/profile/user', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()

    print("\nUser: %s " % results['userid'])
    print("Login Success: %s \n" % results['success'])

def searchBSSID():
    payload = {'netid': BSSID, 'api_key': urlsafe_b64encode(creds_bytes)}
    results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()

    print("Total Results: %s" % results['totalResults'])
    if results['totalResults'] == 0:
      print("Sorry, No results for your query. Try a different BSSID\n")
      return

    lat = 0.0
    lon = 0.0

    for result in results['results']:
        lat = float(result['trilat'])
        lon = float(result['trilong'])
    
    print("Initializing map...")
    #setup map in AoI
    gmap = gmplot.GoogleMapPlotter(lat, lon, 6)
    gmap.apikey = googleMapAPI
    data = ""
    data += result['ssid'] + ","
    data += result['netid'] + ","
    data += result['encryption'] + ","
    data += str(result['channel'])
    gmap.marker(lat, lon, color='#FF0000', title=data)

    #detail search aka every observation
    results = requests.get(url='https://api.wigle.net/api/v2/network/detail', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password))
    json_data = json.loads(results.text)

    print("Creating markers...")
    totalCount = 0
    for x in json_data[u'results']:
      for y in x[u'locationData']:
        #drop marker
        data = ""
        data += result['ssid'] + ","
        data += result['netid'] + ","
        data += result['encryption'] + ","
        data += str(result['channel'])
        print(data)
        gmap.marker(y[u'latitude'], y[u'longitude'], color='#FF0000', title=data)
        totalCount += 1

    print("\nCreating wiglemap.html...")
    print("Total markers set: %d\n" % totalCount)
    gmap.draw("wiglemap.html")

def searchESSID():
    payload = {'ssid': ESSID, 'api_key': urlsafe_b64encode(creds_bytes)}
    results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()

    lat = 39.7392
    lon = -104.9903

    print("Initializing map...")
    #setup map in AoI
    gmap = gmplot.GoogleMapPlotter(lat, lon, 5)
    gmap.apikey = googleMapAPI

    print("Total Results: %s" % results['totalResults'])

    print("Creating markers...")
    totalCount = 0
    if results['totalResults'] > 10000:
        print("Only plotting top 10,000 results")
        pageCount = 0
        while pageCount < 9999:
            payload = {'ssid': ESSID, 'api_key': urlsafe_b64encode(creds_bytes), 'first': pageCount}
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
                data += str(result['channel'])
                gmap.marker(lat, lon, color='#FF0000', title=data)
            pageCount += 100
        print("%d total results discovered!" % results['totalResults'])
        print("%d results plotted on map!" % totalCount)
        print("\nCreating wiglemap.html...")
        gmap.draw("wiglemap.html")
    elif results['totalResults'] > 100 and results['totalResults'] < 10000:
        #determine amount of loops to iterate through all pages
        loops = int(results['totalResults'] / 100)
        leftovers = results['totalResults'] - (loops * 100)
        finalPageFirstNum = results['totalResults'] - leftovers
        pageCount = 0
        while pageCount < (loops*100)-1:
            payload = {'ssid': ESSID, 'api_key': urlsafe_b64encode(creds_bytes), 'first': pageCount}
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
                data += str(result['channel'])
                gmap.marker(lat, lon, color='#FF0000', title=data)
            pageCount += 100
        payload = {'ssid': ESSID, 'api_key': urlsafe_b64encode(creds_bytes), 'first': finalPageFirstNum}
        results = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(wigle_username, wigle_password)).json()
        print("Last page %d - %d" % (finalPageFirstNum,results['totalResults']))
        for result in results['results']:
            totalCount += 1
            lat = float(result['trilat'])
            lon = float(result['trilong'])
            #drop marker for each point
            data = ""
            data += result['ssid'] + ","
            data += result['netid'] + ","
            data += result['encryption'] + ","
            data += str(result['channel'])
            gmap.marker(lat, lon, color='#FF0000', title=data)
        print("%d total results discovered!" % results['totalResults'])
        print("%d results plotted on map!" % totalCount)
        print("\nCreating wiglemap.html...")
        gmap.draw("wiglemap.html")
    elif results['totalResults'] <= 100 and results['totalResults'] > 0:
        for result in results['results']:
            totalCount += 1
            lat = float(result['trilat'])
            lon = float(result['trilong'])
            #drop marker for each point
            data = ""
            data += result['ssid'] + ","
            data += result['netid'] + ","
            data += result['encryption'] + ","
            data += str(result['channel'])
            #print(data)
            gmap.marker(lat, lon, color='#FF0000', title=data)
        print("%d total results discovered!" % results['totalResults'])
        print("%d results plotted on map!" % totalCount)
        print("\nCreating wiglemap.html...")
        gmap.draw("wiglemap.html")
    elif results['totalResults'] < 1:
        print("Sorry, No results for your query. Try a different ESSID\n")
        return

if __name__ == "__main__":
    userStats()
    if args.BSSID:
        searchBSSID()
    elif args.ESSID:
        searchESSID()
    else:
        print(parser.print_help())