import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

from abc import ABC


class Adapter(ABC):
    def __init__(self):
        self._status = "closed"
    
    @abstractmethod
    def do_open(self, **kwargs):
        pass

    def open(self, **kwargs):
        if self._status == "closed":
            logging.info('Opening adapter.')
            self.do_open(**kwargs)
            self._status = "opened"

    @abstractmethod
    def do_close(self, **kwargs):
        pass
    
    def close(self, **kwargs):
        if self._status == "opened":
            logging.info('Closing adapter.')
            self.do_close(**kwargs)
            self._status == "closed"
    
    @abstractmethod
    def write_data(self, sensor_data):
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

    def write_data(self, sensor_data):
        isotimestamp	= datetime.datetime.utcnow().isoformat()
        timestamp 		= datetime.datetime.now().strftime("%Y %b %d - %H:%M:%S")

        sensor_name = sensor_data['sensor_name']
        channels    = sensor_data['channels']
        #print(self._sensor_name)
        #print(f'Data: {data_dict}')

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

    def write_data(self, sensor_data):        
        sensor_name = sensor_data['sensor_name']
        channels = sensor_data['channels']
        for channel_name, channel_data in channels.items():
            topic   = self._get_channel_topic(channel_data)
            payload = channel_data['value']
            logging.debug(f'Publishing mqtt data topic: {topic}, payload: {payload}')
            self._client.publish(topic, payload)