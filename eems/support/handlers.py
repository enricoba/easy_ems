# -*- coding: utf-8 -*-
"""
This module handles file exports and provides functions and classes to call
for other modules inside this package.
"""

import csv
import time
import logging
import ConfigParser
from threading import Lock


"""
defining logger
"""

logger = logging.getLogger(__name__)


class StatusHandler(object):
    def __init__(self, *args):
        """Public Class *StatusHandler* ...

        :param args:
        :return:
            Returns an object.
        """
        self.lock = Lock()
        self.dic = {key: False for key in args}

    def get(self, key):
        return self.dic[key]

    def on(self, key):
        with self.lock:
            self.dic[key] = True

    def off(self, key):
        with self.lock:
            self.dic[key] = False

    def get_all(self):
        return self.dic


class ConfigHandler(object):
    def __init__(self):
        self.parser = ConfigParser.ConfigParser()
        self.path_config = '/home/pi/eems/config.ini'

    def read_all_config(self):
        self.parser.read(self.path_config)
        c_log = self.parser.getboolean('general', 'log')
        c_console = self.parser.getboolean('general', 'console')
        c_csv = self.parser.getboolean('exports', 'csv')
        return c_log, c_console, c_csv

    def read_config(self, section, option, dtype=None):
        self.parser.read(self.path_config)
        if dtype == 'bool':
            return self.parser.getboolean(section, option)
        elif dtype == 'int':
            return self.parser.getint(section, option)
        elif dtype == 'float':
            return self.parser.getfloat(section, option)
        elif dtype is None:
            return self.parser.get(section, option)

    def set_config(self, section, option, value):
        self.parser.read(self.path_config)
        self.parser.set(section, option, value)

    def write_config(self):
        with open(self.path_config, 'wb') as config:
            self.parser.write(config)


class CsvHandler(object):
    def __init__(self, path):
        """Public class *CsvHandler* provides functions to manipulate csv files
        passed via the parameter *csv_file*. Therefore, the standard library
        module *csv* is used.

        :return:
            Returns an object providing the public function *write*.
        """
        self.csv_file = path

    def __count_col(self):
        """Private function *__count_col* reads the csv file handled by the
         parent class and counts existing columns.

        :return:
            Returns an integer containing the count of columns.
        """
        try:
            with open(self.csv_file, 'rb') as _csv:
                csv_reader = csv.reader(_csv, delimiter=';')
                return len(csv_reader.next())
        except IOError as e:
            logger.error('{}'.format(e))

    def __count_rows(self):
        """Private function *__count_rows* reads the csv file handled by the
         parent class and counts existing rows.

        :return:
            Returns an integer containing the count of rows.
        """
        try:
            with open(self.csv_file, 'rb') as _csv:
                csv_reader = csv.reader(_csv, delimiter=';')
                rows = sum(1 for row in csv_reader)
                return rows
        except IOError as e:
            logger.error('{}'.format(e))

    def add(self, csv_file, header):
        """Private function *__add* creates the csv file using the file name of
        the string *csv_file* passed to the parent class.

        :param csv_file:
            Expects a string containing a csv file name. If no string is
            provided, default file name *default.csv* is assumed.
        :param header:
            Expects a list containing all header elements for the csv file.
        :return:
            Returns *None*.
        """
        self.csv_file += csv_file
        header = ['id', 'timestamp', 'date', 'time'] + header
        try:
            with open(self.csv_file, 'wb') as _csv:
                csv_writer = csv.writer(_csv, delimiter=';')
                csv_writer.writerow(header)
        except IOError as e:
            logger.error('{}'.format(e))

    def write(self, data):
        """Public function *write* adds a new row/entry to the handled csv
        file.

        :param data:
            Expects a list containing values with the same length as keys.
        :return:
            Returns *None*.
        """
        print data.dic
        columns = self.__count_col() - 4
        tmp_list = list()
        for sensor_type in data.dic.keys():
            for sensor in data.dic[sensor_type].keys():
                tmp_list.append(sensor)
        print tmp_list
        entries = len(tmp_list)
        # validates if the amount of columns is similar to the passed
        # keys of the dictionary
        if entries == columns:
            row = self.__count_rows()
            tmp_time = time.localtime()
            str_date = time.strftime('%Y-%m-%d', tmp_time)
            str_time = time.strftime('%H:%M:%S', tmp_time)
            timestamp = time.mktime(tmp_time)

            # catch values
            tmp_list = list()
            for sensor_type in data.dic.keys():
                for sensor in sensor_type:
                    tmp_list.append(data.dic[sensor_type][sensor])
            print tmp_list
            data = [row, timestamp, str_date, str_time] + tmp_list
            print data
            try:
                with open(self.csv_file, 'ab') as _csv:
                    csv_writer = csv.writer(_csv, delimiter=';')
                    csv_writer.writerow(data)
            except IOError as e:
                logger.error('{}'.format(e))
        else:
            logger.error('Passed elements do not have the same '
                         'length as columns in csv')
