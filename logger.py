import os
import glob
import argparse
import math
import time
import datetime
import sys
from influxdb import InfluxDBClient



class InfluxDataGenerator(object):
	def __init__(self, name = "Room temperature", **kwargs):
		self._sensor_name = name

	def get_data_dict(self):
		return {}

	def get_record(self):
		isotimestamp	= datetime.datetime.utcnow().isoformat()
		timestamp 		= datetime.datetime.now().strftime("%Y %b %d - %H:%M:%S")
		data_dict 		= self.get_data_dict()

		#print(self._sensor_name)
		#print(f'Data: {data_dict}')

		datapoints = [
		{
			"measurement" : self._sensor_name,
			"tags" : {"runNum":1,},
			"time" : isotimestamp,
			"fields" : data_dict
		}
		]

		return datapoints


class IIO_Sensor(InfluxDataGenerator):
	def __init__(self, sysfs_base_path, **kwargs):
		super().__init__(**kwargs)
		self.__sysfs_base_path = sysfs_base_path

	@property
	def sysfs_base_path(self):
		return self.__sysfs_base_path


class IIO_PressureSensor(IIO_Sensor):
	def __init__(self, sysfs_base_path, **kwargs):
		super().__init__(sysfs_base_path, **kwargs)

		self._temperature_path 	= os.path.join(self.sysfs_base_path, 'in_temp_input')
		self._pressure_path 		= os.path.join(self.sysfs_base_path, 'in_pressure_input')

	def get_temperature(self):
		with open(self._temperature_path, 'r') as f:
			try:
				value = f.readline()
			except:
				value = 0
			return float(value)/1000

	def get_pressure(self):
		with open(self._pressure_path, 'r') as f:
			try:
				value = f.readline()
			except:
				value = 0
			return float(value)

	def get_data_dict(self):
		data = super().get_data_dict()
		data['Pressure'] = self.get_pressure()
		data['Temperature'] = self.get_temperature()
		return data


class IIO_HumiditySensor(IIO_PressureSensor):
	def __init__(self, sysfs_base_path, **kwargs):
		super().__init__(sysfs_base_path, **kwargs)
		self._humidity_path = os.path.join(self.sysfs_base_path, 'in_humidityrelative_input')

	def get_humidity(self):
		with open(self._humidity_path, 'r') as f:
			value = f.readline()
			return float(value)/1000

	def get_data_dict(self):
		data = super().get_data_dict()
		data['Humidity'] = self.get_humidity()
		return data


class I2C_Utils():
	#i2c_bus_path = "/sys/bus/i2c/devices/i2c-1/1-0076/iio:device0"
	i2c_bus_path = "/sys/bus/i2c/devices/i2c-1"
	
	@classmethod
	def get_iio_dev_path(cls, address):
		dev_path = os.path.join(cls.i2c_bus_path, '1-%04X' % address)
		items = os.listdir(dev_path)
		for item in items:
			if item.find('iio:device') > -1:
				return os.path.join(dev_path, item)


class I2C_PressureSensor(IIO_PressureSensor):
	def __init__(self, address, **kwargs):
		iio_path = I2C_Utils.get_iio_dev_path(address)
		super().__init__(iio_path, **kwargs)		


class I2C_HumiditySensor(IIO_HumiditySensor):
	def __init__(self, address, **kwargs):
		iio_path = I2C_Utils.get_iio_dev_path(address)
		super().__init__(iio_path, **kwargs)		


# constant paramters
host = 'localhost'
port = '8086'
user = 'temp_logger'
password = 'temp_logger_69'
sampling_period = 60
dbname = "temp_logger_db"

client = InfluxDBClient(host, port, user, password, dbname)

bmp280 = I2C_PressureSensor(address=0x77, name='Outdoors')
bme280 = I2C_HumiditySensor(address=0x76, name='Room temperature')
sensors = [ bmp280, bme280 ]

try:
	while True:
		for sensor in sensors:
			datapoints = sensor.get_record()
			bResult = client.write_points(datapoints)
			print('Data written successfully.')
		time.sleep(sampling_period)

except KeyboardInterrupt:
	print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")
