# README #

This project is intended to be a web service which will run on a Raspberry pi, and will ultimately control a robotic telescope. The initial version 0.0.0 is simply the web server, with fake inputs and outputs, and may be useful as a general starting point for similar projects.

As the controls are tailored to actual hardware the code will become more hardware specific, and less useful as a general template.

The code is developed using the skipole web framework, the tar download contains both this code and the part of the framework needed to run the web server. Version 0.0.0 has no dependencies other than python3.

The tar file can be downloaded, extracted and __main__.py run to start the web service.  Initial controls are protected with username 'astro', password 'station'. The tar file can be imported into the full framework for further development.