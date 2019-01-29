import json
import logging
import os
import threading
import requests

from queue import Queue
from utilities.local.meta.data import SensorData

logger = logging.LoggerAdapter(logging.getLogger("sensiot"), {"class": os.path.basename(__file__)})


class MetaDataAppender(threading.Thread):

    def __init__(self, name, event, input_queue, output_queue, config):
        super(MetaDataAppender, self).__init__()
        self.name = name
        self.event = event
        self.config = config
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.hostname = self.__get_hostname("/etc/hostname")
        self.device_id = self.config['meta']['device_id']
        self.building = self.config['location']['building']
        self.room = self.config['location']['room']
        self.measurements_name = self.config['measurements']
        self.faas_gateway_ip = self.config['faas']['faas_gateway_ip']
        self.faas_gateway_port = self.config['faas']['faas_gateway_port']
        self.writer_function_name = self.config['faas']['db-writer']
        self.prepare_function_name = self.config['faas']['db-prepare']

        logger.info("{} initialized successfully".format(self.name))

    def run(self):
        logger.info("Started {}".format(self.name))
        while not self.event.is_set():
            self.event.wait(2)
            while not self.input_queue.empty():
                raw = self.input_queue.get()
                logger.info("Raw data received")
                deserialized_data = json.loads(raw.replace("'", '"'))
                converted_data = self.__convert(deserialized_data)
                serialized_data = converted_data.to_json()
                function_url = "http://"+self.faas_gateway_ip+":"+self.faas_gateway_port+"/function/"+self.writer_function_name
                response = requests.post(function_url, serialized_data)
                ##### FUNCTION CALL HERE #####
                ##### The functions receives this for example: {"sensor_id": 3, "type": "SensorMock", "measurements": [{"name": "temperature", "value": -23.0, "unit": "\u00b0C"}, {"name": "humidity", "value": -60.0, "unit": "\u00b0C"}], "hostname": "1ec3f4c24036", "device_id": "RPiDev1", "building": "L9", "room": "Living Room", "measurements_name":"Temp & Humidity", "timestamp": 1548262139} ####
                logger.info("Data sent to OpenFaas function")
        logger.info("Stopped: {}".format(self.name))

    def __get_hostname(self, path):
        if os.path.isfile(path):
            with open(path) as file:
                return file.readline().strip()
        else:
            logger.error("Unable to locate {} for hostname".format(path))
            return "unspecified"

    def __convert(self, data):
        return SensorData(self.hostname,
                          self.device_id,
                          self.building,
                          self.room,
                          self.measurements_name ,
                          data)
