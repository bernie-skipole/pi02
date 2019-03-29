import collections

from ... import FailPage, GoTo, ValidateError, ServerError

from .. import database_ops, hardware


def control_page(skicall):
    """Populate the control page, by setting widget values, and then the results values"""
    # display output description
    skicall.page_data['output01_description', 'para_text'] = hardware.get_output_description('output01')
    # widget output01 is boolean radio and expects a binary True, False value
    skicall.page_data['output01', 'radio_checked'] = _get_output('output01')
    # further widgets for further outputs to be set here
    # finally fill in all results fields
    refresh_results(skicall)


def refresh_results(skicall):
    """Fill in the control page results fields"""
    if _get_output('output01'):
        skicall.page_data['output01_result', 'para_text'] = "The current value of output 01 is : On"
    else:
        skicall.page_data['output01_result', 'para_text'] = "The current value of output 01 is : Off"


def set_output_from_browser(skicall):
    """sets given output, called from browser via web page"""
    if ('output01', 'radio_checked') in skicall.call_data:
        # set output01
        _set_output('output01', skicall.call_data['output01', 'radio_checked'])
    # further elif statements could set further outputs if they are present in call_data


def set_multi_outputs(output_dict):
    """output_dict is a dictionary of name:value to set"""
    for name, value in output_dict.items():
        _set_output(name, value)
    

def _set_output(name, value):
    """Sets an output, given the output name and value"""
    output_type = hardware.get_output_type(name)
    if output_type is None:
        return
    if output_type == 'boolean':
        if (value == 'True') or (value == 'true') or (value is True):
            value = True
        else:
            value = False
        hardware.set_boolean_output(name, value)
    if output_type == 'int':
        if not isinstance(value, int):
            try:
                value = int(value)
            except:
                # Invalid value
                return
    if output_type == 'text':
        if not isinstance(value, str):
            try:
                value = str(value)
            except:
                # Invalid value
                return
        
    # Set output value in database
    database_ops.set_output(name, value)


def _get_output(name):
    """Gets an output value, given the output name, return None on failure"""
    # instructions to get an output from hardware are placed here
    hardtype = hardware.get_output_type(name)
    if hardtype == 'boolean':
        hardvalue = hardware.get_boolean_output(name)
        if hardvalue is not None:
            return hardvalue
    # if hardvalue not available, reads the stored output from the database
    return database_ops.get_output(name)
