class DataUploader(object):
    def __init__(self, mapping):
        self._mapping = mapping

    def all_adapters(self):
        for m in self._mapping:
            adapters = m['adapters']
            for adapter in adapters:
                yield adapter
        return None

    def _open_adapters(self):
        logging.debug('Opening adapters.')
        for adapter in self.all_adapters(): 
            adapter.open()
             
    def _close_adapters(self):
        logging.debug('Closing adapters.')
        for adapter in self.all_adapters():
            adapter.close()

    def _do_update(self):
        for m in self._mapping:
            sensor = m['sensor']
            if sensor is not None:
                sensor_name = sensor.name
                sensor_data = sensor.data
                adapters = m['adapters']            
                for adapter in adapters:
                        adapter.write_data(sensor_data)

    def update_loop(self, loop_period_sec):
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