cd $TEMP_LOGGER_HOME/docker/influxdb

docker run --rm telegraf telegraf config > telegraf.conf
# now modify it to tell it how to authenticate against influxdb
sed -i 's/^  # urls = \["http:\/\/127\.0\.0\.1:8086"\]$/  urls = \["http:\/\/influxdb:8086"\]/g' telegraf.conf
sed -i 's/^  # database = "telegraf"$/  database = "telegraf"/' telegraf.conf
sed -i 's/^  # username = "telegraf"$/  username = "telegraf"/' telegraf.conf
sed -i 's/^  # password = "metricsmetricsmetricsmetrics"$/  password = "telegraf_69"/' telegraf.conf
# as we run inside docker, the telegraf hostname is different from our Raspberry hostname, let's change it
sed -i 's/^  hostname = ""$/  hostname = "'${HOSTNAME}'"/' telegraf.conf

cd -
