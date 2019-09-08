
import os, sys

from skipole import WSGIApplication, FailPage, GoTo, ValidateError, ServerError, set_debug, use_submit_list


# the framework needs to know the location of the projectfiles directory holding this and
# other projects - specifically the skis and skiadmin projects
# The following line assumes, as default, that this file is located beneath
# ...projectfiles/newproj/code/

PROJECTFILES = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
PROJECT = 'pi02'


from picode import control, login, database_ops, hardware

# These pages do not require authentication, any others do
_PUBLIC_PAGES = [1,  # index
                10,  # submit_login
               540,  # no_javascript
              1004   # css
               ]

# login page 4 is unique - login status is checked, but access is allowed

try:
    # checks database exists, if not create it
    database_ops.start_database(PROJECT, PROJECTFILES)
except:
    print("Invalid read of database, delete setup directory to revert to defaults")
    sys.exit(1)

# setup hardware
hardware.initial_setup_outputs()

# get dictionary of initial start-up output values from database
output_dict = database_ops.power_up_values()
if not output_dict:
    print("Invalid read of database, delete setup directory to revert to defaults")
    sys.exit(1)

# set the initial start-up values
control.set_multi_outputs(output_dict)

database_ops.set_message("Service started")


def start_call(called_ident, skicall):
    "When a call is initially received this function is called."
    if not called_ident:
        return
    if skicall.environ.get('HTTP_HOST'):
        # This is used in the information page to insert the host into a displayed url
        skicall.call_data['HTTP_HOST'] = skicall.environ['HTTP_HOST']
    else:
        skicall.call_data['HTTP_HOST'] = skicall.environ['SERVER_NAME']
    # calls to public pages are allowed
    if called_ident[1] in _PUBLIC_PAGES:
        return called_ident
    # any other, are password protected pages
    logged_in = False
    if skicall.received_cookies:
        cookie_name = skicall.project + '2'
        if cookie_name in skicall.received_cookies:
            cookie_string = skicall.received_cookies[cookie_name]
            if cookie_string and (cookie_string != "000"):
                # so a recognised cookie has arrived, check database_ops to see if the user has logged in
                con = None
                try:
                    access_user = database_ops.get_access_user()
                    con = database_ops.open_database()
                    stored_cookie = database_ops.get_cookie(access_user, con)
                    if stored_cookie == cookie_string:
                        logged_in = True
                        # this user is logged in, so update last connect time
                        database_ops.update_last_connect(access_user, con)
                except:
                    pass
                    # Any exception causes logged_in to remain False
                finally:
                    if con:
                        con.close()
    skicall.call_data['logged_in'] = logged_in                   
    if logged_in or called_ident[1] == 4:
        return called_ident
    # not logged in, not page 4, go to home, unless page 4
    return skicall.project,1


@use_submit_list
def submit_data(skicall):
    """This function is called when a Responder wishes to submit data for processing in some manner
       For two or more submit_list values, the decorator ensures the matching function is called instead"""

    raise FailPage("submit_list string not recognised")


def end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with page_data."""
    # in this example, status is the value on input02
    status = hardware.get_text_input('input02')
    if status:
        skicall.page_data['topnav','status', 'para_text'] = status
    else:
        skicall.page_data['topnav','status', 'para_text'] = "Status: input02 unavailable"
    return


##############################################################################
#
# The above functions will be inserted into the skipole.WSGIApplication object
# and will be called as required
#
##############################################################################


# create the wsgi application
application = WSGIApplication(project=PROJECT,
                              projectfiles=PROJECTFILES,
                              proj_data={},
                              start_call=start_call,
                              submit_data=submit_data,
                              end_call=end_call,
                              url="/")

# This creates a WSGI application object. On being created the object uses the projectfiles location to find
# and load json files which define the project, and also uses the functions :
#     start_call, submit_data, end_call
# to populate returned pages.
# proj_data is an optional dictionary which you may use for your own purposes,
# it is included as the skicall.proj_data attribute


# The skis application must always be added, without skis you're going nowhere!
# The skis sub project serves javascript files required by the framework widgets.

skis_code = os.path.join(PROJECTFILES, 'skis', 'code')
if skis_code not in sys.path:
    sys.path.append(skis_code)
import skis
skis_application = skis.makeapp(PROJECTFILES)
application.add_project(skis_application, url='/lib')

# The add_project method of application, enables the added sub application
# to be served at a URL which should extend the URL of the main 'root' application.
# The above shows the main newproj application served at "/" and the skis library
# project served at "/lib"


# to deploy on a web server, you would typically install skipole on the web server,
# together with a 'projectfiles' directory containing the projects you want
# to serve (typically this project, and the skis project).
# you would then follow the web servers own documentation which should describe how
# to load a wsgi application.

# You could remove everything below here when deploying and serving
# the application. The following lines are used to serve the project locally
# and add the skiadmin project for development.

if __name__ == "__main__":

    # If called as a script, this portion runs the python wsgiref.simple_server
    # and serves the project. Typically you would do this with the 'skiadmin'
    # sub project added which can be used to develop pages for your project

    ############################### THESE LINES ADD SKIADMIN ######################
                                                                                  #
    set_debug(True)                                                               #
    skiadmin_code = os.path.join(PROJECTFILES, 'skiadmin', 'code')                #
    if skiadmin_code not in sys.path:                                             #
        sys.path.append(skiadmin_code)                                            #
    import skiadmin                                                               #
    skiadmin_application = skiadmin.makeapp(PROJECTFILES, editedprojname=PROJECT) #
    application.add_project(skiadmin_application, url='/skiadmin')                #
                                                                                  #
    ###############################################################################

    from wsgiref.simple_server import make_server

    # serve the application
    host = "127.0.0.1"
    port = 8000

    httpd = make_server(host, port, application)
    print("Serving %s on port %s. Call http://localhost:%s/skiadmin to edit." % (PROJECT, port, port))
    httpd.serve_forever()

