from network import Network, get_demand_per_dc, demand_all, dump_dc
from start import ZipCodesData
import sim_fun as fun
from fore_cast import fore_cast


#intialize
net = Network(pickle=False)
calander = fun.Datey()
fore = fore_cast(calander.get_date())
demand_dict = fore.create_forecast_dict()
warehouse_demand = demand_all(demand_dict, net)
for i in warehouse_demand.keys():
    for j in range(0,len(warehouse_demand[i])):
        net.warehouses[j].add_inventory(i, warehouse_demand[i][j][0])
zips = ZipCodesData()
net.distribution_centers(zips)
net.pickle()
get_demand_per_dc()
dump_dc()



