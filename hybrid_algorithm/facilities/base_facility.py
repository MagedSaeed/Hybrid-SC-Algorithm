from hybrid_algorithm.config import AppConfig

config = AppConfig.configure()

facilities_config = config["facilities"]


class BaseFacility:
    NUMBER_OF_SUPPLIERS = int(facilities_config["facilities_count"])
    NUMBER_OF_PLANTS = int(facilities_config["facilities_count"])
    NUMBER_OF_WAREHOUSES = int(facilities_config["facilities_count"])
    NUMBER_OF_DISTRIBUTION_CENTERS = int(facilities_config["facilities_count"])
    NUMBER_OF_RAW_MATERIALS = int(config["facilities"]["raw_materials_count"])
    NUMBER_OF_MARKETS = int(config["facilities"]["markets_count"])
    NUMBER_OF_PRODUCTS = int(config["facilities"]["products_count"])
