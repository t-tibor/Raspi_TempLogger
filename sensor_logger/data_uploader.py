import logging
import time
from sensor import Sensor
from adapters import Adapter
from dataclasses import dataclass
from typing import Generator, List, Dict, Any


class SensorMapping:
    _sensor: Sensor
    _adapters: List[Adapter]

    def __init__(self, sensor: Sensor):
        self._sensor = sensor
        self._adapters = list()

    @property
    def sensor(self) -> Sensor:
        return self._sensor
    
    @property
    def adapters(self) -> List[Adapter]:
        return self._adapters
    
    def add_adapter(self, adapter:Adapter) -> None:
        self.adapters.append(adapter)
    

class DataUploader(object):
    _mapping: List[SensorMapping]

    def __init__(self, mapping: List[SensorMapping]):
        self._mapping = mapping

    def all_adapters(self) -> Generator[Adapter, None, None]:
        for m in self._mapping:
            adapters = m.adapters
            for adapter in adapters:
                yield adapter
        return None

    def _open_adapters(self) -> None:
        logging.debug('Opening adapters.')
        for adapter in self.all_adapters(): 
            adapter.open()
             
    def _close_adapters(self) -> None:
        logging.debug('Closing adapters.')
        for adapter in self.all_adapters():
            adapter.close()

    def _do_update(self) -> None:
        for m in self._mapping:
            sensor = m.sensor
            if sensor is not None:
                sensor_name = sensor.name
                sensor_data = sensor.data
                adapters = m.adapters          
                for adapter in adapters:
                        adapter.write_data(sensor_data)

    def update_loop(self, loop_period_sec: float):
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




class DataUploaderBuilder:
    _active_mapping: SensorMapping
    _mappings: List[SensorMapping]
    
    def __init__(self):
        self._mappings = list()

    def from_sensor(self, sensor: Sensor):
        self._active_mapping = SensorMapping(sensor)
        self._mappings.append(self._active_mapping)
        return self

    def save_data_to(self, adapter:Adapter):
        if self._active_mapping is not None:
            self._active_mapping.add_adapter(adapter)
        return self


    def build(self) -> DataUploader:
        uploader =  DataUploader(self._mappings)
        self._active_mapping = None
        self._mappings = list()
        return uploader 
