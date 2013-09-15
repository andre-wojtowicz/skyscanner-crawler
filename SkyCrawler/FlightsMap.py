# -*- coding: utf-8 -*-

import networkx as nx

class FlightsMap(object):

    def __init__(self, price_limit, departure_point):
        
        self.price_limit     = price_limit
        self.departure_point = departure_point

        self.map            = nx.DiGraph()
        self.points_names   = {}
        self.to_visit       = set()
        self.visited        = set()

        self.map.add_node(self.departure_point)
        self.to_visit.add(self.departure_point)

    def process_connection(self, from_point, to_point_name, to_point_code, to_point_price):

        self.points_names[to_point_code] = to_point_name
            
        if to_point_price > self.price_limit:
            return False # break
                
        if from_point != self.departure_point:
            if to_point_code in self.map.nodes():
                if nx.dijkstra_path_length(self.map, self.departure_point, from_point) + to_point_price >= nx.dijkstra_path_length(self.map, self.departure_point, to_point_code):
                    return True # continue
            elif nx.dijkstra_path_length(self.map, self.departure_point, from_point) + to_point_price > self.price_limit:
                return True # continue
            
        self.map.add_node(to_point_code)
        self.map.add_edge(from_point, to_point_code, label=to_point_price, weight=to_point_price)
            
        if to_point_code not in self.visited:
            self.to_visit.add(to_point_code)

        return True # continue


    def points_to_visit(self):

        return len(self.to_visit)

    def pop_next_to_visit(self):

        return self.to_visit.pop()

    def add_to_visited(self, point):

        self.visited.add(point)

    def save_as_dot(self, filename):

        nx.write_dot(self.map, filename)
        # pygraphviz required
        # conversion e.g.: neato -Tps grid.dot > grid.ps
