#/bin/bash

# Update the python3 and the logger script path in the service file.
cat ./sensor_logger.service.in  | sed -e "s#ExecStart=.*#ExecStart= `which python3` `realpath ../sensor_logger/sensor_logger.py`#" > ./sensor_logger.service

# Copy the service file to the systemd config folder
sudo cp ./sensor_logger.service /etc/systemd/system/

# Reload the systemd unis files
sudo systemctl daemon-reload 

# Set the temp_logger service to auto start mode
sudo systemctl enable sensor_logger.service

# And also start to make sure
sudo systemctl start sensor_logger.service
