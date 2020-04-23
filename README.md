# wigleQuery
A command line tool for querying wigle.net and displaying results on Google Maps.

## Created by
[![Twitter](https://img.shields.io/badge/twitter-@theDarracott-blue.svg)](https://twitter.com/theDarracott)

## Installation
```
pip3 install -r requirements.txt
```

## Help
```
usage: wigleQuery.py [-h] [-b AA:BB:CC:DD:EE:FF] [-B ssids.txt] [-e Home-Wifi]
                     [-E wifiNetworks.txt] -wA WigleAPIName -wT WigleAPIToken
                     -g GoogleMapsAPI

A command line tool for querying wigle.net and displaying results on Google
Maps.

optional arguments:
  -h, --help            show this help message and exit
  -b AA:BB:CC:DD:EE:FF  Search for single BSSID
  -B ssids.txt          Search for list of BSSIDs
  -e Home-Wifi          Search for single ESSID
  -E wifiNetworks.txt   Search for list of ESSIDs
  -wA WigleAPIName      Wigle API Name from wigle.net
  -wT WigleAPIToken     Wigle API Token from wigle.net
  -g GoogleMapsAPI      Google Maps API key
```

## Usage

```
python3 wigleQuery.py -wA AI***************18 -wT e6****************b8 -e "BobsWiFi" -g AI********************VKI    

User: wytshadow 
Login Success: true 

Initializing map...
Total Results: 294
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
