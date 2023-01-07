import csv
import random
import sys

sys.path.append(".")
import glob
import os

import numpy as np
from supply_chain_network import SupplyChainNetwork
from supply_chain_network.optimizers import HybridAlgorithm, LPModel
from supply_chain_network.config import AppConfig
from supply_chain_network.facilities import warehouses
from supply_chain_network.optimizers.utils import Solution
from supply_chain_network.utils import get_three_random_weights
from xlsxwriter.workbook import Workbook

AppConfig.configure(config_file_path="experiments/three_facilities/config.ini")

seed = 1

np.random.seed(seed)
random.seed(seed)

facilities_count = 3
markets_count = 10
products_count = 4
raw_materials_count = 4

N = facilities_count * 4 + markets_count


tabu_size = 5

T = 50
Tf = 1

alpha = 0.9

K = int(0.5 * N)


net = SupplyChainNetwork(
    facilities_count=facilities_count,
    raw_materials_count=raw_materials_count,
    markets_count=markets_count,
    products_count=products_count,
)
net.initialize_random_network()
net.apply_initial_greedy_solution()


def export(filename, rows, add_header=True):
    os.system("mkdir -p scripts/net_to_csv/")
    with open(f"scripts/net_to_csv/{filename}.csv", "w") as file:
        writer = csv.writer(file)
        if add_header:
            writer.writerow(["", *range(1, len(rows[0]) + 1)])
        [writer.writerow([index, *row]) for index, row in enumerate(rows, start=1)]


# export demand
export(filename="d", rows=[market.products_demand for market in net.markets_echelon])

# export dist center capacity for each product
export(
    filename="dccap",
    rows=[dist_center.capacity for dist_center in net.distribution_centers_echelon],
)

# export distance between dist centers and warehouses
"""NOTE: these distances seems to be not consistent with the excel file"""
# export(
#     filename="distdcw",
#     rows=[warehouse.dist_centers_distances for warehouse in net.warehouses_echelon],
# )
export(
    filename="distwdc",
    rows=[warehouse.dist_centers_distances for warehouse in net.warehouses_echelon],
)

# export distance between factory/plant to warehouses
# export(
#     filename="distfdc",
#     rows=[plant.warehouses_distances for plant in net.plants_echelon],
# )
export(
    filename="distfw",
    rows=[plant.warehouses_distances for plant in net.plants_echelon],
)


# export distance between supplier to factory/plant
"""NOTE: Numbers are not consistent"""
export(
    filename="distspf",
    rows=[supplier.plants_distances for supplier in net.suppliers_echelon],
)

# export distance between dist centers and customers
# export(
#     filename="distws",
#     rows=[
#         dist_center.market_distances for dist_center in net.distribution_centers_echelon
#     ],
# )
export(
    filename="distdcs",
    rows=[
        dist_center.market_distances for dist_center in net.distribution_centers_echelon
    ],
)


# export env impact of opening dist center
"""NOTE: Numbers are not consistent"""
export(
    filename="ED",
    rows=[
        [dist_center.opening_env_impact]
        for dist_center in net.distribution_centers_echelon
    ],
    add_header=False,
)

# export env impact of opening plant
"""NOTE: Numbers are not consistent"""
export(
    filename="EF",
    rows=[[plant.opening_env_impact] for plant in net.plants_echelon],
    add_header=False,
)

# export production env impact for plants
"""NOTE: Numbers are not consistent"""
export(
    filename="EP",
    rows=[plant.products_env_impact for plant in net.plants_echelon],
)

# export trans env impact from warehouse to dist center
# HOW??
# numbers are very different!!
export(
    filename="ETW",
    rows=[
        [
            # sum(
            #     [
            #         product_impact
            #         for product_impact in warehouse.products_trans_env_impact[
            #             dist_center_index
            #         ]
            #     ]
            # )
            warehouse.products_trans_env_impact[dist_center_index][0]
            * dist_center_distance
            for dist_center_index, dist_center_distance in enumerate(
                warehouse.dist_centers_distances,
            )
        ]
        for warehouse in net.warehouses_echelon
    ],
)

