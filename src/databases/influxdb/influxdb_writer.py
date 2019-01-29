import json
import logging
import os
import threading
import requests

from influxdb import client as influxdb
from databases.influxdb.influxdb_converter import InfluxDBConverter


logger = logging.LoggerAdapter(logging.getLogger("sensiot"), {"class": os.path.basename(__file__)})

# TODO: We don't need this, do we?
class InfluxDBWriter(threading.Thread):
    def __init__(self, name, event, queue, config):
        threading.Thread.__init__(self)
        self.name = name
        self.event = event
        self.queue = queue
        self.config = config
        self.converter = InfluxDBConverter(self.config['measurements'])
        #self.influxdb = influxdb.InfluxDBClient(self.config['ip'], self.config['port'], self.config['user'], self.config['password'], self.config['database'])
        #self.influxdb.create_database(self.config['database'])
        self.faas_gateway_ip = self.config['faas']['faas_gateway_ip']
        self.faas_gateway_port = self.config['faas']['faas_gateway_port']
        self.writer_function_name = self.config['faas']['db-writer']
        self.prepare_function_name = self.config['faas']['db-prepare']

        logger.info("{} initialized successfully".format(self.name))

    def run(self):
        logger.info("Started {}".format(self.name))
        while not self.event.is_set():
            self.event.wait(1)
            while not self.queue.empty():
                #data = json.loads(self.queue.get())
                #influxdb_format = self.converter.convert(data)
                #response = requests.post("http://"+self.faas_gateway_ip+":"+self.faas_gateway_port+"/function/"+self.prepare_function_name, data)
                #influxdb_format=response
                #logger.info("########## INFLUXDB JSON READY FOR DB, FAASIFIED BABY!\n{}".format(str(influxdb_format)))
                #self.__send_data(influxdb_format.get())
                logger.info("Received data from queue and put into Influxdb")

        logger.info("Stopped {}".format(self.name))

    def __send_data(self, line):
        self.influxdb.write_points(line)
