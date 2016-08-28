"The setup package"

import os

from ....skilift import FailPage, GoTo, ValidateError, ServerError, get_projectfiles_dir

from .. import login, database_ops

def setup_page(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set up the setup page"""
    project = ident_list[-1][0]
    username = database_ops.get_access_user()
    password = database_ops.get_default_password()
    defaults = "This will create a new setup, with defaults - username '%s' and password '%s'." % (username, password)
    setup_directory = os.path.join(get_projectfiles_dir(project), "setup")
    page_data['defaults', 'para_text'] = defaults
    page_data['setup', 'para_text'] = setup_directory


def set_password(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set up the setup page"""
    oldpassword = call_data['oldpassword', 'input_text']
    newpassword1 = call_data['newpassword1', 'input_text']
    newpassword2 = call_data['newpassword2', 'input_text']
    if (not oldpassword) or (not newpassword1) or (not newpassword2):
        raise FailPage(message="Missing data, all fields are required. Please try again.", displaywidgetname='accesspassword')
    if newpassword1 != newpassword2:
        raise FailPage(message="The new password fields are not equal. Please try again.", displaywidgetname='accesspassword')
    if oldpassword == newpassword1:
        raise FailPage(message="The new and current passwords must be different. Please try again.", displaywidgetname='accesspassword')
    if len(newpassword1) < 4:
        raise FailPage(message="Four characters or more please. Please try again.", displaywidgetname='accesspassword')
    if not login.check_password(oldpassword):
        raise FailPage(message="Invalid current password. Please try again.", displaywidgetname='accesspassword')
    # password ok, now set it
    user = database_ops.get_access_user()
    hashed_password = login.hash_password(newpassword1)
    if not database_ops.set_password(user, hashed_password):
        raise FailPage(message="Sorry, database access failure.", displaywidgetname='accesspassword')
    page_data['passwordset', 'show_para'] = True
