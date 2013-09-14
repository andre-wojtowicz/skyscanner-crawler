#!/usr/bin/python
# -*- coding: utf-8 -*-

import networkx as nx
from selenium import selenium

import re
import sys
import time
import traceback
import urlparse

#__________________________________________________________________

WEBPAGE_LANGUAGE = "pl"
WEBPAGE_CURRENCY = "pln"
WEBPAGE_USRPLACE = "PL"

DEPARTURE_COUNTRY = "pl"
DEPARTURE_MONTH   = "october"
DEPARTURE_YEAR    = "2013"
PRICE_LIMIT       = 100
FLIGHTS_LIMIT     = 2

SELENIUM_ADDRESS      = "localhost"
SELENIUM_PORT         = 4444
SELENIUM_TYPE         = "*chrome"
SELENIUM_ROOT_URL     = "http://www.skyscanner.net/"
SELENIUM_TEMPLATE_URL = "http://www.skyscanner.net/flights-from/{COUNTRY}/{MONTH}-{YEAR}/"
SELENIUM_LOAD_TIMEOUT = 7.5 # seconds

OUTPUT_ENCODING = "utf-8"

#__________________________________________________________________
    
class Crawler():

    def __init__(self, webpage_language,
                       webpage_currency,
                       webpage_usrplace,
                       departure_country,
                       departure_month,
                       departure_year,
                       price_limit,
                       flights_limit,
                       selenium_address,
                       selenium_port,
                       selenium_type,
                       selenium_root_url,
                       selenium_template_url,
                       selenium_load_timeout,
                       output_encoding):

        print 'Initializing crawler...'

        self.webpage_language      = webpage_language
        self.webpage_currency      = webpage_currency
        self.webpage_usrplace      = webpage_usrplace
        self.departure_country     = departure_country
        self.departure_month       = departure_month
        self.departure_year        = departure_year
        self.price_limit           = price_limit
        self.flights_limit         = flights_limit
        self.selenium_address      = selenium_address
        self.selenium_port         = selenium_port
        self.selenium_type         = selenium_type
        self.selenium_root_url     = selenium_root_url
        self.selenium_template_url = selenium_template_url
        self.selenium_load_timeout = selenium_load_timeout
        self.output_encoding       = output_encoding
        
        self.links          = nx.DiGraph()
        self.country_names  = {}
        self.to_visit       = set()
        self.visited        = set()
        self.num_of_flights = -1
        
    def crawl(self):

        print 'Initializing selenium...'

        self.browser = selenium(self.selenium_address, self.selenium_port, self.selenium_type, self.selenium_root_url)
        try:
            self.browser.start()
        except Exception as err:
            self.browser = None
            raise SeleniumError("Can't connect to selenium service. Error message:\r\n{0}".format(str(err)))

        self.browser.open(self.selenium_root_url)
        self.browser.delete_all_visible_cookies()
        self.browser.create_cookie(u'scanner=usrplace:::{USRPLACE}&lang:::{LANGUAGE}&currency:::{CURRENCY}&fromCy:::{USRPLACE}&from:::{USRPLACE}'.format(
            LANGUAGE=self.webpage_language,
            CURRENCY=self.webpage_currency,
            USRPLACE=self.webpage_usrplace
            ),
            "path=/")
    
        self.links.add_node(self.departure_country)
        self.to_visit.add(self.departure_country)
        
        while len(self.to_visit) > 0:
            print "Countries to check: {0}".format(len(self.to_visit))

            node = self.to_visit.pop()
            self._process_page(node)
            
        costs, paths = nx.single_source_dijkstra(self.links, self.departure_country)
        
        for country in sorted(costs, key=lambda y: costs[y]):
            print self.country_names[country].encode(self.output_encoding), costs[country],

            p = paths[country][1:-1]

            if len(p)>0 :
                print '\tvia',
                for c in p:
                    print self.country_names[c].encode(self.output_encoding),
            print ""
        
    
    def _process_page(self, current_link):
    
        self.visited.add(current_link)
    
        url = self.selenium_template_url.format(COUNTRY=current_link,
                                                YEAR=self.departure_year,
                                                MONTH=self.departure_month)
        self._load_flights_and_wait(url)
        
        print 'Processing {0} flights for {1}...'.format(self.num_of_flights, current_link.upper())

        for i in range(1, self.num_of_flights+1):
            ct = self.browser.get_text("//*[@id=\"browse-data-table\"]/tbody/tr[{0}]/td[1]/a".format(i))
            cd = self.browser.get_attribute("//*[@id=\"browse-data-table\"]/tbody/tr[{0}]/td[1]/a@href".format(i))
            cd = urlparse.parse_qs(cd)['iplace'][0]
            cd = cd.lower()
            self.country_names[cd] = ct
            pr = self.browser.get_text("//*[@id=\"browse-data-table\"]/tbody/tr[{0}]/td[3]/a".format(i))
            pr = re.sub("[^0-9]", "", pr)
            try:
                pr = int(pr)
            except Exception: # if text
            # break instead of continue - page results are sorted
                break
            
            if pr > self.price_limit:
                break
                
            if current_link != self.departure_country:
                if cd in self.links.nodes():
                    if nx.dijkstra_path_length(self.links, self.departure_country, current_link) + pr >= nx.dijkstra_path_length(self.links, self.departure_country, cd):
                        continue
                elif nx.dijkstra_path_length(self.links, self.departure_country, current_link) + pr > self.price_limit:
                    continue
            
            self.links.add_node(cd)
            self.links.add_edge(current_link, cd, label=pr, weight=pr)
            
            if cd not in self.visited:
                self.to_visit.add(cd)
        

    def _load_flights_and_wait(self, url):
    
        print 'Loading page...',
    
        self.browser.open(url)
    
        print 'waiting for Javascript execution...'

        self.num_of_flights = 0
        time.sleep(self.selenium_load_timeout/3.) # init timeout
        
        for i in range(int(self.selenium_load_timeout)):
            self.num_of_flights = self.browser.get_xpath_count("//*[@id=\"browse-data-table\"]/tbody/tr")
            if self.num_of_flights > 0:
                break
            time.sleep(1)
            print "[phase 1] waiting (flights: {0}, round: {1})...".format(self.num_of_flights, i+1)
        else:
            print 'Warning! No flights detected on the page!'
            return
        
        for i in range(int(self.selenium_load_timeout)):
            tmp = self.browser.get_xpath_count("//*[@id=\"browse-data-table\"]/tbody/tr")
            m = self.num_of_flights
            self.num_of_flights = tmp
            
            if m == self.num_of_flights:
                break
            else:
                time.sleep(1)
                print "[phase 2] waiting (flights: {0}, round: {1})...".format(self.num_of_flights, i+1)
        else:
            print 'Page not fully loaded!'
            
    
    def close(self):

        if (self.browser != None):
            print 'Closing selenium...'

            self.browser.stop()


class SeleniumError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
#__________________________________________________________________
    
if __name__ == "__main__":

    c = Crawler(WEBPAGE_LANGUAGE,
                WEBPAGE_CURRENCY,
                WEBPAGE_USRPLACE,
                DEPARTURE_COUNTRY,
                DEPARTURE_MONTH,
                DEPARTURE_YEAR,
                PRICE_LIMIT,
                FLIGHTS_LIMIT,
                SELENIUM_ADDRESS,
                SELENIUM_PORT,
                SELENIUM_TYPE,
                SELENIUM_ROOT_URL,
                SELENIUM_TEMPLATE_URL,
                SELENIUM_LOAD_TIMEOUT,
                OUTPUT_ENCODING)

    try:
        c.crawl()
    except KeyboardInterrupt:
        print "Ctrl-C pressed..."
    except SeleniumError as err:
        print str(err)
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
    finally:
        c.close()