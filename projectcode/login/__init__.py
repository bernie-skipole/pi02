

import uuid

from http import cookies

from ... import FailPage, GoTo, ValidateError, ServerError


from ....skilift import projectURLpaths

from .. import database_ops


def check_password(password):
    "Returns True if password ok, False otherwise"
    try:
        access_user = database_ops.get_access_user()
        database_password, seed = database_ops.get_password(access_user)
        if (database_password, seed) == database_ops.hash_password(password, seed):
            # password ok
            return True
    except:
        pass
        # Any exception causes False to be returned
    # password fail
    return False


def submit_password(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    "If password not ok, raise FailPage"
    if 'password' not in call_data:
        raise FailPage("Invalid password!")
    password = call_data['password']
    if not password:
        raise FailPage("Invalid password!")
    if not check_password(password):
        raise FailPage("Invalid password!")


def request_login(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """create a cookie"""
    # After a user has tried to login and his password successfully checked then
    # this function is called from responder 2010 which is of type 'SetCookies'
    # a cookie is generated, set into the database and sent to the user browser
    # so future access is immediate when a received cookie is compared with the database cookie

    # set a cookie for cookie key 'project2'
    project = call_data['project']
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
    # and set the cookie string into database
    user = database_ops.get_access_user()
    status = database_ops.set_cookie(user, ck_string)
    if not status:
        raise FailPage("Access failed - database error")
    return cki


def check(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    "Called when a request to the login page is made, to check if the user is already logged in"
    if ('logged_in' in call_data) and call_data['logged_in']:
        # user is already logged in, go to page 2011
        raise GoTo(target=2011)


def logout(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Logs the user out by deleting the user cookie from the database, and also 
          set a cookie in the user browser to '000' which indicates logged out"""

    # When a user chooses logout - this calls responder 11 which is of type 'SetCookies'
    # The responder calls this function, and expects the function to return a cookie object

    call_data['logged_in'] =  False
    # set a cookie 'project2:000'
    project = call_data['project']
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





