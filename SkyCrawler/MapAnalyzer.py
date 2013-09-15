# -*- coding: utf-8 -*-

import networkx as nx

class MapAnalyzer(object):

    def __init__(self, webpage_currency, output_encoding):
        
        self.webpage_currency = webpage_currency
        self.output_encoding  = output_encoding


    def list_flights(self, flights_map, price_limit, flights_limit, departure_point):

        costs, paths = nx.single_source_dijkstra(flights_map.map, departure_point)
        price_w = len(str(max(costs)))
        
        for country in sorted(costs, key=lambda y: costs[y]):
            print("{0:{1}} {2} - {3}".format(costs[country], price_w, self.webpage_currency, flights_map.points_names[country].encode(self.output_encoding))),

            p = paths[country][1:-1]

            if len(p)>0 :
                print('\t( via'),
                for c in p:
                    print(flights_map.points_names[c].encode(self.output_encoding)),
                print(")"),

            print("")
        