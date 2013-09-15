#!/usr/bin/python
# -*- coding: utf-8 -*-

from Crawler import *
from SeleniumWrapper import SeleniumError

import argparse
from   datetime import date, timedelta
import locale
import sys
from   time import strftime
import traceback

#__________________________________________________________________

if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'enu_us')
elif 'linux' in sys.platform or sys.platform == 'cygwin':
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF8')

#__________________________________________________________________

WEBPAGE_LANGUAGE = "pl"
WEBPAGE_CURRENCY = "pln"
WEBPAGE_USRPLACE = "PL"

DEPARTURE_POINT   = "pl"
IGNORED_POINTS    = None # list
NEXT_MONTH_DATE   = date.today()+timedelta(30)
DEPARTURE_MONTH   = strftime("%B", (NEXT_MONTH_DATE.timetuple())).lower() # next month, eg. "october"
DEPARTURE_YEAR    = NEXT_MONTH_DATE.year

PRICE_LIMIT       = 200
FLIGHTS_LIMIT     = 2

SELENIUM_HOST         = "localhost"
SELENIUM_PORT         = 4444
SELENIUM_START_CMD    = "*chrome"
SELENIUM_LOAD_TIMEOUT = 7.5 # seconds

MAP_SAVE_TO_DOT  = False
MAP_DOT_FILENAME = "map.dot"

OUTPUT_ENCODING = "utf-8"

#__________________________________________________________________
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Crawler for skyscanner.net which lists good first-to-check list of possible flights with changes in given date',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    g_webpage = parser.add_argument_group('webpage')
    g_webpage.add_argument('-l', '--language',   help='language for names of countries or cities', default=WEBPAGE_LANGUAGE)
    g_webpage.add_argument('-c', '--currency',   help='type of money; useful to set price limit', default=WEBPAGE_CURRENCY)
    g_webpage.add_argument('-u', '--user-place', help='country code for communication with website', default=WEBPAGE_USRPLACE)

    g_map = parser.add_argument_group('map')
    g_map.add_argument('-d', '--departure-point', help='country or city code which from crawler starts', default=DEPARTURE_POINT)
    g_map.add_argument('-i', '--ignored-points',  help='codes of countries or cities to ignore when crawler builds map of connections, e.g. fr gr it', default=IGNORED_POINTS, nargs='+')
    g_map.add_argument('-m', '--departure-month', help='month when you want to depart', default=DEPARTURE_MONTH)
    g_map.add_argument('-y', '--departure-year',  help='year when you want to depart', default=DEPARTURE_YEAR)
    g_map.add_argument('-r', '--price-limit',     help='price limit for overall flights to desired point', default=PRICE_LIMIT, type=int)
    g_map.add_argument('-f', '--flights-limit',   help='maximum number of changes', default=FLIGHTS_LIMIT, type=int)

    g_selenium = parser.add_argument_group('selenium')
    g_selenium.add_argument('-a', '--selenium-host',         help='address of running selenium service', default=SELENIUM_HOST)
    g_selenium.add_argument('-p', '--selenium-port',         help='port number of running selenium service', default=SELENIUM_PORT, type=int)
    g_selenium.add_argument('-s', '--selenium-start-cmd',    help='start command for selenium browser', default=SELENIUM_START_CMD)
    g_selenium.add_argument('-t', '--selenium-load-timeout', help='maximum waiting time in seconds to fully load webpage', default=SELENIUM_LOAD_TIMEOUT, type=float)

    g_dot = parser.add_argument_group('dot')
    g_dot.add_argument('-o', '--map-save-to-dot',  help='save built map to a dot file', action='store_true')
    g_dot.add_argument('-n', '--map-dot-filename', help='name of dot file', default=MAP_DOT_FILENAME)


    parser.add_argument('-e', '--output-encoding', help='encoding for shell', default=OUTPUT_ENCODING)

    parser.set_defaults(map_save_to_dot=MAP_SAVE_TO_DOT)

    args = parser.parse_args()

    print("Running configuration:")
    for attr, value in sorted(args.__dict__.iteritems()):
        print("\t{0} = {1}".format(attr, value))

    c = Crawler(args.language,
                args.currency,
                args.user_place,
                args.departure_point,
                args.ignored_points,
                args.departure_month,
                args.departure_year,
                args.price_limit,
                args.flights_limit,
                args.selenium_host,
                args.selenium_port,
                args.selenium_start_cmd,
                args.selenium_load_timeout,
                args.map_save_to_dot,
                args.map_dot_filename,
                args.output_encoding)

    try:
        c.create_map()
        c.analyze_map()
    except KeyboardInterrupt:
        print("Ctrl-C pressed...")
    except SeleniumError as err:
        print(str(err))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
    finally:
        c.cleanup()