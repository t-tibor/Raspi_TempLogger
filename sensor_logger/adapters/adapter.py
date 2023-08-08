from abc import ABC, abstractmethod
import logging


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


