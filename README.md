# README #

This project is intended to be a general purpose web service which will run on a Raspberry pi, and is a basis for future projects. It presents a web service requiring password authentication to control outputs, and list inputs.

The code is developed using the skipole web framework - see http://skipole.ski

Note: Raspberry Pi is a trademark of the Raspberry Pi Foundation, this project, and the skipole web framework, is not associated with any Raspberry Pi products or services.

Initially the project is set with example inputs and outputs, and password 'password'.

You will need the python3 version of rpi.gpio

To check if you have it, try

sudo python3

and then

import RPi.GPIO as GPIO

If this is accepted without errors, you are ok, if not, exit from python with ctrl-D and then install it using:

sudo apt-get install python3-rpi.gpio

**Installation with manual start**

Download the latest version of the pi02 tar file from the Downloads section, and uncompress it into a directory of your choice.

Within the directory, use python3 to run the file:

sudo python3 \_\_main\_\_.py -p 80

and this will run the web server. You will be able to connect to it from a browser using the ip address of the pi.

**Optionally use the Waitress web server**

As default \_\_main\_\_.py uses the python library wsgiref server, however if you have the package 'python3-waitress' installed using:

sudo apt-get install python3-waitress

The script can be run with the -w option, which uses the Waitress web server.

sudo python3 \_\_main\_\_.py -w -p 80

Note: this project, and the skipole web framework, is not associated with the Waitress web server project, the option is included because, in our opinion, it seems a good fit.

**Installation with automatic boot up**

Download the latest version of the tar file from the Downloads section, and uncompress it into /opt, creating directory:

/opt/pi02/

Give the directory and contents root ownership

sudo chown -R root:root /opt/pi02

Then create a file :

/lib/systemd/system/pi02.service

containing the following:


    [Unit]
    Description=My project description
    After=multi-user.target

    [Service]
    Type=idle
    ExecStart=/usr/bin/python3 /opt/pi02/__main__.py -w -p 80

    WorkingDirectory=/opt/pi02
    Restart=on-failure

    # Connects standard output to /dev/null
    StandardOutput=null

    # Connects standard error to journal
    StandardError=journal

    [Install]
    WantedBy=multi-user.target

You will notice the -w option uses Waitress, remove the option if you just wish to use the wsgiref server. However we recommend Waitress as it is a multi threaded server.

Then set permissions of the file

sudo chown root:root /lib/systemd/system/pi02.service

sudo chmod 644 /lib/systemd/system/pi02.service


Enable the service

sudo systemctl daemon-reload

sudo systemctl enable pi02.service

This starts /opt/pi02/\_\_main\_\_.py serving on port 80 on boot up.

Useful functions to test the service:

sudo systemctl start pi02

sudo systemctl stop pi02

sudo systemctl restart pi02

sudo systemctl status pi02

sudo systemctl disable pi02

Display last lines of the journal

sudo journalctl -n

Display and continuously print the latest journal entries

sudo journalctl -f

**Security**

Using these instructions the service will be running as root, and the password authentication is unencrypted. These factors are considered unsafe on the internet, therefore this project is intended for a safe environment such as an internal LAN only.

**Further Development**

You will need to edit the file hardware.py (beneath projectcode), and develop further code for appropriate inputs and outputs. To further develop the web pages you need to be familiar with the skipole.py framework, and import the project, make a copy and develop it within the framework.

 
