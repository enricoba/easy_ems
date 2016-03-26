# -*- coding: utf-8 -*-
"""
Core module.
"""
# Standard modules/functions from python
import time
import logging
import os
import sys
from threading import Lock
# Internal modules/functions from eems
from eems.support.checks import Check
from eems.support.detects import ds18b20_sensors
from support.handlers import ConfigHandler, CsvHandler


class _SensorDictionary(object):
    def __init__(self):
        """Private class *_SensorDictionary* provides functions to manage the
        sensors dictionary.

        :return:
            Returns a in-memory object tree providing the functions
            *set_temp*, *get_dic* and *reset_dic*.
        """
        self.dic = dict()
        self.lock = Lock()

    def add_sensor(self, sensor_type, sensors):
        self.dic[sensor_type] = {sensor: None for sensor in sensors}

    def set_temp(self, sensor, temp):
        """Public function *set_temp* sets the value for an individual key.

        :param sensor:
            Expects a string of the sensor name to match with the sensor key.
        :param temp:
            Expects an integer or a float containing the sensor value
            to store.
        :return:
            Returns *None*.
        """
        with self.lock:
            self.dic.__setitem__(sensor, temp)

    def get_dic(self):
        """Public function *get_dic* returns the sensors dictionary.

        :return:
            Returns the dictionary.
        """
        return self.dic

    def reset_dic(self):
        """Public function *reset_dic* sets all dictionary values to None.

        :return:
            Returns *None*.
        """
        for sensor in self.dic.keys():
            self.dic.__setitem__(sensor, None)


class Eems(object):
    def __init__(self, sensors, log=None, console=None, csv=None):
        """

        :param log:
        :param console:
        :param csv:
        :return:
        """
        # Check sensors
        if isinstance(sensors, list) is True:
            for sensor in sensors:
                if isinstance(sensor, str) is True:
                    pass
                else:
                    logging.error('Sensor list must contain strings')
                    sys.exit()
        else:
            logging.error('Please provides sensors as list')
            sys.exit()

        # flags, handlers etc.
        __home__ = '/home/pi/eems'
        __config__ = ConfigHandler()
        self.__csv__ = CsvHandler(__home__)

        c_log, c_console, c_csv = __config__.read_all_config()
        if log is None:
            log = c_log
        if console is None:
            console = c_console
        if csv is None:
            csv = c_csv

        # validate user input
        if isinstance(log, bool) is True:
            pass
        else:
            logging.error('Parameter *log* must be a bool')
            sys.exit()
        if isinstance(console, bool) is True:
            pass
        else:
            logging.error('Parameter *console* must be a bool')
            sys.exit()
        if isinstance(csv, bool) is True:
            pass
        else:
            logging.error('Parameter *csv* must be a bool')
            sys.exit()

        # save parameter to config file
        if log is True:
            __config__.set_config('general', 'log', True)
            __config__.write_config()
        elif log is False:
            __config__.set_config('general', 'log', False)
            __config__.write_config()
        if console is True:
            __config__.set_config('general', 'console', True)
            __config__.write_config()
        elif console is False:
            __config__.set_config('general', 'console', False)
            __config__.write_config()

        # logger
        str_date = time.strftime('%Y-%m-%d')
        str_time = time.strftime('%H-%M-%S')
        log_format = '%(asctime)-21s %(name)-22s %(levelname)-9s %(message)s'
        log_date_format = '%Y-%m-%d %H:%M:%S'
        if os.path.basename(sys.argv[0])[-3:] == '.py':
            filename_script = os.path.basename(sys.argv[0])[:-3]
        else:
            filename_script = 'eems'

        if log is True:
            log_file = '{}{}_{}_{}.txt'.format(__home__, str_date, str_time,
                                               filename_script)
            logging.basicConfig(level=logging.DEBUG,
                                format=log_format,
                                datefmt=log_date_format,
                                filename=log_file)
            if console is True:
                console = logging.StreamHandler()
                console.setLevel(logging.INFO)
                formatter = logging.Formatter(fmt=log_format,
                                              datefmt=log_date_format)
                console.setFormatter(formatter)
                logging.getLogger('').addHandler(console)
            logger = logging.getLogger(__name__)
            logger.info('Logfile has been created')
        else:
            logging.basicConfig(level=logging.INFO,
                                format=log_format,
                                datefmt=log_date_format)
            if console is False:
                logging.disabled = True
            logger = logging.getLogger(__name__)
            logger.info('No logfile has been created')

        # check sensors list + detect connected sensors
        c = Check()
        self.sensors_dict = _SensorDictionary()
        for sensor in sensors:
            if sensor.upper() == 'DS18B20':
                if c.w1_config() is True and c.w1_modules() is True:
                    tmp_sensors = ds18b20_sensors()
                    if tmp_sensors is False:
                        sys.exit()
                    else:
                        self.sensors_dict.add_sensor('DS18B20', tmp_sensors)
                else:
                    logger.error('Check for DS18B20 failed')
                    sys.exit()
            # elif sensor.upper() == 'DHT11':
            #    print 'check dht11'
            else:
                logging.warning('Sensor: {} not available'.format(sensor))

        # CSV
        if csv is True:
            # save parameter to config file
            __config__.set_config('exports', 'csv', True)
            __config__.write_config()

            csv_file = '{}_{}_{}.csv'.format(str_date, str_time,
                                             filename_script)
            csv_sensor_list = list()
            for sensor_type in self.sensors_dict.dic.keys():
                for sensor in sensor_type.keys():
                    csv_sensor_list.append('{}_{}'.format(sensor_type, sensor))

            # generate csv handler
            self.__csv__.add(csv_file, csv_sensor_list)
        elif csv is False:
            __config__.set_config('exports', 'csv', False)
            __config__.write_config()