# wigleQuery
A command line tool for querying wigle.net and displaying results on Google Maps.

## Created by
[![Twitter](https://img.shields.io/badge/twitter-@theDarracott-blue.svg)](https://twitter.com/theDarracott)
<a href="https://wigle.net">
  
<img border="0" src="https://wigle.net/bi/caj9te22I7lh_+M3SDLdsg.png">
</a>

## Installation
```
pip3 install -r requirements.txt
```

## Help
```
usage: wigleQuery.py [-h] [-b AA:BB:CC:DD:EE:FF] [-B ssids.txt] [-e Home-Wifi] [-E wifiNetworks.txt] [-lat 47.25264] [-long -87.256243] [-dist 0.010] [-range y] -wA WigleAPIName -wT WigleAPIToken -g GoogleMapsAPI

A command line tool for querying wigle.net and displaying results on Google Maps.

optional arguments:
  -h, --help            show this help message and exit
  -b AA:BB:CC:DD:EE:FF  Search for single BSSID
  -B ssids.txt          Search for list of BSSIDs
  -e Home-Wifi          Search for single ESSID
  -E wifiNetworks.txt   Search for list of ESSIDs
  -lat 47.25264         Latitude
  -long -87.256243      Longitude
  -dist 0.010           Value must be between 0.001 and 0.2.
  -range y              Show circle on map for Lat/Long query
  -wA WigleAPIName      Wigle API Name from wigle.net
  -wT WigleAPIToken     Wigle API Token from wigle.net
  -g GoogleMapsAPI      Google Maps API key
```
### WiGLE API
WiGLE API Name and Token are not your username and password. After creating an account on wigle.net, visit https://wigle.net/account to see your API Name and API Token.

WiGLE has a limit on how many API queries a user can make per day. It is easy to exceed that daily limit using this tool. 


### Google Maps API
Follow the instructions at https://developers.google.com/maps/documentation/javascript/get-api-key to get a Maps JavaScript API key for use with this tool.

## Usage
```
python3 wigleQuery.py -wA AI***************18 -wT e6****************b8 -e "BobsWiFi" -g AI********************VKI    

User: wytshadow 
Rank: 1629 
Discovered Wifi+GPS: 60037 
Last Upload: 20200408-02113 

Query Success: True 

Total Results: 294
Initializing map...
Creating markers...
Plotting results 0 - 100...
Plotting results 100 - 200...
Last page 200 - 294
294 total results discovered!
294 results plotted on map!

Creating wiglemap.html...
```
Open wiglemap.html in a web browser.

![](https://github.com/wytshadow/wigleQuery/blob/master/wigleExample.png)

Hover over a marker on the map to see information about a wireless access point.

![](https://github.com/wytshadow/wigleQuery/blob/master/data.png)
