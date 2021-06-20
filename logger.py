import os
import glob
import argparse
import math
import time
import datetime
import logging
import sys
from influxdb import InfluxDBClient

import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.INFO)


class SensorChannel(object):
    def __init__(self, name, **kwargs):
        self._channel_name = name
        self._unit = kwargs.get("unit", "")
        self._hass_device_class = kwargs.get("hass_device_class", "")
        logging.debug(f'Sensor channel created: {self._channel_name}')

    @property
    def name(self):
        return self._channel_name

    def get_data(self):
        data = {}
        data['channel_name'] = self._channel_name
        data['unit']         = self._unit
        data['device_class'] = self._hass_device_class
        return data

    @property
    def data(self):
        return self.get_data()
    

class IIO_SensorChannel(SensorChannel):
    def __init__(self, name, sysfs_path, **kwargs):
        super().__init__(name, **kwargs)
        self._div = kwargs.get('div', 1)
        self._path = sysfs_path

    def get_data(self):
        data = super().get_data()
        with open(self._path, 'r') as f:
            try:
                value = f.readline()
            except:
                value = 0
        data['value'] = float(value)/self._div
        return data


class Sensor(object):
    def __init__(self, name="Unknown", **kwargs):
        self._sensor_name = name
        self._channels = list()
        logging.debug(f'Sensor created: {name}')

    @property
    def name(self):
        return self._sensor_name

    def add_channel(self, channel):
        self._channels.append(channel)

    @property
    def data(self):
        return self.get_data_dict()

    def get_data_dict(self):
        data = {}        
        for ch in self._channels:
            data[ch.name] = ch.data
        logging.debug(f'Sensor data dict created: {data}')
        return data


class IIO_Sensor(Sensor):
    def __init__(self, name, sysfs_base_path, **kwargs):
        super().__init__(name, **kwargs)
        self._sysfs_base_path = sysfs_base_path

    @property
    def sysfs_base_path(self):
        return self._sysfs_base_path


class IIO_PressureSensor(IIO_Sensor):
    def __init__(self, sysfs_base_path, **kwargs):
        super().__init__(sysfs_base_path=sysfs_base_path, **kwargs)

        temp_path = os.path.join(self.sysfs_base_path, 'in_temp_input')
        temp_ch = IIO_SensorChannel(name="Temperature", unit="°C", hass_device_class='Temperature', sysfs_path=temp_path, div=1000)
        self.add_channel(temp_ch)

        pressure_path 		= os.path.join(self.sysfs_base_path, 'in_pressure_input')
        press_ch = IIO_SensorChannel(name="Pressure", unit='kPa', hass_device_class='Pressure', sysfs_path=pressure_path)
        self.add_channel(press_ch)


class IIO_HumiditySensor(IIO_PressureSensor):
    def __init__(self, sysfs_base_path, **kwargs):
        super().__init__(sysfs_base_path, **kwargs)
        humidity_path = os.path.join(self.sysfs_base_path, 'in_humidityrelative_input')
        humidity_ch = IIO_SensorChannel(name="Humidity", unit='%', hass_device_class="humidity",  sysfs_path=humidity_path, div=1000)
        self.add_channel(humidity_ch)

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



class Adapter(object):
    def __init__(self):
        self._status = "closed"

    def do_open(self, **kwargs):
        pass

    def open(self, **kwargs):
        if self._status == "closed":
            logging.info('Opening adapter.')
            self.do_open(**kwargs)
            self._status = "opened"

    def do_close(self, **kwargs):
        pass
    
    def close(self, **kwargs):
        if self._status == "opened":
            logging.info('Closing adapter.')
            self.do_close(**kwargs)
            self._status == "closed"
    
    def write_data(self, sensor_name, data):
        pass


class InfluxAdapter(Adapter):    
    def __init__(self):
        super().__init__()
        # constant parameters        
        self.host = '192.168.1.100'
        self.port = '8086'
        self.user = 'temp_logger'
        self.password = 'temp_logger_69'
        self.sampling_period = 60
        self.dbname = "temp_logger_db"
        self.client = None

    def do_open(self, **kwargs):
        logging.info('Opening influxdb adapter.')
        self.client = InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
   
    def do_close(self, **kwargs):
        self.client = None

    def write_data(self, sensor_name, data):
        isotimestamp	= datetime.datetime.utcnow().isoformat()
        timestamp 		= datetime.datetime.now().strftime("%Y %b %d - %H:%M:%S")

        #print(self._sensor_name)
        #print(f'Data: {data_dict}')

        fields = { ch_name:ch_data['value'] for (ch_name, ch_data) in data.items() }
        datapoints = [
        {
            "measurement" : sensor_name,
            "tags" : {"runNum":1,},
            "time" : isotimestamp,
            "fields" : fields
        }
        ]

        logging.debug(f'Writing influxdb data: {datapoints}')

        self.client.write_points(datapoints)


