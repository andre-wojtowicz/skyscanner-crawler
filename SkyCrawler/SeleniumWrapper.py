# -*- coding: utf-8 -*-

from selenium import selenium

import re
import time
import urlparse

class SeleniumWrapper(object):

    root_url     = "http://www.skyscanner.net/"
    template_url = "http://www.skyscanner.net/flights-from/{FROM_POINT}/{MONTH}-{YEAR}/"

    def __init__(self, host,
                       port,
                       start_cmd,
                       load_timeout,
                       webpage_language,
                       webpage_currency,
                       webpage_usrplace,
                       departure_month,
                       departure_year,
                       output_encoding):

        print('Initializing selenium...')
        
        self.host             = host
        self.port             = port
        self.start_cmd        = start_cmd
        self.load_timeout     = load_timeout
        self.webpage_language = webpage_language
        self.webpage_currency = webpage_currency
        self.webpage_usrplace = webpage_usrplace
        self.departure_month  = departure_month
        self.departure_year   = departure_year
        self.output_encoding  = output_encoding

        self.num_of_flights = -1

        self.browser = selenium(self.host, self.port, self.start_cmd, self.root_url)

    def prepare_browser(self):

        try:
            self.browser.start()
        except Exception as err:
            self.browser = None
            raise SeleniumError("Can't connect to selenium service. Error message:\r\n{0}".format(str(err)))

        self.browser.open(self.root_url)
        self.browser.delete_all_visible_cookies()
        self.browser.create_cookie(u'scanner=usrplace:::{USRPLACE}&lang:::{LANGUAGE}&currency:::{CURRENCY}&fromCy:::{USRPLACE}&from:::{USRPLACE}'.format(
            LANGUAGE=self.webpage_language,
            CURRENCY=self.webpage_currency,
            USRPLACE=self.webpage_usrplace
            ),
            "path=/")


    def process_page(self, current_point):
    
        url = self.template_url.format(FROM_POINT=current_point,
                                       YEAR=self.departure_year,
                                       MONTH=self.departure_month)

        print('Loading page for {0}...'.format(current_point.upper())),

        self._load_flights_and_wait(url)
        
        print('processing {0} flights...'.format(self.num_of_flights))

        for i in range(1, self.num_of_flights+1):
            point_name = self.browser.get_text("//*[@id=\"browse-data-table\"]/tbody/tr[{0}]/td[1]/a".format(i))
            point_code = self.browser.get_attribute("//*[@id=\"browse-data-table\"]/tbody/tr[{0}]/td[1]/a@href".format(i))
            point_code = urlparse.parse_qs(point_code)['iplace'][0]
            point_code = point_code.lower()
            
            point_price = self.browser.get_text("//*[@id=\"browse-data-table\"]/tbody/tr[{0}]/td[3]/a".format(i))
            point_price = re.sub("[^0-9]", "", point_price)
            try:
                point_price = int(point_price)
            except Exception: # if text
                break # results are sorted

            yield point_name, point_code, point_price
        

    def _load_flights_and_wait(self, url):
    
        self.browser.open(url)
    
        print('waiting for Javascript execution...'),

        self.num_of_flights = 0
        time.sleep(self.load_timeout/3.) # init timeout
        
        for i in range(int(self.load_timeout)):
            self.num_of_flights = self.browser.get_xpath_count("//*[@id=\"browse-data-table\"]/tbody/tr")
            if self.num_of_flights > 0:
                break
            time.sleep(1)
            print("."),
        else:
            print('Warning! No flights detected on the page!')
            return
        
        for i in range(int(self.load_timeout)):
            tmp = self.browser.get_xpath_count("//*[@id=\"browse-data-table\"]/tbody/tr")
            m = self.num_of_flights
            self.num_of_flights = tmp
            
            if m == self.num_of_flights:
                break
            else:
                time.sleep(1)
                print("."),
        else:
            print('Warning! Page not fully loaded!')
            
    
    def close(self):

        if (self.browser != None):
            print('Closing selenium...')

            self.browser.stop()


#__________________________________________________________________

class SeleniumError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
