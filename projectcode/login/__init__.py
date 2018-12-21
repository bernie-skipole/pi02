

import uuid
from datetime import datetime, timedelta

from http import cookies

from ... import FailPage, GoTo, ValidateError, ServerError


from ....skilift import projectURLpaths

from .. import database_ops

_ONE_MINUTE = timedelta(minutes = 1)

def check_password(password):
    "Returns True if password ok, False otherwise"
    try:
        access_user = database_ops.get_access_user()
        database_password, seed = database_ops.get_password(access_user)
        if (database_password, seed) == database_ops.hash_password(password, seed):
            # password ok
            return True
        database_ops.set_message("Invalid password submitted")
    except:
        pass
        # Any exception causes False to be returned
    # password fail
    return False


def submit_password(skicall):
    "If password not ok, raise FailPage"
    if 'password' not in skicall.call_data:
        raise FailPage("Invalid password!")
    password = skicall.call_data['password']
    if not password:
        raise FailPage("Invalid password!")
    if not check_password(password):
        raise FailPage("Invalid password!")


def request_login(skicall):
    """create a cookie"""
    # After a user has tried to login and his password successfully checked then
    # this function is called from responder 2010 which is of type 'SetCookies'
    # a cookie is generated, set into the database and sent to the user browser
    # so future access is immediate when a received cookie is compared with the database cookie

    # create a cookie for cookie key 'project2'
    project = skicall.project
    # generate a cookie string
    ck_string = uuid.uuid4().hex
    ck_key = project +"2"
    cki = cookies.SimpleCookie()
    cki[ck_key] = ck_string
    # twelve hours expirey time
    cki[ck_key]['max-age'] = 43200
    # set root project path
    url_dict = projectURLpaths()
    cki[ck_key]['path'] = url_dict[project]
    # is an admin user already logged in? - get the stored cookie.
    user = database_ops.get_access_user()
    stored_cookie = database_ops.get_cookie(user)
    if stored_cookie != "000":
        # someone is logged in, find last access time
        last_connect = database_ops.get_last_connect(user)
        now = datetime.utcnow()
        if now - last_connect < _ONE_MINUTE:
            # cannot allow the user to log in
            raise GoTo(target=2012)
    # Either no one is currently logged in,
    # or it has been longer than a minute since the last connection,
    # so log this user in by setting the cookie into the database
    # and returning it here for the SetCookies responder to apply it
    status = database_ops.set_cookie(user, ck_string)
    if not status:
        raise FailPage("Access failed - database error")
    return cki


def check(skicall):
    "Called when a request to the login page is made, to check if the user is already logged in"
    if ('logged_in' in skicall.call_data) and skicall.call_data['logged_in']:
        # user is already logged in, go to page 2011
        raise GoTo(target=2011)
    # user is not logged in, but do not allow access to login page, if admin user has
    # accessed the system in the last minute
    user = database_ops.get_access_user()
    # is an admin user logged in?
    stored_cookie = database_ops.get_cookie(user)
    if stored_cookie == "000":
        # no one is logged in, ok to go to login page
        return
    # someone is logged in, find last access time
    last_connect = database_ops.get_last_connect(user)
    now = datetime.utcnow()
    if now - last_connect < _ONE_MINUTE:
        raise GoTo(target=2012)
    # It has been longer than a minute since the last connection, so allow user
    # to access the login page
    return
    


def logout(skicall):
    """Logs the user out by deleting the user cookie from the database, and also 
          set a cookie in the user browser to '000' which indicates logged out"""

    # When a user chooses logout - this calls responder 11 which is of type 'SetCookies'
    # The responder calls this function, and expects the function to return a cookie object

    skicall.call_data['logged_in'] =  False
    # set a cookie 'project2:000'
    project = skicall.project
    ck_key = project +"2"
    cki = cookies.SimpleCookie()
    cki[ck_key] = "000"
    # set root project path in the cookie
    url_dict = projectURLpaths()
    cki[ck_key]['path'] = url_dict[project]
    # and set the cookie string into database
    user = database_ops.get_access_user()
    status = database_ops.set_cookie(user, "000")
    if not status:
        raise FailPage("Access failed - database error")
    return cki


# Following is not really a login function, but fits here as well as anywhere else

def display_logs(skicall):
    "Displays logs from the database"
    skicall.page_data['messages', 'para_text'] = database_ops.get_all_messages()


