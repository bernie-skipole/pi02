from ....skilift import FailPage, GoTo, ValidateError, ServerError


def request_login(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set up the basic authentication"""
    failtext = 'Please Authenticate\n'
    page_data['headers'] = [
            ('content-type', 'text/plain'),
            ('content-length', str(len(failtext))),
            ('WWW-Authenticate', 'Basic realm="Outputs"')]
    page_data['status'] = '401 Unauthorized'
    return failtext