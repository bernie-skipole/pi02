# default output values
# This dictionary has keys output names, and values being a tuple of (type, value, onpower, BCM number)
# where type is one of 'text', 'boolean', 'integer'
# value is the default value to put in the database when first created
# onpower is True if the 'default value' is to be set on power up, or False if last recorded value is to be used
# BCM number is the appropriate BCM pin number, or None if not relevant

# Currently only one output 'output01' on BCM 24 is defined

_OUTPUTS = {"output01" : ('boolean', False, True, 24)}


# import RPi.GPIO
_gpio_control = True
try:
    import RPi.GPIO as GPIO            # import RPi.GPIO module  
except:
    _gpio_control = False


def initial_setup_outputs():
    "Returns True if successfull, False if not
    if not _gpio_control:
        return False
    GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD
    for bcm in _OUTPUTS.values():
        # set outputs
        if bcm[3] is not None: 
            GPIO.setup(bcm[3], GPIO.OUT)


def get_output_names():
    "Returns list of output names, the list is sorted by boolean, integer and text items, and in name order within these categories"
    global _OUTPUTS
    bool_list = sorted(name for name in _OUTPUTS if _OUTPUTS[name][0] == 'boolean')
    int_list =  sorted(name for name in _OUTPUTS if _OUTPUTS[name][0] == 'integer')
    text_list = sorted(name for name in _OUTPUTS if _OUTPUTS[name][0] == 'text')
    controls_list = []
    if bool_list:
        controls_list.extend(bool_list)
    if int_list:
        controls_list.extend(int_list)
    if text_list:
        controls_list.extend(text_list)
    return controls_list


def get_outputs():
    global _OUTPUTS
    return _OUTPUTS.copy()


def get_output_type(name):
    "Given an output name, returns the output type, or None if the name is not found"
    if name in _OUTPUTS:
        return _OUTPUTS[name][0]


def get_boolean_output(name):
    "Given an output name, return True or False for the state of the output, or None if name not found, or not boolean, or _gpio_control is False"
    if not _gpio_control:
        return
    if name not in _OUTPUTS:
        return
    if _OUTPUTS[name][0] != 'boolean':
        return
    return bool(GPIO.input(_OUTPUTS[name][3]))