class HassAdapter(Adapter):
    broker_address = "192.168.1.100"

    def __init__(self, name):
        super().__init__()
        self._name   = name
        self._mqtt_autodetect = dict()

    def do_open(self, **kwargs):
        self._client = mqtt.Client(self._name)
        self._client.connect(self.broker_address)
              
    def do_close(self, **kwargs):
        self._unregister_topics()
        self._client.disconnect()
        self._client = None
        self._mqtt_autodetect = {}

    def _unregister_topics(self):
        for channel_name, autodetect_data in self._mqtt_autodetect.items():
            config_topic = autodetect_data['config_topic']
            # Cleanup all the registered sensors
            self._client.publish(config_topic, "")
            
    def _compose_config_topic(self, channel_name):
        return f"homeassistant/sensor/{self._name}/{channel_name}/config"
        
    def _compose_state_topic(self, channel_name):
        return f"homeassistant/sensor/{self._name}/{channel_name}/state"

    def _get_channel_topic(self, channel_data):
        channel_name = channel_data['channel_name']
        autodetect_data = self._mqtt_autodetect.get(channel_name, None)
        if autodetect_data is None:
            autodetect_data = dict()
            autodetect_data['config_topic'] = self._compose_config_topic(channel_name)
            autodetect_data['state_topic']  = self._compose_state_topic(channel_name)
            self._mqtt_autodetect[channel_name] = autodetect_data

            # create a new sensor in the home assistant using the mqtt discovery
            topic = autodetect_data['config_topic']
            
            cls = channel_data['device_class']
            name = self._name + "_" + channel_data['channel_name'] 
            state = autodetect_data['state_topic']
            unit = channel_data['unit']

            payload = '{' + f'''"device_class": "{cls}", 
                        "name":"{name}", 
                        "state_topic":"{state}",
                        "unit_of_measurement":"{unit}"''' + '}'

            logging.debug(f'Registering home assisstant mqtt sensor with topic: {topic}, payload: {payload}')
            self._client.publish(topic, payload)
            time.sleep(0.1)
        return autodetect_data['state_topic']

    def write_data(self, sensor_name, sensor_data):        
        for channel_name, channel_data in sensor_data.items():
            topic   = self._get_channel_topic(channel_data)
            payload = channel_data['value']
            logging.debug(f'Publishing mqtt data topic: {topic}, payload: {payload}')
            self._client.publish(topic, payload)




class DataUploader(object):
    def __init__(self, mapping):
        self._mapping = mapping

    def all_adapters(self):
        for m in self._mapping:
            adapters = m['adapters']
            for adapter in adapters:
                yield adapter
        return None

    def _open_adapters(self):
        logging.debug('Opening adapters.')
        for adapter in self.all_adapters(): 
            adapter.open()
             
    def _close_adapters(self):
        logging.debug('Closing adapters.')
        for adapter in self.all_adapters():
            adapter.close()

    def _do_update(self):
        for m in self._mapping:
            sensor = m['sensor']
            sensor_name = sensor.name
            sensor_data = sensor.data
            adapters = m['adapters']            
            for adapter in adapters:
                adapter.write_data(sensor_name, sensor_data)

    def update_loop(self, loop_period_sec):
        self._open_adapters()
        logging.info('Starting data uploader loop.')
        try:
            while True:
                self._do_update()
                time.sleep(loop_period_sec)
        except KeyboardInterrupt:
            print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")         
        logging.info('Exiting data uploader loop.')
        self._close_adapters()


influx_adapter = InfluxAdapter()
outdoor_hass_adapter = HassAdapter(name='Outdoor')
indoor_hass_adapter = HassAdapter(name = 'Indoor')

uploader = DataUploader( mapping = [
                                        {
                                            'sensor':   I2C_PressureSensor(address=0x77, name='Outdoors'),
                                            'adapters': [ influx_adapter,outdoor_hass_adapter]
                                        },
                                        {
                                            'sensor':   I2C_HumiditySensor(address=0x76, name='Room temperature'),
                                            'adapters': [ influx_adapter, indoor_hass_adapter]
                                        }
                                   ]
                       )

uploader.update_loop(loop_period_sec = 55)

