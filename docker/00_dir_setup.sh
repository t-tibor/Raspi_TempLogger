# do this on your raspi
export TEMP_LOGGER_HOME=~/projects/temp_logger

mkdir -p $TEMP_LOGGER_HOME/docker/influxdb/data
mkdir -p $TEMP_LOGGER_HOME/docker/influxdb/init
mkdir -p $TEMP_LOGGER_HOME/docker/compose-files/influxdb



mkdir -p $TEMP_LOGGER_HOME/docker/grafana/data
sudo chown 472:472 $TEMP_LOGGER_HOME/docker/grafana/data
kdir -p $TEMP_LOGGER_HOME/docker/grafana/provisioning
mkdir -p $TEMP_LOGGER_HOME/docker/compose-files/grafana
