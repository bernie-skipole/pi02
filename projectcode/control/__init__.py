import collections

from ....skilift import FailPage, GoTo, ValidateError, ServerError


# These global variables temporarily take the place of output functions
_OUTPUT_01 = False


_CONTROLS = ["output01"]


def control_page(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set up the control page"""
    page_data['output01', 'radio_checked'] = _return_output01()
    refresh_results(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang)


def refresh_results(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """Set the control page results fields"""
    if _return_output01():
        page_data['output01_result', 'para_text'] = "The current value of output 01 is : True"
    else:
        page_data['output01_result', 'para_text'] = "The current value of output 01 is : False"


def controls_json_api(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    controls = _CONTROLS 
    values = [_return_output01()]
    return collections.OrderedDict(zip(controls,values))


def set_output01(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    """sets output 01 to True or False"""
    if ('output01', 'radio_checked') in call_data:
        _set_output01(call_data['output01', 'radio_checked'])


def set_output(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    "External api call"
    if 'received_data' not in call_data:
        return
    received = call_data['received_data']
    if ('name' in received) and ('value' in received):
        if received['name'] == 'output01':
            call_data['OUTPUT'] = 'output01'
            _set_output01(received['value'])

def return_output(caller_ident, ident_list, submit_list, submit_dict, call_data, page_data, lang):
    "Returned as a result of external api call"
    if 'OUTPUT' not in call_data:
        return {}
    output = call_data['OUTPUT']
    if output =='output01':
        value = _return_output01()
        return {'output01':value}
    else:
        return {}

def _set_output01(value):
        global _OUTPUT_01
        if value == 'True':
            _OUTPUT_01 = True
        else:
            _OUTPUT_01 = False

def _return_output01():
    global _OUTPUT_01
    return _OUTPUT_01
