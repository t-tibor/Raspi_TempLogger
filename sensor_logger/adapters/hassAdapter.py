from .adapter import Adapter

import paho.mqtt.client as mqtt


import logging
import time


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

    def _compose_config_topic(self, channel_name: str) -> str:
        return f"homeassistant/sensor/{self._name}/{channel_name}/config"

    def _compose_state_topic(self, channel_name: str) -> str:
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