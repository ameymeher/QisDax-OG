from configparser import ConfigParser
from os import getcwd


def get_config(path = f'{getcwd()}/config.ini'):
    config = ConfigParser()
    config.read(path)
    return config
