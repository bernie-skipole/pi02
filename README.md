# README #

This project is intended to be a web service which will run on a Raspberry pi, and will ultimately control a robotic telescope. The initial versions 0.0.0 to 0.0.9 consist of the web server, with fake inputs and outputs, and may be useful as a general starting point for similar projects.

From version 0.1.* onwards, code specific to the raspberry pi is imported, and the controls will be tailored to actual hardware. The code will therefore become more hardware specific, and less useful as a general template.

The code is developed using the skipole web framework, the tar download contains both this project code and the part of the framework needed to run the web server. Versions 0.0.* have no dependencies other than python3.

The tar file can be downloaded, extracted and 'python3 pi01' run to start the web service.  Initial controls are protected with default username 'astro', password 'station' - the password can be changed via the web service. The tar file can be imported into the full skipole framework for further development.