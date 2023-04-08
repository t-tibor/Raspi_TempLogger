from adapters import InfluxAdapter, HassAdapter

logging.basicConfig(level=logging.INFO)


logging.info('Sensor logger version 2.0')
influx_adapter = InfluxAdapter()
outdoor_hass_adapter = HassAdapter(name='Outdoor')
indoor_hass_adapter = HassAdapter(name = 'Indoor')

uploader = DataUploader( mapping = [
                                        {
                                            'sensor':   I2C_SensorFactory.create_sensor('humidity', address=0x76, name='Room temperature'),
                                            'adapters': [ influx_adapter, indoor_hass_adapter]
                                        }
                                   ]
                       )

uploader.update_loop(loop_period_sec = 55)

