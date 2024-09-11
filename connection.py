import configparser
import mysql.connector

config = configparser.ConfigParser()
config.read('config.ini')

def Connect():
    return mysql.connector.connect(host = config['mysqlDB']['host'],
                           user = config['mysqlDB']['user'],
                           password = config['mysqlDB']['pass'],
                           database = config['mysqlDB']['db'],
                           port = config['mysqlDB']['port'])

def Error():
    return mysql.connector.Error




