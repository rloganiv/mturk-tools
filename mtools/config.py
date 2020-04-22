"""
Client / database configuration.

Defines `config` to be used as a singleton in other scripts.
"""
import configparser


config = configparser.ConfigParser()

with open('config.ini', 'r') as config_file:
    config.read_file(config_file)
