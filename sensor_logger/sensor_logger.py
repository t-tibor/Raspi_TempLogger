import logging
from adapters import InfluxAdapter, HassAdapter
from i2c_sensors import I2C_SensorFactory
from data_uploader import DataUploader, DataUploaderBuilder

logging.basicConfig(level=logging.INFO)


logging.info('Sensor logger version 2.0')
sensor = I2C_SensorFactory.create_sensor('humidity', address=0x76, name='Room temperature')
influx_adapter = InfluxAdapter()
outdoor_hass_adapter = HassAdapter(name='Outdoor')
indoor_hass_adapter = HassAdapter(name = 'Indoor')

builder = DataUploaderBuilder()
builder.from_sensor(sensor).save_data_to(influx_adapter).save_data_to(indoor_hass_adapter)

uploader = builder.build()
uploader.update_loop(loop_period_sec = 55)
