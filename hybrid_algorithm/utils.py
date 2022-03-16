import copy

import numpy as np


def get_open_facilities_in_echelon(echelon):
    return [facility for facility in echelon if facility.is_open == 1]


def reset_dict_entries(dict_obj):
    new_dict = dict()
    for index, (dict_key, dict_value) in enumerate(dict_obj.items()):
        new_dict[index] = dict_value
    return new_dict


def exclude_closed_facilities(network,inplace=False):
    """
    This method will remove the closed facilities from the network.
    This is not to include them in the lp calculation
    The closed facilities will be removed from all echelons and
    also any related properties will be deleted as well, like suppliers trans cost to closed plants, etc.
    """
    if not inplace:
        network = copy.deepcopy(network)
        
    original_facilities_status = network.facilities_statuses
    """filter out closed facilities from echelons"""
    network.suppliers_echelon = get_open_facilities_in_echelon(
        network.suppliers_echelon
    )
    network.plants_echelon = get_open_facilities_in_echelon(network.plants_echelon)
    network.warehouses_echelon = get_open_facilities_in_echelon(
        network.warehouses_echelon
    )
    network.distribution_centers_echelon = get_open_facilities_in_echelon(
        network.distribution_centers_echelon
    )

    """ remove any relation between suppliers and closed plants """
    closed_plants_idexes = [
        plant_index
        for plant_index, plant_status in enumerate(original_facilities_status[1])
        if plant_status == 0
    ]
    for supplier in network.suppliers_echelon:
        supplier.plants_distances = np.delete(
            supplier.plants_distances, closed_plants_idexes
        )
        for plant_index in closed_plants_idexes:
            del supplier.material_trans_cost[plant_index]
            del supplier.material_trans_env_impact[plant_index]
        supplier.material_trans_cost = reset_dict_entries(supplier.material_trans_cost)
        supplier.material_trans_env_impact = reset_dict_entries(
            supplier.material_trans_env_impact
        )

    """ remove any relation between plants and closed warehouses """
    closed_warehouses_idexes = [
        warehouse_index
        for warehouse_index, warehouse_status in enumerate(
            original_facilities_status[2]
        )
        if warehouse_status == 0
    ]
    for plant in network.plants_echelon:
        plant.warehouses_distances = np.delete(
            plant.warehouses_distances, closed_warehouses_idexes
        )
        for warehouse_index in closed_warehouses_idexes:
            del plant.products_trans_cost[warehouse_index]
            del plant.products_trans_env_impact[warehouse_index]
        plant.products_trans_cost = reset_dict_entries(plant.products_trans_cost)
        plant.products_trans_env_impact = reset_dict_entries(
            plant.products_trans_env_impact
        )

    """ remove any relation between warehouses and closed distribution centers """
    closed_dist_centers_idexes = [
        dist_center_index
        for dist_center_index, dist_center_status in enumerate(
            original_facilities_status[3]
        )
        if dist_center_status == 0
    ]
    for warehouse in network.warehouses_echelon:
        warehouse.dist_centers_distances = np.delete(
            warehouse.dist_centers_distances, closed_dist_centers_idexes
        )
        for dist_center_index in closed_dist_centers_idexes:
            del warehouse.products_trans_cost[dist_center_index]
            del warehouse.products_trans_env_impact[dist_center_index]
        warehouse.products_trans_cost = reset_dict_entries(
            warehouse.products_trans_cost
        )
        warehouse.products_trans_env_impact = reset_dict_entries(
            warehouse.products_trans_env_impact
        )
    return network
