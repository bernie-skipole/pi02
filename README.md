# README #

This project is intended to be a general purpose web service which will run on a Raspberry pi, and is a basis for future projects. It presents a web service displaying basic password authenticated output controls, and lists inputs.

The project uses random numbers as inputs, and stores a value as an output - these would be replaced by input and output hardware routines in a full project.

The code is developed using the skipole web framework - see http://skipole.ski

Note: Raspberry Pi is a trademark of the Raspberry Pi Foundation, this project, and the skipole web framework, is not associated with any Raspberry Pi products or services.

This project uses the Waitress Python web server, and requires the package 'python3-waitress' to be installed using:

sudo apt-get install python3-waitress

You will also need the python3 version of rpi.gpio

To check if you have it, try

sudo python3

and then

import RPi.GPIO as GPIO

If this is accepted without errors, you are ok, if not, exit from python with ctrl-D and then install it using:

sudo apt-get install python3-rpi.gpio

**Installation with manual start**

Download the latest version of the pi01 tar file from the Downloads section, and uncompress it into a directory of your choice.

Within the directory, use python3 to run the file:

sudo python3 \_\_main\_\_.py -p 80

and this will run the web server.


**Installation with automatic boot up**

Download the latest version of the tar file from the Downloads section, and uncompress it into /opt, creating directory:

/opt/pi01/

Give the directory and contents root ownership

sudo chown -R root:root /opt/pi01

Then, using

sudo crontab -e

Add the following to the end of the crontab file:


        @reboot /usr/bin/python3 /opt/pi01/__main__.py -p 80 > /dev/null 2>&1 &


This starts the Waitress web server and pi01 application on port 80 on boot up.
