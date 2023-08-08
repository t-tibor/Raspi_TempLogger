from .adapter import Adapter

from influxdb import InfluxDBClient


import datetime
import logging


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

    def write_data(self, sensor_data):
        isotimestamp = datetime.datetime.utcnow().isoformat()
        timestamp   = datetime.datetime.now().strftime("%Y %b %d - %H:%M:%S")

        sensor_name = sensor_data['sensor_name']
        channels    = sensor_data['channels']

        fields = { ch_name:ch_data['value'] for (ch_name, ch_data) in channels.items() }
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