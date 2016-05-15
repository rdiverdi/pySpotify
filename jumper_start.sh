#!/bin/sh
echo '27' > /sys/class/gpio/export
echo 'in' > /sys/class/gpio/gpio27/direction
if grep -q '1' /sys/class/gpio/gpio27/value
then 
  echo 'start spotify'
  /home/pi/pySpotify/startFlask.sh
else 
  echo 'start normally'
fi
echo '27' > /sys/class/gpio/unexport 
