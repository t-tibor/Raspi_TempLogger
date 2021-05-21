#!/bin/bash

echo "Enable manually the 1w interface on the raspberry using the raspi-config tools"
echo "Interface options -> 1-Wire -> Enable"
echo "Do you want to do it? (Type 1 or 2)"
select yn in "Yes" "No"; do
	case $yn in
		Yes ) sudo raspi-config; break;;
		No ) break;;
		esac
done