# export trans env impact from plants to warehouse
export(
    filename="ETF",
    rows=[
        [
            # sum(
            #     [
            #         product_trans_impact
            #         for product_trans_impact in plant.products_trans_env_impact[
            #             warehouse_index
            #         ]
            #     ]
            # )
            plant.products_trans_env_impact[warehouse_index][0] * warehouse_distance
            for warehouse_index, warehouse_distance in enumerate(
                plant.warehouses_distances
            )
        ]
        for plant in net.plants_echelon
    ],
)
# export trans env impact from suppliers to plants
export(
    filename="ETS",
    rows=[
        [
            # sum(
            #     [
            #         material_impact
            #         for material_impact in supplier.material_trans_env_impact[
            #             plant_index
            #         ]
            #     ]
            # )
            supplier.material_trans_env_impact[plant_index][0] * plant_distance
            for plant_index, plant_distance in enumerate(supplier.plants_distances)
        ]
        for supplier in net.suppliers_echelon
    ],
)

# export trans env impact from dist to markets
export(
    filename="ETD",
    rows=[
        [
            # sum(
            #     [
            #         product_impact
            #         for product_impact in dist_center.products_trans_env_impact[
            #             market_index
            #         ]
            #     ]
            # )
            dist_center.products_trans_env_impact[market_index][0] * market_distance
            for market_index, market_distance in enumerate(dist_center.market_distances)
        ]
        for dist_center in net.distribution_centers_echelon
    ],
)

# export production env impact for plants
"""NOTE: Numbers are not consistent"""
export(
    filename="EW",
    rows=[[warehouse.opening_env_impact] for warehouse in net.warehouses_echelon],
    add_header=False,
)

# export fixed dist center cost
export(
    filename="fdccost",
    rows=[[dist_center.fixed_cost] for dist_center in net.distribution_centers_echelon],
    add_header=False,
)

# export fixed plants cost
export(
    filename="ffcost",
    rows=[[plant.fixed_cost] for plant in net.plants_echelon],
    add_header=False,
)

# export fixed warehoses cost
export(
    filename="fwcost",
    rows=[[warehouse.fixed_cost] for warehouse in net.warehouses_echelon],
    add_header=False,
)

# export products capacity
export(
    filename="pcap",
    rows=[plant.product_capacity for plant in net.plants_echelon],
)

# export products production cost
export(
    filename="pcost",
    rows=[plant.products_prod_cost for plant in net.plants_echelon],
)

# export selling prices
# export(
#     filename="Pricews",
#     rows=[
#         [
#             products_prices[0]  # all products have the same price
#             for products_prices in dist_center.selling_prices.values()
#         ]
#         for dist_center in net.distribution_centers_echelon
#     ],
# )
export(
    filename="Pricedcs",
    rows=[
        [
            products_prices[0]  # all products have the same price
            for products_prices in dist_center.selling_prices.values()
        ]
        for dist_center in net.distribution_centers_echelon
    ],
)

# export purchase cost
export(
    filename="pucost",
    rows=[supplier.material_purchase_cost for supplier in net.suppliers_echelon],
)

# export supplier capacity
export(filename="spcap", rows=[supplier.capacity for supplier in net.suppliers_echelon])


# def sum_trans_costs(echelon, cost_attr="products_trans_cost"):
#     costs = []
#     for product_index in range(len(getattr(echelon[0], cost_attr)[0])):
#         product_cost = 0
#         for facility in echelon:
#             for target_facility_key in getattr(facility, cost_attr).keys():
#                 product_cost += getattr(facility, cost_attr)[target_facility_key][
#                     product_index
#                 ]
#         costs.append([product_cost])
#     return costs


# export transportation cost between warehouses and dist centers
# export(
#     filename="tcostdcw",
#     rows=[
#         [prod_trans_cost]
#         for prod_trans_cost in net.warehouses_echelon[0].products_trans_cost[0]
#     ],  # it is the same for all dist_centers
#     add_header=False,
# )
export(
    filename="tcostwdc",
    rows=[
        [prod_trans_cost]
        for prod_trans_cost in net.warehouses_echelon[0].products_trans_cost[0]
    ],  # it is the same for all dist_centers
    add_header=False,
)

