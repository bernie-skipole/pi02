import collections

from ....skilift import FailPage, GoTo, ValidateError, ServerError

from .. import database_ops


def control_page(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set up the control page"""
    page_data['output01', 'radio_checked'] = _get_output01()
    refresh_results(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang)


def refresh_results(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set the control page results fields"""
    if _get_output01():
        page_data['output01_result', 'para_text'] = "The current value of output 01 is : True"
    else:
        page_data['output01_result', 'para_text'] = "The current value of output 01 is : False"


def controls_json_api(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    "Returns json dictionary of output names : output values, used by external api"
    controls = database_ops.get_control_names()
    values = [ _get_output(name) for name in controls ]
    return collections.OrderedDict(zip(controls,values))


def set_output01(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """sets output 01 to True or False, called via web page"""
    if ('output01', 'radio_checked') in call_data:
        _set_output01(call_data['output01', 'radio_checked'])


def set_output(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    "External api call"
    if 'received_data' not in call_data:
        return
    received = call_data['received_data']
    if ('name' in received) and ('value' in received):
        name = received['name']
        value = received['value']
        controls = database_ops.get_control_names()
        if name not in controls:
            return
        _set_output(name_value)
        call_data['OUTPUT'] = name
           

def return_output(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """{outputname:value} returned as a result of external api call,
           outputname should have previously been set in call_data['OUTPUT']"""
    if 'OUTPUT' not in call_data:
        return {}
    outputname = call_data['OUTPUT']
    value = _get_output(outputname)
    if value is None:
        return {}
    return {outputname:value}

def _set_output(name, value):
    "Sets an output, given the output name and value"
    if name == 'output01':
        _set_output01(value)


def _get_output(name):
    "Gets an output value, given the output name, return None on failure"
    if name == 'output01':
        return _get_output01()


def _set_output01(value):
        "Sets output01"
        # currently only sets this in database, eventually will do it on hardware
        if value == 'True':
            database_ops.set_output('output01', True)
        else:
            database_ops.set_output('output01', False)
 

def _get_output01():
    "Gets output01"
    # currently only reads from database, eventually will do it on hardware
    return database_ops.get_output('output01')
