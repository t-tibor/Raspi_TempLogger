# Raspi_temp_logger
Config and setup scripts for an environment monitoring system using a rasberry pi and BME280/BMP280 sensors.

# Installation steps
1. Build the device tree overlay as described in  the devtree/build_device_tree_overlay file.
2. Copy the devicetree overlay to the /boot/overlays folder.
3. Include the new overlay in the /boot/config.txt file so that it gets loaded upon system boot.
4. Reboot the system.
5. Check whether the new devices are shown under the following path: /sys/bus/i2c/devices/1-xxxx
6. Run the setup_python.sh script so that the dependencies are installed.
7. Check whether the logger.py script works.
8. Install the logger as a deamon service using the scripts/setup_logger_daemon.sh scipt.