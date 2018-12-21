"""
This package will be called by the Skipole framework to access your data.
"""


import sys, time

from .. import FailPage, GoTo, ValidateError, ServerError, use_submit_list

from . import control, login, database_ops, hardware


# These pages do not require authentication, any others do
_PUBLIC_PAGES = [1,  # index
                10,  # submit_login
               540,  # no_javascript
              1002,  # css
              1004,  # css
              1006   # css
               ]

# login page 4 is unique - login status is checked, but access is allowed


def start_project(project, projectfiles, path, option):
    """On a project being loaded, and before the wsgi service is started, this is called once,
       Note: it may be called multiple times if your web server starts multiple processes.
       This function should return a dictionary (typically an empty dictionary if this value is not used).
       Can be used to set any initial parameters, and the dictionary returned will be passed as
       'proj_data' to subsequent start_call functions."""
    proj_data = {}

    try:
        # checks database exists, if not create it
        database_ops.start_database(project, projectfiles)
    except:
        print("Invalid read of database, delete setup directory to revert to defaults")
        sys.exit(1)

    # a time delay may be required here to give other services time to start
    # this has been found to be necessary in some situations if the service is
    # started on boot up and a network connection such as an mqtt client is needed

    # time.sleep(10)

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
    return proj_data


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
    """This function is called at the end of a call prior to filling the returned page with page_data,
       it can also return an optional ident_data string to embed into forms."""
    # in this example, status is the value on input02
    status = hardware.get_text_input('input02')
    if status:
        skicall.page_data['topnav','status', 'para_text'] = status
    else:
        skicall.page_data['topnav','status', 'para_text'] = "Status: input02 unavailable"
    return
