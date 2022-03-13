from dataclasses import dataclass
from hybrid_algorithm.config import AppConfig

config = AppConfig.config
facilities_config = config["facilities"]


@dataclass
class BaseFacility:
    @classmethod
    def _configure(cls):
        cls.NUMBER_OF_SUPPLIERS = int(facilities_config["facilities_count"])
        cls.NUMBER_OF_PLANTS = int(facilities_config["facilities_count"])
        cls.NUMBER_OF_WAREHOUSES = int(facilities_config["facilities_count"])
        cls.NUMBER_OF_DISTRIBUTION_CENTERS = int(facilities_config["facilities_count"])
        cls.NUMBER_OF_RAW_MATERIALS = int(config["facilities"]["raw_materials_count"])
        cls.NUMBER_OF_MARKETS = int(config["facilities"]["markets_count"])
        cls.NUMBER_OF_PRODUCTS = int(config["facilities"]["products_count"])
