cd $TEMP_LOGGER_HOME/docker/grafana

docker run --rm --entrypoint /bin/bash grafana/grafana:latest -c 'cat $GF_PATHS_CONFIG' > grafana.ini

cd -
