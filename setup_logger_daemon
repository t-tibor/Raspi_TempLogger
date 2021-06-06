#/bin/bash

# Update the python3 and the logger script path in the service file.
cat ./temp_logger.service  | sed -e "s#ExecStart=.*#ExecStart= `which python3` `realpath ./logger.py`#" > ./temp_logger.service

# Copy the service file to the systemd config folder
sudo cp ./temp_logger.service /etc/systemd/system/

# Reload the systemd unis files
sudo systemctl daemon-reload 

# Set the temp_logger service to auto start mode
sudo systemctl enable temp_logger.service

# And also start to make sure
sudo systemctl start temp_logger.service
