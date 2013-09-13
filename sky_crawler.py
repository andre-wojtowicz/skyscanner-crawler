import networkx as nx
from selenium import selenium

import re
import urlparse
import time
import traceback
import sys

#__________________________________________________________________

TPL_URL = "http://www.skyscanner.net/flights-from/{COUNTRY}/{MONTH}-{YEAR}/"
INIT_COUNTRY = "pl"
INIT_MONTH = "september"
INIT_YEAR = "2013"
PRICE_LIMIT = 100
MAX_FLIGHTS = 2
CRAWL_TIMEOUT = 7.5 # seconds

WEB_LANGUAGE = "pl"
WEB_CURRENCY = "pln"
WEB_USRPLACE = "PL"

#__________________________________________________________________
    
class Crawler():

    def __init__(self, tpl_url, init_country, init_month, init_year,
                       price_limit, max_flights, crawl_timeout):
        print 'Initializing crawler...'
        self.tpl_url = tpl_url
        self.init_country  = init_country
        self.init_month    = init_month
        self.init_year     = init_year
        self.price_limit   = price_limit
        self.depth         = max_flights
        self.crawl_timeout = int(crawl_timeout)
        
        self.links = nx.DiGraph()
        self.country_names = {}
        self.to_visit = set()
        self.visited = set()
        
    def crawl(self):
        print 'Initializing selenium...'
        self.browser = selenium("localhost", 4444, "*chrome", "http://www.skyscanner.net/")
        self.browser.start()
        self.browser.open("http://www.skyscanner.net/")
        self.browser.delete_all_visible_cookies()
        self.browser.create_cookie(u'scanner=usrplace:::{WEB_USRPLACE}&lang:::{WEB_LANGUAGE}&currency:::{WEB_CURRENCY}&fromCy:::{WEB_USRPLACE}&from:::{WEB_USRPLACE}'.format(
            WEB_LANGUAGE=WEB_LANGUAGE,
            WEB_CURRENCY=WEB_CURRENCY,
            WEB_USRPLACE=WEB_USRPLACE
            ),
            "path=/")
    
        self.links.add_node(self.init_country)
        self.to_visit.add(self.init_country)
        
        while len(self.to_visit) > 0:
            node = self.to_visit.pop()
            self._process_page(node)
            
        
        costs, paths = nx.single_source_dijkstra(self.links, self.init_country)
        
        for country in sorted(costs, key=lambda y: costs[y]):
            print self.country_names[country], costs[country],

            p = paths[country][1:-1]
            if len(p)>0:
                print '\tvia',
                for c in p:
                    print self.country_names[c],
            print ""
        
    
    def _process_page(self, current_link):
    
        self.visited.add(current_link)
    
        url = self.tpl_url.format(COUNTRY=current_link,
                                  YEAR=self.init_year,
                                  MONTH=self.init_month)
        self._load_flights_and_wait(url)
        
        print 'Extracting {0} flights for {1}...'.format(self.num_of_flights, current_link)

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
                
            if current_link != self.init_country:
                if cd in self.links.nodes():
                    if nx.dijkstra_path_length(self.links, self.init_country, current_link) + pr >= nx.dijkstra_path_length(self.links, self.init_country, cd):
                        continue
                elif nx.dijkstra_path_length(self.links, self.init_country, current_link) + pr > self.price_limit:
                    continue
            
            self.links.add_node(cd)
            self.links.add_edge(current_link, cd, label=pr, weight=pr)
            
            if cd not in self.visited:
                self.to_visit.add(cd)
        

    def _load_flights_and_wait(self, url):
    
        print 'Loading page...'
    
        self.browser.open(url)
    
        print 'Waiting for Javascript execution...'

        self.num_of_flights = 0
        time.sleep(self.crawl_timeout/3.) # init timeout
        
        for i in range(self.crawl_timeout):
            self.num_of_flights = self.browser.get_xpath_count("//*[@id=\"browse-data-table\"]/tbody/tr")
            if self.num_of_flights > 0:
                break
            time.sleep(1)
            print "[phase 1] waiting (flights: {0}, tour: {1})...".format(self.num_of_flights, i+1)
        else:
            print 'Warning! No flights detected on the page!'
            return
        
        for i in range(self.crawl_timeout):
            tmp = self.browser.get_xpath_count("//*[@id=\"browse-data-table\"]/tbody/tr")
            m = self.num_of_flights
            self.num_of_flights = tmp
            
            if m == self.num_of_flights:
                break
            else:
                time.sleep(1)
                print "[phase 2] waiting (flights: {0}, tour: {1})...".format(self.num_of_flights, i+1)
        else:
            print 'Page not fully loaded!'
            
    
    def close(self):
        print 'Closing selenium...'
        self.browser.stop()
#__________________________________________________________________
    
if __name__ == "__main__":
    c = Crawler(TPL_URL, INIT_COUNTRY, INIT_MONTH, INIT_YEAR,
                PRICE_LIMIT, MAX_FLIGHTS, CRAWL_TIMEOUT)
    try:
        c.crawl()
    except KeyboardInterrupt:
        print "Ctrl-C pressed..."
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
    finally:
        c.close()