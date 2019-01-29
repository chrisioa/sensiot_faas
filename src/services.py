import json
import logging
import os

from multiprocessing import Queue


logger = logging.LoggerAdapter(logging.getLogger("sensiot"), {"class": os.path.basename(__file__)})

class Services:
    def __init__(self, config, event):
        self.config = config
        self.event = event
        self.services = {
            "local_manager": self.__create_local_manager,
            "temperature_humidity_sensor": self.__create_temperature_humidity_sensor
        }

    def get_services(self, type):
        return self.services.get(type)()

    """
    Local Manager

    """
    def __get_local_configuration(self):
        local_configuration_path = self.config['services']['local_manager']['local_configuration']
        logger.info("Local configuration file set to {}".format(local_configuration_path))
        if os.path.isfile(local_configuration_path):
            with open(local_configuration_path, 'r') as file:
                configuration = json.load(file)
                return configuration
        else:
            logger.error("Local configuration file not found: {}".format(local_configuration_path))

    def __create_local_manager(self):
            from utilities.socket.socket_reader import SocketReader
            from utilities.local.metadata_appender import MetaDataAppender
            from utilities.local.local_manager import LocalManager


            threads = []
            local_configuration = self.__get_local_configuration()

            message_queue = Queue(maxsize=10)
            meta_queue = Queue(maxsize=10)

            socket_reader = SocketReader("SocketReader", self.event, message_queue)
            meta_data_appender = MetaDataAppender("MetaData", self.event, message_queue, meta_queue, local_configuration)
            local_manager = LocalManager("LocalManager", self.event, {"local_manager": self.config['services']['local_manager'], "local_configuration": local_configuration, "utilities": self.config["utilities"]["logging"]})

            threads.append(socket_reader)
            threads.append(meta_data_appender)
            threads.append(local_manager)

            return threads

    """
    Temperature & Humidity Sensors

    """
    def __create_temperature_humidity_sensor(self):
            from utilities.socket.socket_writer import SocketWriter
            threads = []
            type = os.environ['TYPE']

            sensor_queue = Queue(maxsize=10)

            if type == "ash2200":
                from sensors.temperature_humidity.ash2200 import ASH2200, USBSerial
                usb_serial = USBSerial(self.config['configuration'])
                ash2200 = ASH2200("ASH2200", usb_serial, self.event, sensor_queue)
                threads.append(ash2200)
            elif type == "dht":
                from sensors.temperature_humidity.dht import DHT
                dht = DHT("DHT", self.config['configuration'], self.event, sensor_queue)
                threads.append(dht)
            elif type == "mock":
                from sensors.temperature_humidity.sensor_mock import SensorMock
                mock = SensorMock("Mock", self.event, sensor_queue, self.config['configuration'])
                threads.append(mock)
            elif type == "openweathermap":
                from sensors.temperature_humidity.openweathermap import OpenWeatherMap
                open_weather_map = OpenWeatherMap("OpenWeatherMap", self.config['configuration'], self.event, sensor_queue)
                threads.append(open_weather_map)
            else:
                logger.error("No sensortype selected: {}".format(type))

            socket_writer = SocketWriter("SocketWriter", self.event, sensor_queue, os.environ['SOCKET'])
            threads.append(socket_writer)

            return threads

