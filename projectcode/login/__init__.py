
import hashlib
from base64 import b64decode


from ....skilift import FailPage, GoTo, ValidateError, ServerError

from .. import database_ops  


def check_login(project, environ):
    "Returns True if login ok, False otherwise"
    try:
        # checks database exists, if not create it
        if not database_ops.check_database_exists(project):
            # create the database
            database_ops.create_database()
        access_user = database_ops.get_access_user()
        access_password = database_ops.get_password(access_user)
        if access_password is None:
            return False
        auth = environ.get('HTTP_AUTHORIZATION')
        if auth:
            scheme, data = auth.split(" ", 1)
            if scheme.lower() != 'basic':
                return False
            username, password = b64decode(data).decode('UTF-8').split(':', 1)
            binary_password = (access_user + password).encode('utf-8')
            hashed_password = hashlib.sha512(binary_password).digest()
            if username == access_user and hashed_password == access_password:
                # login ok
                return True
    except:
        pass
        # Any exception causes False to be returned
    # login fail
    return False


def request_login(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set up the basic authentication"""
    failtext = 'Please Authenticate\n'
    page_data['headers'] = [
            ('content-type', 'text/plain'),
            ('content-length', str(len(failtext))),
            ('WWW-Authenticate', 'Basic realm="Outputs"')]
    page_data['status'] = '401 Unauthorized'
    return failtext