import csv
import glob
import os
import sys
import pandas as pd
from xlsxwriter.workbook import Workbook

sys.path.append(".")

class NetworkExporter:
    def __init__(self,network,output_path):
        self.network = network
        self.output_path = output_path

    def export_to_file(self, filename, rows, add_header=True):
        with open(f"{self.output_path}/{filename}.csv", "w") as file:
            writer = csv.writer(file)
            if add_header:
                writer.writerow(["", *range(1, len(rows[0]) + 1)])
            [writer.writerow([index, *row]) for index, row in enumerate(rows, start=1)]
            
    def export(self):
        
        # export demand
        self.export_to_file(filename="d", rows=[market.products_demand for market in self.network.markets_echelon])

        # export dist center capacity for each product
        self.export_to_file(
            filename="dccap",
            rows=[dist_center.capacity for dist_center in self.network.distribution_centers_echelon],
        )

        # export distance between dist centers and warehouses
        self.export_to_file(
            filename="distwdc",
            rows=[warehouse.dist_centers_distances for warehouse in self.network.warehouses_echelon],
        )

        # export distance between factory/plant to warehouses
        self.export_to_file(
            filename="distfw",
            rows=[plant.warehouses_distances for plant in self.network.plants_echelon],
        )


        # export distance between supplier to factory/plant
        self.export_to_file(
            filename="distspf",
            rows=[supplier.plants_distances for supplier in self.network.suppliers_echelon],
        )

        self.export_to_file(
            filename="distdcs",
            rows=[
                dist_center.market_distances for dist_center in self.network.distribution_centers_echelon
            ],
        )


        # export env impact of opening dist center
        self.export_to_file(
            filename="ED",
            rows=[
                [dist_center.opening_env_impact]
                for dist_center in self.network.distribution_centers_echelon
            ],
            add_header=False,
        )

        # export env impact of opening plant
        self.export_to_file(
            filename="EF",
            rows=[[plant.opening_env_impact] for plant in self.network.plants_echelon],
            add_header=False,
        )

        # export production env impact for plants
        self.export_to_file(
            filename="EP",
            rows=[plant.products_env_impact for plant in self.network.plants_echelon],
        )

        # export trans env impact from warehouse to dist center
        self.export_to_file(
            filename="ETW",
            rows=[
                [
                    warehouse.products_trans_env_impact[dist_center_index][0]
                    * dist_center_distance
                    for dist_center_index, dist_center_distance in enumerate(
                        warehouse.dist_centers_distances,
                    )
                ]
                for warehouse in self.network.warehouses_echelon
            ],
        )

        # export trans env impact from plants to warehouse
        self.export_to_file(
            filename="ETF",
            rows=[
                [
                    plant.products_trans_env_impact[warehouse_index][0] * warehouse_distance
                    for warehouse_index, warehouse_distance in enumerate(
                        plant.warehouses_distances
                    )
                ]
                for plant in self.network.plants_echelon
            ],
        )
        # export trans env impact from suppliers to plants
        self.export_to_file(
            filename="ETS",
            rows=[
                [
                    supplier.material_trans_env_impact[plant_index][0] * plant_distance
                    for plant_index, plant_distance in enumerate(supplier.plants_distances)
                ]
                for supplier in self.network.suppliers_echelon
            ],
        )

        # export trans env impact from dist to markets
        self.export_to_file(
            filename="ETD",
            rows=[
                [
                    dist_center.products_trans_env_impact[market_index][0] * market_distance
                    for market_index, market_distance in enumerate(dist_center.market_distances)
                ]
                for dist_center in self.network.distribution_centers_echelon
            ],
        )

        # export production env impact for plants
        """NOTE: Numbers are not consistent"""
        self.export_to_file(
            filename="EW",
            rows=[[warehouse.opening_env_impact] for warehouse in self.network.warehouses_echelon],
            add_header=False,
        )

        # export fixed dist center cost
        self.export_to_file(
            filename="fdccost",
            rows=[[dist_center.fixed_cost] for dist_center in self.network.distribution_centers_echelon],
            add_header=False,
        )

        # export fixed plants cost
        self.export_to_file(
            filename="ffcost",
            rows=[[plant.fixed_cost] for plant in self.network.plants_echelon],
            add_header=False,
        )

        # export fixed warehoses cost
        self.export_to_file(
            filename="fwcost",
            rows=[[warehouse.fixed_cost] for warehouse in self.network.warehouses_echelon],
            add_header=False,
        )

        # export products capacity
        self.export_to_file(
            filename="pcap",
            rows=[plant.product_capacity for plant in self.network.plants_echelon],
        )

        # export products production cost
        self.export_to_file(
            filename="pcost",
            rows=[plant.products_prod_cost for plant in self.network.plants_echelon],
        )

        # export selling prices
        self.export_to_file(
            filename="Pricedcs",
            rows=[
                [
                    products_prices[0]  # all products have the same price
                    for products_prices in dist_center.selling_prices.values()
                ]
                for dist_center in self.network.distribution_centers_echelon
            ],
        )

        # export purchase cost
        self.export_to_file(
            filename="pucost",
            rows=[supplier.material_purchase_cost for supplier in self.network.suppliers_echelon],
        )

        # export supplier capacity
        self.export_to_file(filename="spcap", rows=[supplier.capacity for supplier in self.network.suppliers_echelon])

        # export transportation cost between warehouses and dist centers
        self.export_to_file(
            filename="tcostwdc",
            rows=[
                [prod_trans_cost]
                for prod_trans_cost in self.network.warehouses_echelon[0].products_trans_cost[0]
            ],  # it is the same for all dist_centers
            add_header=False,
        )

        # export transportation cost between plants and warehouses
        self.export_to_file(
            filename="tcostfw",
            rows=[
                [prod_trans_cost]
                for prod_trans_cost in self.network.plants_echelon[0].products_trans_cost[0]
            ],
            add_header=False,
        )

        # export transportation cost between suppliers and plants
        self.export_to_file(
            filename="tcostspf",
            rows=[
                [prod_trans_cost]
                for prod_trans_cost in self.network.suppliers_echelon[0].material_trans_cost[0]
            ],
            add_header=False,
        )

        # export transportation cost between dist centers and customers
        self.export_to_file(
            filename="tcostdcs",
            rows=[
                [prod_trans_cost]
                for prod_trans_cost in self.network.distribution_centers_echelon[0].products_trans_cost[
                    0
                ]
            ],
            add_header=False,
        )

        # export total delivery risk for Zk (see the objective function Z2)
        self.export_to_file(
            filename="Total_delivery_risk_DC",
            rows=[
                [
                    product_prop_delivery_risk * product_delivery_risk_impact
                    for product_prop_delivery_risk, product_delivery_risk_impact in zip(
                        dist_center.prop_delivery_risk,
                        dist_center.delivery_risk_impact,
                    )
                ]
                for dist_center in self.network.distribution_centers_echelon
            ],
        )

        # export total delivery risk for Yj (see the objective function Z2)
        self.export_to_file(
            filename="Total_delivery_risk_w",
            rows=[
                [
                    product_prop_delivery_risk * product_delivery_risk_impact
                    for product_prop_delivery_risk, product_delivery_risk_impact in zip(
                        warehouse.prop_delivery_risk,
                        warehouse.delivery_risk_impact,
                    )
                ]
                for warehouse in self.network.warehouses_echelon
            ],
        )

        # export total delivery risk for Xi (see the objective function Z2)
        self.export_to_file(
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
                for plant in self.network.plants_echelon
            ],
        )

        # export total delivery risk for Us (see the objective function Z2)
        self.export_to_file(
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
                for supplier in self.network.suppliers_echelon
            ],
        )

        # export warehouse capacity
        self.export_to_file(
            filename="wcap", rows=[warehouse.capacity for warehouse in self.network.warehouses_echelon]
        )
        
    @staticmethod
    def convert_directory_csv_files_to_xlxs(input_directory,output_directory):
        for csvfile in glob.glob(os.path.join(f"{input_directory}/", "*.csv")):
            filename = csvfile.split("/")[-1]
            workbook = Workbook(
                f"{output_directory}/{''.join(filename.split('.')[:-1])}.xlsx",
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
            # pd.read_csv(csvfile).to_excel(
            #     f"""{output_directory}/{''.join(csvfile.split("/")[-1].split('.')[:-1])}.xlsx""",
            #     index=False,
            # )