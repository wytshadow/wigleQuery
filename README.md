# wigleQuery
A command line tool for querying wigle.net and displaying results on Google Maps.

## Created by
[![Twitter](https://img.shields.io/badge/twitter-@theDarracott-blue.svg)](https://twitter.com/theDarracott)
<a href="https://wigle.net">
  
<img border="0" src="https://wigle.net/bi/caj9te22I7lh_+M3SDLdsg.png">
</a>

## Installation
```
python3 -m pip install -r requirements.txt
```

## Help
```
usage: wigleQuery.py [-h] [-b AA:BB:CC:DD:EE:FF] [-B ssids.txt] [-e Home-Wifi] [-E wifiNetworks.txt]
[-lat 47.25264] [-long -87.256243] [-dist 0.010] [-range y] -wA WigleAPIName -wT WigleAPIToken -g GoogleMapsAPI

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
  -o output.html, --output output.html
                        Output filename for the map
```
### WiGLE API
WiGLE API Name and Token are not your username and password. After creating an account on wigle.net, visit https://wigle.net/account to see your API Name and API Token.

*****WiGLE has a limit on how many API queries a user can make per day. It is easy to exceed that daily limit using this tool.*****


### Google Maps API
Follow the instructions at https://developers.google.com/maps/documentation/javascript/get-api-key to get a Maps JavaScript API key for use with this tool.

## Usage
```
python3 wigleQuery.py -wA AI***************18 -wT e6****************b8 -e "BobsWiFi" -g AI********************VKI -o wiglemap.html   

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

Plot multiple ESSIDs or BSSIDs

```
python3 wigleQuery.py -wA AI**********************18 -wT e6********************b8 -g AI***************************I -E testESSIDs.txt -o wiglemap.html

User: wytshadow
Rank: 1660
Discovered Wifi+GPS: 60380
Last Upload: 20200425-01714

List of 2 ESSIDs

Querying for xfinitywifi

Query Success: True

Total Results: 14623298
Creating markers...
Only plotting top 10,000 results
Plotting results 0 - 100...
...
...
...
10000 results plotted on map!
14623298 total results discovered!

Populating wiglemap.html...


Querying for attwifi

Query Success: True

Total Results: 332249
Creating markers...
Only plotting top 10,000 results
Plotting results 0 - 100...
...
...
...
10000 results plotted on map!
332249 total results discovered!

Populating wiglemap.html...
```

![](https://github.com/wytshadow/wigleQuery/blob/master/colors.png)

Specify Latitude/Longitude and Distance away from Lat/Long point. Value must be between 0.001 and 0.2.

```
python3 wigleQuery.py -lat 38.8895 -long "-77.0353" -dist 0.010 -wA AI**********************8 -wT e6*******************b8 -g A*********************I -o wiglemap.html

User: wytshadow
Rank: 1660
Discovered Wifi+GPS: 60380
Last Upload: 20200425-01714

Query Success: True

Total Results: 116937
FOUND: GlobalSuiteWireless,00:00:C5:D7:5D:D0,none,6,2007-02-11T15:00:00.000Z
FOUND: GlobalSuiteWireless,00:00:C5:D7:62:A0,none,1,2007-02-11T10:00:00.000Z
FOUND: HH3W304WAP-A,00:01:24:F1:C0:7B,wep,11,2004-05-03T20:00:00.000Z
FOUND: FPTLAN,00:01:24:F1:FD:77,unknown,0,2004-05-03T18:00:00.000Z
FOUND: wireless,00:01:36:10:29:D7,wep,6,2007-08-02T16:00:00.000Z
FOUND: David Kim,00:01:36:5B:A9:D0,wep,9,2011-12-10T18:00:00.000Z
FOUND: ---HIDDEN---,00:01:36:61:7E:CE,unknown,0,2010-08-20T19:00:00.000Z
FOUND: ---HIDDEN---,00:01:8E:D6:01:A9,unknown,0,2014-09-07T19:00:00.000Z
FOUND: <no ssid>,00:01:E6:93:49:FE,unknown,0,2006-05-19T19:00:00.000Z
```
![](https://github.com/wytshadow/wigleQuery/blob/master/latlong.png)

Add circle on map with range option to display search area.

```
python3 wigleQuery.py -lat 38.8895 -long "-77.0353" -dist 0.010 -range y -wA AI**********************18 -wT e6*******************b8 -g AI**************I -o wiglemap.html

User: wytshadow
Rank: 1660
Discovered Wifi+GPS: 60380
Last Upload: 20200425-01714

Query Success: True

Total Results: 116937
FOUND: GlobalSuiteWireless,00:00:C5:D7:5D:D0,none,6,2007-02-11T15:00:00.000Z
FOUND: GlobalSuiteWireless,00:00:C5:D7:62:A0,none,1,2007-02-11T10:00:00.000Z
FOUND: HH3W304WAP-A,00:01:24:F1:C0:7B,wep,11,2004-05-03T20:00:00.000Z
FOUND: FPTLAN,00:01:24:F1:FD:77,unknown,0,2004-05-03T18:00:00.000Z
FOUND: wireless,00:01:36:10:29:D7,wep,6,2007-08-02T16:00:00.000Z
FOUND: David Kim,00:01:36:5B:A9:D0,wep,9,2011-12-10T18:00:00.000Z
FOUND: ---HIDDEN---,00:01:36:61:7E:CE,unknown,0,2010-08-20T19:00:00.000Z
```
![](https://github.com/wytshadow/wigleQuery/blob/master/circle.png)

Seach for single BSSID/ESSID or list of BSSIDs/ESSIDs while specifying Lat/Long.

```
python3 wigleQuery.py -lat 38.8895 -long "-77.0353" -dist 0.010 -range y -wA AI**********************18 -wT e6*******************b8 -g AI**************I -e "GlobalSuiteWireless" -o wiglemap.html

User: wytshadow
Rank: 1660
Discovered Wifi+GPS: 60380
Last Upload: 20200425-01714

Query Success: True

Total Results: 13
FOUND: GlobalSuiteWireless,00:00:C5:D7:5D:D0,none,6,2007-02-11T15:00:00.000Z
FOUND: GlobalSuiteWireless,00:00:C5:D7:62:A0,none,1,2007-02-11T10:00:00.000Z
FOUND: GlobalSuiteWireless,00:0C:F1:07:15:09,unknown,0,2006-06-12T19:00:00.000Z
FOUND: GlobalSuiteWireless,00:0C:F1:4F:D7:79,unknown,0,2006-10-22T09:00:00.000Z
FOUND: GlobalSuiteWireless,00:14:A5:09:DA:25,none,0,2007-08-02T16:00:00.000Z
FOUND: GlobalSuiteWireless,00:14:A5:44:E8:7B,none,0,2007-08-02T16:00:00.000Z
FOUND: GlobalSuiteWireless,00:14:A5:4B:F6:33,unknown,0,2006-05-19T19:00:00.000Z
FOUND: GlobalSuiteWireless,00:14:A5:5A:E0:AB,unknown,0,2006-10-22T09:00:00.000Z
FOUND: GlobalSuiteWireless,02:16:6F:00:53:86,none,11,2007-02-11T10:00:00.000Z
FOUND: GlobalSuiteWireless,06:3E:17:3B:BB:07,none,11,2007-02-11T10:00:00.000Z
FOUND: GlobalSuiteWireless,1A:AF:11:08:92:1C,none,11,2007-09-12T19:00:00.000Z
FOUND: GlobalSuiteWireless,3A:C5:4E:41:92:79,unknown,0,2004-05-15T18:00:00.000Z
FOUND: GlobalSuiteWireless,42:C2:D3:D8:68:37,none,11,2008-08-12T12:00:00.000Z
Populating wiglemap.html...
```
