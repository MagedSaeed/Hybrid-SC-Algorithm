from configparser import ConfigParser
import logging
import os

import sys

# increase recursion level
# https://stackoverflow.com/questions/6809402/python-maximum-recursion-depth-exceeded-while-calling-a-python-object
sys.setrecursionlimit(10_000)


class AppConfigMeta(type):
    @property
    def config(cls):
        if cls._config is None:
            cls.configure()
        return cls._config


class AppConfig(metaclass=AppConfigMeta):
    _config = None
    default_config_file_path = "hybrid_algorithm/default_config.ini"
    config_file_path = None

    @classmethod
    def _configure(cls):
        cls._config = ConfigParser()
        cls._config.read(cls.default_config_file_path)
        if cls.config_file_path is not None:
            if not os.path.isfile(cls.config_file_path):
                raise ValueError(f"{cls.config_file_path} if not a valid file path")
            cls._config.read(cls.config_file_path)
            logging.basicConfig(level=getattr(logging, cls.config["logging"]["level"]))

    @classmethod
    def configure(cls, config_file_path=None):
        if config_file_path is not None:
            cls.config_file_path = config_file_path
        cls._configure()
        return cls._config

    @classmethod
    def set_config(cls, config):
        cls._config = config
