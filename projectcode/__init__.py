"""
This package will be called by the Skipole framework to access your data.
"""


from base64 import b64decode

# These exception classes are available to be imported

from ...skilift import FailPage, GoTo, ValidateError, ServerError

from . import sensors, control, information, login

_USERNAME = "astro"
_PASSWORD = "station"


##############################################################################
#
# Your code needs to provide your own version of the following functions
#
##############################################################################

def start_call(environ, path, project, called_ident, caller_ident, received_cookies, ident_data, lang, check, proj_data):
    "When a call is initially received this function is called."
    call_data = {}
    page_data = {}
    if not called_ident:
        return None, call_data, page_data, lang
    if 'HTTP_HOST' in environ:
        # This is used in the information page to insert the host into a displayed url
        call_data['HTTP_HOST'] = environ['HTTP_HOST']
    if (called_ident[1] == 3001) or (called_ident[1] == 3002)  or (called_ident[1] == 8):
        # check login
        auth = environ.get('HTTP_AUTHORIZATION')
        if auth:
            scheme, data = auth.split(" ", 1)
            assert scheme.lower() == 'basic'
            username, password = b64decode(data).decode('UTF-8').split(':', 1)
            if username == _USERNAME and password == _PASSWORD:
                # login ok
                return called_ident, call_data, page_data, lang
        # login fail, ask for another login
        return (project,2010), call_data, page_data, lang
    return called_ident, call_data, page_data, lang


def submit_data(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    "This function is called when a Responder wishes to submit data for processing in some manner"

    # calls to sensors package
    if submit_list and (submit_list[0] == 'sensors'):
        try:
            submitfunc = getattr(sensors, submit_list[1])
        except:
            raise FailPage("submit_list contains 'sensors', but function not recognised")
        return submitfunc(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang)

    # calls to control package
    if submit_list and (submit_list[0] == 'control'):
        try:
            submitfunc = getattr(control, submit_list[1])
        except:
            raise FailPage("submit_list contains 'control', but function not recognised")
        return submitfunc(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang)

    # calls to information package
    if submit_list and (submit_list[0] == 'information'):
        try:
            submitfunc = getattr(information, submit_list[1])
        except:
            raise FailPage("submit_list contains 'information', but function not recognised")
        return submitfunc(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang)

    # calls to login package
    if submit_list and (submit_list[0] == 'login'):
        try:
            submitfunc = getattr(login, submit_list[1])
        except:
            raise FailPage("submit_list contains 'login', but function not recognised")
        return submitfunc(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang)

    raise FailPage("submit_list string not recognised")


def end_call(page_ident, call_data, page_data, proj_data, lang):
    """This function is called at the end of a call prior to filling the returned page with page_data,
       it can also return an optional ident_data string to embed into forms."""
    return
