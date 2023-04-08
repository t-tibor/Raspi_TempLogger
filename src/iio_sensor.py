import os
import glob
import argparse
import math
import time
import datetime
import logging
import sys



class IIO_SensorChannel(SensorChannel):
    def __init__(self, name, sysfs_path, **kwargs):
        super().__init__(name, **kwargs)
        self._div = kwargs.get('div', 1)
        self._path = sysfs_path

    def get_channel_data(self):
        data = super().get_channel_data()
        with open(self._path, 'r') as f:
            try:
                value = f.readline()
            except:
                value = math.nan
        data['value'] = float(value)/self._div
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