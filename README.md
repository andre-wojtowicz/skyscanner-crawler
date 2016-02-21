Skyscanner crawler
==================

This program crawls [http://www.skyscanner.net](http://www.skyscanner.net) and lists possible combined flights destinations in a given month. This might be helpful (as a first step) when you plan your holidays.

### Requirements

* [Selenium](http://www.seleniumhq.org) (2.35),
* Python (2.6).

Python libs:

* argparse,
* networkx,
* selenium.

### Exemplary execution
```
$ python SkyCrawler.py --price-limit 100 --currency pln --departure-point pl --language en

Running configuration:
        currency = pln
        departure_month = november
        departure_point = pl
        departure_year = 2013
        flights_limit = 2
        ignored_points = None
        language = en
        map_dot_filename = map.dot
        map_save_to_dot = False
        output_encoding = utf-8
        price_limit = 100
        selenium_host = localhost
        selenium_load_timeout = 7.5
        selenium_port = 4444
        selenium_start_cmd = *chrome
        user_place = PL
Initializing crawler...
Initializing selenium...
Points to check: 1
Loading page for PL... waiting for Javascript execution... processing 176 flights...
Points to check: 14
Loading page for BE... waiting for Javascript execution... processing 182 flights...
Points to check: 18
Loading page for FR... waiting for Javascript execution... processing 195 flights...
Points to check: 17
Loading page for NL... waiting for Javascript execution... processing 192 flights...
Points to check: 16
Loading page for GR... waiting for Javascript execution... processing 174 flights...

(...)

Points to check: 3
Loading page for MT... waiting for Javascript execution... processing 148 flights...
Points to check: 2
Loading page for UK... waiting for Javascript execution... processing 206 flights...
Points to check: 2
Loading page for SE... waiting for Javascript execution... processing 184 flights...
Points to check: 3
Loading page for CZ... waiting for Javascript execution... processing 180 flights...
Points to check: 2
Loading page for BA... waiting for Javascript execution... processing 105 flights...
Points to check: 1
Loading page for MK... waiting for Javascript execution... processing 111 flights...
Flights from Poland:
19 pln - Norway
19 pln - Sweden
33 pln - Spain
33 pln - Belgium
33 pln - Germany
33 pln - United Kingdom
38 pln - Poland         ( via Norway )
40 pln - Finland
42 pln - Italy
42 pln - Netherlands
48 pln - France         ( via Sweden )
64 pln - Ireland
69 pln - Portugal       ( via Spain )
75 pln - Lithuania      ( via Norway )
75 pln - Romania        ( via Germany )
76 pln - Latvia         ( via Norway )
78 pln - Estonia        ( via Norway )
78 pln - Cyprus         ( via Norway )
78 pln - Malta  ( via Italy )
80 pln - Hungary        ( via Sweden )
81 pln - Greece         ( via Norway )
81 pln - Bosnia and Herzegovina         ( via Sweden )
81 pln - Republic of Macedonia  ( via Sweden )
90 pln - Morocco        ( via Belgium )
96 pln - Denmark        ( via United Kingdom )
96 pln - Croatia        ( via Belgium )
96 pln - Slovakia       ( via Belgium )
97 pln - Czech Republic         ( via United Kingdom )
99 pln - Georgia
Closing selenium...
```
