#!/usr/bin/env python3

###########################
#
# pi01 robotic telescope
#
###########################

# sys is used for the sys.exit function and to check python version
import sys, os

# Check the python version
if sys.version_info[0] != 3 or sys.version_info[1] < 2:
    print("Sorry, your python version is not compatable")
    print("This program requires python 3.2 or later")
    print("Program exiting")
    sys.exit(1)

# argparse is used to pass the port and check value
import argparse

# used to run the python wsgi server
from wsgiref.simple_server import make_server

# the skipoles package contains your own code plus
# the skipole framework code
import skipoles 

# Sets up a parser to get port and check value
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='Robotics Telescope Raspberry Pi 01 web service',
                                 epilog='Stop the server with ctrl-c')

parser.add_argument("-p", "--port", type=int, dest="port", default=8000,
                  help="The port the web server will listen at, default 8000")


parser.add_argument('--version', action='version', version='pi01 0.0.6')

args = parser.parse_args()

print("Loading site")

# The skipoles.load_project() function requires the project name,
# and the location of the 'projectfiles' directory, normally in the same
# directory as this script

projectfiles = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'projectfiles')

site = skipoles.load_project("pi01", projectfiles)

if site is None:
    print("Project not found")
    sys.exit(1)


# Power up outputs, read required outputs from database
from skipoles.projectcode.pi01 import database_ops

if not database_ops.check_database_exists("pi01"):
    # create the database
   database_ops. create_database()

# get dictionary of output values
output_dict = database_ops.power_up_values()
if not output_dict:
    print("Invalid read of database, delete setup directory to revert to defaults")
    sys.exit(1)

print("Setting up output values:")
print(output_dict)

from skipoles.projectcode.pi01 import control
control.set_multi_outputs(output_dict)


# Define the wsgi app

def the_app(environ, start_response):
    "Defines the wsgi application"
    # uses the 'site' object created previously
    status, headers, data = site.respond(environ)
    start_response(status, headers)
    return data

# serve the site, using the python wsgi web server

httpd = make_server('', args.port, the_app)
print("Serving on port " + str(args.port) + "...")
print("Press ctrl-c to stop")

# Serve until process is killed
httpd.serve_forever()
