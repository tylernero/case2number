import sys
sys.path.append('..')
import pickle
import math
import csv
import dbQuery as db
from warehouse import Warehouse, ZipCode
from start import ZipCodesData
 


class Network(object):
    """main class for managing the network demand"""
    def __init__(self, pickle=False):
        if pickle == False:
            warehouse_zips = db.getDataFromString('exec dbo.facility')[:100]
            zip_data_class = ZipCodesData()
            self.distribution_centers(zip_data_class)
            self.warehouses = []
            self.warehouses.extend(self.dcs)
            self.ranking = Ranking()
            for i in warehouse_zips:
                self.warehouses.append(Warehouse(i[0], i[1], i[2], i[3], i[4], i[5]))
            zips = db.getDataFromString('exec dbo.zipcode')
            self.zips = {}
            dc_cords = []
            for i in self.dcs:
                dc_cords.append(i.get_cordinates())
            for i in self.warehouses:
                dc_cords.append(i.get_cordinates())
            for i in zips:
                try:
                    int(i[0][:5])
                    zip = ('00000' + str(i[0][:5]))[-5:]
                except:
                    zip = i[0]
                cords = zip_data_class.get_cordinates(zip)
                state = zip_data_class.get_state(zip)
                self.zips[zip] = ZipCode(zip, cords, state)
                self.zips[zip].get_serviceable_array(dc_cords)
        else:
            self.pickle_load()
    def pickle(self):
        try:
            pickle.dump(self.warehouses, open('pickle/net_ware.p', 'wb'))
        except:
            print("warehouse dump failed")
        try:
            pickle.dump(self.zips, open('pickle/net_zips.p', 'wb'))
        except:
            print("zips dump failes")
        try:
            pickle.dump(self.dcs, open('pickle/net_dcs.p', 'wb'))
        except:
            print("dcs dump failed")
        try:
            pickle.dump(self.ranking, open('pickle/net_rank.p', 'wb'))
        except:
            print("ranking dump failed")

    def pickle_load(self):
        try:
            self.warehouses = pickle.load(open('pickle/net_ware.p', 'rb'))
        except:
            print("warehouse load failed")
        try:
            self.zips = pickle.load(open('pickle/net_zips.p', 'rb'))
        except:
            print("zips load failes")
        try:
            self.dcs = pickle.load(open('pickle/net_dcs.p', 'rb'))
        except:
            print "dcs load failes"
        try:
            self.ranking = pickle.load(open('pickle/net_rack.p', 'rb'))
        except:
            print " ranking load failed"

    def construct_demand_Matrix(self, zip_dict):
        """breaks down demand by indivual zipcode sets"""
        demand_dict = [0]*len(self.zips)
        for zip, data in zip_dict.iteritems():
            try:
                zip_string = str(ZipCodesData.convert_zip_name(zip))
                set_index = self.zips[zip_string].serviceable_array
                demands = self.zips[zip_string].get_demand_arrays(data)
                i = 0
                while i < len(set_index):
                    demand_dict[set_index[i]] += demands[i]
                    i += 1
            except KeyError:
                pass
        return demand_dict
    def distribution_centers(self, zipcodes):
        """created self.dcs object"""
        dcs = [['Sainte-Croix', 'G0S 2H0'], ['Coaticook', 'J1A 1Z5'], ['Juarez', '31000']\
        , ['Nashville', '37011'], ['Salt Lake', '84044']]
        self.dcs = []
        for i in dcs:
            cords = zipcodes.get_cordinates(i[1])
            self.dcs.append(Warehouse(i[0], i[1], 2, 4, cords[0], cords[1]))

    def get_nearest(self, lat, long):
        """used for find the dc to service a fc"""
        dist = 100000
        index = 0
        j = 0
        for i in self.dcs:
            new_dist = ZipCodesData.distance_on_sphere(lat, long, i.lat, i.long)
            if new_dist < dist:
                dist = new_dist
                index = j
            j += 1
        return index
    def simulate_a_dy_dist(self):
        demand = db.getDataFromString("execute dbo.get_daily_sales '1/1/2016'")
        array = []
        for i in demand:
            clean = str(ZipCodesData.convert_zip_name(i[1]))
            rank = self.ranking.get_leadtime(i[0], self.zips[clean].state)
            lead_time = self.zips[clean].gen_lead_time(rank)
            try:
                ware_rank = self.zips[clean].serviceable_array[lead_time]
            except:
                ware_rank = 'nope'
            cur = i
            cur.extend([ware_rank, lead_time, ware_rank if ware_rank == 'nope' else self.warehouses[ware_rank].zipcode])
            array.append(cur)
        with open('day_of_dist.csv', 'wb') as csv_file:
            writer =  csv.writer(csv_file)
            writer.writerows(array)



def demand_all(demand_dict, network):
    """takes a dict of forecasts and transform into warehouse """
    warehouse_demand = {}
    for sku, sku_data in demand_dict.iteritems():
        warehouse_demand[sku] = []
        for i in range(0, len(network.warehouses)):
            warehouse_demand[sku].append([0, 0])
        for i in sku_data.keys():
            try:
                clean = ZipCodesData.convert_zip_name(i)
                rank = network.ranking.get_leadtime(clean, network.zips[clean].state)
                set_demand = network.zips[str(clean)].get_demand_arrays(sku_data[i])
                for j in range(0, len(set_demand[1])):
                    try:
                        warehouse_demand[sku][set_demand[1][j]][0] += set_demand[0][j]
                        warehouse_demand[sku][set_demand[1][j]][1] += (math.sqrt(set_demand[0][j]))**2
                    except:
                        pass
            except KeyError:
                pass
    return warehouse_demand



def get_demand_per_dc():
    """calculates expected demand per dc based on fcs servered"""
    network = Network(pickle=True)
    for i in network.warehouses:
        k = i.inventory
        lat = i.lat
        longi = i.long
        index = network.get_nearest(lat, longi)
        for j in k.keys():
            network.dcs[index].add_inventory(j, i.inventory[j])
    network.pickle()

def dump_dc():
    """geneerate csv for expected demand per fc"""
    network = Network(pickle=True)
    skus = {}
    for i in range(0, len(network.dcs)):
        for j in network.dcs[i].inventory.keys():
            if j not in skus:
                skus[j] = [0, 0, 0, 0, 0]
                skus[j][i] += network.dcs[i].inventory[j]
            else:
                skus[j][i] += network.dcs[i].inventory[j]
    arr = []
    for i in skus.keys():
        arr.append([i,skus[i][0], skus[i][1], skus[i][2], skus[i][3], skus[i][4]])
    with open('dc_inv.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(arr)

class Ranking(object):
    def __init__(self):
        """class for stroring rank of sku/states"""
        array = db.getDataFromString("execute [dbo].[ranking] '1/1/2016', 365")
        self.ranking = {}
        for i in array:
            if i[0] not in self.ranking:
                self.ranking[i[0]] = {}
            self.ranking[i[0]][i[1]] = i[2]
    def get_leadtime(self, state, sku):
        """get additional lead time based on sku state ranking"""
        try:
            rank = self.ranking[sku][state]
            if rank == 'TOP 10':
                return 0
            elif rank == 'MIDDLE 50':
                return 1
            else:
                return 2
        except:
            return 2