# README #

This project is intended to be a general purpose web service which will run on a Raspberry pi, and is a basis for future projects. It presents a web service displaying basic password authenticated output controls, and lists inputs.

The project uses random numbers as inputs, and stores a value as an output - these would be replaced by input and output hardware routines in a full project.

The code is developed using the skipole web framework - see http://skipole.ski

Note: Raspberry Pi is a trademark of the Raspberry Pi Foundation, this project, and the skipole web framework, is not associated with any Raspberry Pi products or services.

**Simple serving for a Raspberry Pi**

This method simply uses the in-built Python web server, running as root.  It is not secure enough for Internet connection, nor is it suitable for multiple simultaneous access, but for a simple control project it may be suitable.

Assuming your project is called 'myproj'.  

Move myproj.tar.gz file, and uncompress it into /opt, creating directory:

/opt/myproj/

Give the directory and contents root ownership

sudo chown -R root:root /opt/myproj

Then, using

sudo crontab -e

Add the following to the end of the crontab file:


.. sourcecode:: python

        @reboot /usr/bin/python3 /opt/myproj/__main__.py -p 80 > /dev/null 2>&1 &


This starts /opt/myproj/__main__.py serving on port 80 on boot up.

The myproj web service is running in the background, with all logging output going to /dev/null, this may seem fairly primitive, with a single blocking process running as root.  However for internal LAN operation this may be sufficient.  Operation of the input/output pins also requires the process to be root.