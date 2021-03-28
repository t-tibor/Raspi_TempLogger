cd $TEMP_LOGGER_HOME/docker/influxdb

docker run --rm influxdb:1.8.4 influxd config > influxdb.conf
# 💡 for influx v2 you need to use `print-config` instead of `config` -> docker run --rm influxdb influxd print-config > influxdb.conf
#     kudos to the reader that tipped me of about this difference
# next do some modifications to the default config
# enable HTTP auth
sed -i 's/^  auth-enabled = false$/  auth-enabled = true/g' influxdb.conf
# do any other changes you want, or replace with your own config entirely

# back to the original folder
cd -
