import math
import logging
from typing import List

class SensorChannel(object):
    def __init__(self, name:str, **kwargs):
        self._channel_name = name
        self._unit = kwargs.get("unit", "")
        self._hass_device_class = kwargs.get("hass_device_class", "")
        logging.debug(f'Sensor channel created: {self._channel_name}')

    @property
    def name(self):
        return self._channel_name

    def get_channel_data(self):
        channel_data = {}
        channel_data['channel_name'] = self._channel_name
        channel_data['unit']         = self._unit
        channel_data['device_class'] = self._hass_device_class
        channel_data['value']        = math.nan
        return channel_data

    @property
    def data(self):
        return self.get_channel_data()
    

class Sensor(object):
    def __init__(self, name="Unknown", **kwargs):
        self._sensor_name = name
        self._channels = list()
        logging.debug(f'Sensor created: {name}')

    @property
    def name(self):
        return self._sensor_name

    def add_channel(self, channel: List[SensorChannel]) -> None:
        self._channels.append(channel)

    @property
    def data(self) -> List[SensorChannel]:
        return self.get_sensor_data()

    def get_sensor_data(self):
        sensor_data = {}
        sensor_data['sensor_name'] = self._sensor_name
        all_channel_data = { ch.name:ch.data for ch in self._channels }        
        sensor_data['channels'] = { name:data for name,data in all_channel_data.items()  if not math.isnan(data['value']) }
        logging.debug(f'Sensor data dict created: {sensor_data}')
        return sensor_data
