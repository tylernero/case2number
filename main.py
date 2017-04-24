from fore_cast import fore_cast
from network import Network, demand_all
from warehouse import get_replenishments
import math
import pickle


network = Network()
fore = fore_cast('1/1/2015')
fore.create_forecast_dict()
demand_dict = fore.fore_cast
warehouse_demand = demand_all(demand_dict, network)
intial_inv = get_replenishments(warehouse_demand, network.net_matrix.cross_demand, network.warehouses)

for i, j in intial_inv.iteritems():
    for k in range(0, len(j)):
        network.warehouses[k].add_inventory(i, math.ceil(j[k]))

network.pickle()
