# -*- coding: utf-8 -*-

from SeleniumWrapper import *
from FlightsMap import *
from MapAnalyzer import *

#__________________________________________________________________


class Crawler(object):
    
    def __init__(self, webpage_language,
                       webpage_currency,
                       webpage_usrplace,
                       departure_point,
                       ignored_points,
                       departure_month,
                       departure_year,
                       price_limit,
                       flights_limit,
                       selenium_host,
                       selenium_port,
                       selenium_start_cmd,
                       selenium_load_timeout,
                       map_save_to_dot,
                       map_dot_filename,
                       output_encoding):

        print('Initializing crawler...')

        self.selenium_wrapper = SeleniumWrapper(selenium_host,
                                                selenium_port,
                                                selenium_start_cmd,
                                                selenium_load_timeout,
                                                webpage_language,
                                                webpage_currency,
                                                webpage_usrplace,
                                                departure_month,
                                                departure_year,
                                                output_encoding)

        self.flights_map  = FlightsMap(price_limit, departure_point, ignored_points)
        self.map_analyzer = MapAnalyzer(webpage_currency, output_encoding)

        self.departure_point  = departure_point
        self.price_limit      = price_limit
        self.flights_limit    = flights_limit
        self.map_save_to_dot  = map_save_to_dot
        self.map_dot_filename = map_dot_filename
        self.output_encoding  = output_encoding
        
    def create_map(self):
        
        while self.flights_map.points_to_visit() > 0:
            print("Points to check: {0}".format(self.flights_map.points_to_visit()))

            from_point = self.flights_map.pop_next_to_visit()
            self.flights_map.add_to_visited(from_point)

            for to_point_name, to_point_code, to_point_price in self.selenium_wrapper.process_page(from_point):
                if not self.flights_map.process_connection(from_point, to_point_name, to_point_code, to_point_price):
                    break

    def analyze_map(self):

        self.map_analyzer.list_flights(self.flights_map,
                                       self.price_limit, 
                                       self.flights_limit, 
                                       self.departure_point)

        if (self.map_save_to_dot):
            try:
                self.flights_map.save_as_dot(self.map_dot_filename)
            except Exception as err:
                print("Can't save map as dot file. Error message: {0}".format(str(err)))
        
    def cleanup(self):

        self.selenium_wrapper.close()
    