# export transportation cost between plants and warehouses
# export(
#     filename="tcostfdc",
#     rows=[
#         [prod_trans_cost]
#         for prod_trans_cost in net.plants_echelon[0].products_trans_cost[0]
#     ],
#     add_header=False,
# )
export(
    filename="tcostfw",
    rows=[
        [prod_trans_cost]
        for prod_trans_cost in net.plants_echelon[0].products_trans_cost[0]
    ],
    add_header=False,
)

# export transportation cost between suppliers and plants
export(
    filename="tcostspf",
    rows=[
        [prod_trans_cost]
        for prod_trans_cost in net.suppliers_echelon[0].material_trans_cost[0]
    ],
    add_header=False,
)

# export transportation cost between dist centers and customers
# export(
#     filename="tcostws",
#     rows=[
#         [prod_trans_cost]
#         for prod_trans_cost in net.distribution_centers_echelon[0].products_trans_cost[
#             0
#         ]
#     ],
#     add_header=False,
# )
export(
    filename="tcostdcs",
    rows=[
        [prod_trans_cost]
        for prod_trans_cost in net.distribution_centers_echelon[0].products_trans_cost[
            0
        ]
    ],
    add_header=False,
)

# export total delivery risk for Zk (see the objective function Z2)
export(
    filename="Total_delivery_risk_DC",
    rows=[
        [
            product_prop_delivery_risk * product_delivery_risk_impact
            for product_prop_delivery_risk, product_delivery_risk_impact in zip(
                dist_center.prop_delivery_risk,
                dist_center.delivery_risk_impact,
            )
        ]
        for dist_center in net.distribution_centers_echelon
    ],
)

# export total delivery risk for Yj (see the objective function Z2)
export(
    filename="Total_delivery_risk_w",
    rows=[
        [
            product_prop_delivery_risk * product_delivery_risk_impact
            for product_prop_delivery_risk, product_delivery_risk_impact in zip(
                warehouse.prop_delivery_risk,
                warehouse.delivery_risk_impact,
            )
        ]
        for warehouse in net.warehouses_echelon
    ],
)

# export total delivery risk for Xi (see the objective function Z2)
export(
    filename="Total_impact_risk_P",
    rows=[
        [
            product_prop_delivery_risk * product_delivery_risk_impact
            + product_prop_quality_risk * product_quality_risk_impact
            + product_prop_delivery_risk
            * product_prop_quality_risk
            * max(product_delivery_risk_impact, product_quality_risk_impact)
            for product_prop_delivery_risk, product_delivery_risk_impact, product_prop_quality_risk, product_quality_risk_impact in zip(
                plant.prop_delivery_risk,
                plant.delivery_risk_impact,
                plant.prop_quality_risk,
                plant.quality_risk_impact,
            )
        ]
        for plant in net.plants_echelon
    ],
)

# export total delivery risk for Us (see the objective function Z2)
export(
    filename="Total_impact_risk1",
    rows=[
        [
            material_prop_delivery_risk * material_delivery_risk_impact
            + material_prop_quality_risk * material_quality_risk_impact
            + material_prop_delivery_risk
            * material_prop_quality_risk
            * max(material_delivery_risk_impact, material_quality_risk_impact)
            for material_prop_delivery_risk, material_delivery_risk_impact, material_prop_quality_risk, material_quality_risk_impact in zip(
                supplier.prop_delivery_risk,
                supplier.delivery_risk_impact,
                supplier.prop_quality_risk,
                supplier.quality_risk_impact,
            )
        ]
        for supplier in net.suppliers_echelon
    ],
)

# export warehouse capacity
export(
    filename="wcap", rows=[warehouse.capacity for warehouse in net.warehouses_echelon]
)


""" change the csv to excel """
os.system("mkdir -p scripts/net_to_excel/")
for csvfile in glob.glob(os.path.join("scripts/net_to_csv/", "*.csv")):
    filename = csvfile.split("/")[-1]
    workbook = Workbook(
        f"scripts/net_to_excel/{''.join(filename.split('.')[:-1])}.xlsx",
        {"strings_to_numbers": True},
    )
    worksheet = workbook.add_worksheet()
    worksheet.name = "sheet1"
    with open(csvfile, "rt", encoding="utf8") as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()
