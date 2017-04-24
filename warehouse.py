import sys
sys.path.append('..')
import pickle
import dbQuery as db
import math
import numpy as np
import random
import start as s
from start import ZipCodesData
import csv


class Warehouse(object):
    """stores warehouse data and inventory"""
    def __init__(self, city, zipcode, labor_cost, storage, lat, long):
        self.zipcode = zipcode
        self.labor_cost = labor_cost
        self.storage = storage
        self.lat = lat
        self.long = long
        self.inventory = {}
    def get_cordinates(self):
        return [self.lat, self.long]
    def add_inventory(self, part, qty):
        if part not in self.inventory:
            self.inventory[part] = 0
        self.inventory[part] += qty
    def remove_inventory(self, part, qty):
        if qty <= self.inventory[part]:
            self.inventory[part] -= qty
            return qty
        else:
            qty = self.inventory[part]
            self.inventory[part] = 0
            return qty
    def get_inventory(self, sku):
        try:
            return self.inventory[sku]
        except KeyError:
            return 0

def get_replenishments(warehouse_demand, cross_demand, warehouses):
    """calculates replensihments"""
    shortage = {}
    for i in warehouse_demand.keys():
        shortage[i] = []
        for k in range(0, len(warehouses)):
            shortage[i].append(0)
        for j in range(0, len(warehouse_demand[i])):
            shortage[i][j] += (warehouse_demand[i][j][0] + math.sqrt(warehouse_demand[i][j][1]))  - warehouses[j].get_inventory(i)
    return shortage

class ZipCode(object):
    """class handles zipcode demand and servicable warehouses"""
    def __init__(self, zipcode, cords, state):
        """init class with lat and long"""
        self.lat = cords[0]
        self.long = cords[1]
        self.state = state
    def get_serviceable_array(self,cords):
        """create the arrays of servicable warehouses"""
        distance_a_day = [250, 800, 1400, 2000, 2600, 3200, 3800, 4400, 5000, 5600]
        self.serviceable_array = []
        for i in distance_a_day:
            for j in range(0,len(cords)):
                dist = s.ZipCodesData.distance_on_sphere(self.lat, self.long, cords[j][0], cords[j][1])
                if dist < i:
                    self.serviceable_array.append(j)
                    break
        return self.serviceable_array 
    def addArrayIndex(self, index_array):
        """adds array index of demands from networkmatrix"""
        self.index_array = index_array
    def get_demand_arrays(self, qty, rank=0):
        """calculates the demand for each set of warehouses"""
        demand_array = [qty] * len(self.serviceable_array)
        i = 0
        if rank == 0:
            demands = [.25, .25, .20, .1, .5, .5, .5, .5, 0, 0]
        elif rank == 0:
            demands =  [0, .25, .25, .20, .1, .5, .5, .5, .5, 0]
        else:
            demands =  [0, 0, .25, .25, .20, .1, .5, .5, .5, .5]
        while i < len(demand_array):
            demand_array[i] = demand_array[i] * demands[i]
            i += 1
        return (demand_array, self.serviceable_array)
    def gen_lead_time(self, rank=0):
        """simulate the lead time for an order"""
        i = 0
        if rank == 0:
            demands = [.25, .25, .20, .1, .5, .5, .5, .5, 0, 0]
        elif rank == 1:
            demands =  [0, .25, .25, .20, .1, .5, .5, .5, .5, 0]
        else:
            demands =  [0, 0, .25, .25, .20, .1, .5, .5, .5, .5]
        ran = random.uniform(0, 1)
        while i < len(demands):
            if ran < sum(demands[:i]):
                return i
            i += 1