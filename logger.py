import os
import glob
import argparse
import time
import datetime
import sys
from influxdb import InfluxDBClient



i2c_base = "/sys/bus/i2c/devices/i2c-1/1-0076/iio:device0"
humidity_path = os.path.join(i2c_base, 'in_humidityrelative_input')
temperature_path = os.path.join(i2c_base, 'in_temp_input')
pressure_path = os.path.join(i2c_base, 'in_pressure_input')

def get_humidity():
	with open(humidity_path, 'r') as f:
		value = f.readline()
		return float(value)/1000

def get_temperature():
	with open(temperature_path, 'r') as f:
		value = f.readline()
		return float(value)/1000

def get_pressure():
	with open(pressure_path, 'r') as f:
		value = f.readline()
		return float(value)

def get_data_points():
	hum 					= get_humidity()
	temp 					= get_temperature()
	press 				= get_pressure()
	isotimestamp	= datetime.datetime.utcnow().isoformat()
	timestamp 		= datetime.datetime.now().strftime("%Y %b %d - %H:%M:%S")

	#print(timestamp + ":  %f%%, %f°C, %fkPa" % (hum, temp, press))

	datapoints = [
	{
		"measurement" : "Room temperature",
		"tags" : {"runNum":1,},
		"time" : isotimestamp,
		"fields" : {"Humidity":hum, "Temperature":temp, "Pressure":press}
	}
	]

	return datapoints

# constant paramters
host = 'localhost'
port = '8086'
user = 'root'
password = 'root'
sampling_period = 60
dbname = "temp_logger_db"

client = InfluxDBClient(host, port, user, password, dbname)

try:
	while True:
		
		datapoints = get_data_points()
		bResult = client.write_points(datapoints)

		time.sleep(sampling_period)

except KeyboardInterrupt:
	print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")
