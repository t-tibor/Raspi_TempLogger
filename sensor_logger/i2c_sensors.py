import os
import logging
from typing import Any
from iio_sensor import IIO_HumiditySensor, IIO_PressureSensor

class I2C_Utils():
    #i2c_bus_path = "/sys/bus/i2c/devices/i2c-1/1-0076/iio:device0"
    i2c_bus_path:str = "/sys/bus/i2c/devices/i2c-1"
    
    @classmethod
    def get_iio_dev_path(cls, address:str) -> Any:
        dev_path = os.path.join(cls.i2c_bus_path, '1-%04X' % address)
        items = os.listdir(dev_path)
        for item in items:
            if item.find('iio:device') > -1:
                return os.path.join(dev_path, item)
        return None


class I2C_PressureSensor(IIO_PressureSensor):
    def __init__(self, address, **kwargs):
        iio_path = I2C_Utils.get_iio_dev_path(address)
        super().__init__(iio_path, **kwargs)		


class I2C_HumiditySensor(IIO_HumiditySensor):
    def __init__(self, address:str, **kwargs):
        iio_path = I2C_Utils.get_iio_dev_path(address)
        super().__init__(iio_path, **kwargs)		


class I2C_SensorFactory(object):
  @staticmethod
  def create_sensor(type:str, address, **kwargs):
    sensor=None

    try:
        if type=='humidity':
            sensor=I2C_HumiditySensor(address, **kwargs)
        elif type=='pressure':
            sensor=I2C_PressureSensor(address, **kwargs)
    except:
        logging.error(f'Cannot create sensor with type: {type}, address: {address}, args: {kwargs}')

    return sensor
