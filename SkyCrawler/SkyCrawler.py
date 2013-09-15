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

    c = Crawler(WEBPAGE_LANGUAGE,
                WEBPAGE_CURRENCY,
                WEBPAGE_USRPLACE,
                DEPARTURE_POINT,
                IGNORED_POINTS,
                DEPARTURE_MONTH,
                DEPARTURE_YEAR,
                PRICE_LIMIT,
                FLIGHTS_LIMIT,
                SELENIUM_HOST,
                SELENIUM_PORT,
                SELENIUM_START_CMD,
                SELENIUM_LOAD_TIMEOUT,
                MAP_SAVE_TO_DOT,
                MAP_DOT_FILENAME,
                OUTPUT_ENCODING)

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