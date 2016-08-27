"The setup package"

from ...skilift import FailPage, GoTo, ValidateError, ServerError, get_projectfiles_dir

from .. import database_ops

def setup_page(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set up the setup page"""
    # currently not used
    pass