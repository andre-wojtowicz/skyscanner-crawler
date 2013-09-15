# -*- coding: utf-8 -*-

import networkx as nx

class MapAnalyzer(object):

    def __init__(self, webpage_currency, output_encoding):
        
        self.webpage_currency = webpage_currency
        self.output_encoding  = output_encoding


    def list_flights(self, flights_map, price_limit, flights_limit, departure_point):

        print("Flights from {0}:".format(flights_map.points_names[departure_point].encode(self.output_encoding)))

        costs, paths = nx.single_source_dijkstra(flights_map.map, departure_point)
        self._find_cycle_from_dep_point(flights_map.map, departure_point, costs, paths)

        price_w = len(str(max(costs)))
        
        for point in sorted(costs, key=lambda y: costs[y]):
            print("{0:{1}} {2} - {3}".format(costs[point], price_w, self.webpage_currency, flights_map.points_names[point].encode(self.output_encoding))),

            p = paths[point][1:-1]

            if len(p)>0 :
                print('\t( via'),
                for c in p:
                    print(flights_map.points_names[c].encode(self.output_encoding)),
                print(")"),

            print("")

    @staticmethod
    def  _find_cycle_from_dep_point(map, point, costs, paths):

        costs[point] = float("inf")
        
        if map.edge[point].has_key(point):
            costs[point] = map.edge[point][point]["weight"]

        map.add_node("point_copy")

        for p in map.edge[point].copy():
            map.add_edge(p, "point_copy", weight=map.edge[point][p]["weight"])

        copy_cost, copy_path = nx.single_source_dijkstra(map, point, "point_copy")

        if copy_cost["point_copy"] < costs[point]:
            costs[point] = copy_cost["point_copy"]
            paths[point] = copy_path["point_copy"]

        map.remove_node("point_copy")

        if costs[point] == float("inf"):
            costs.pop(point, None)