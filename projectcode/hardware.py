
# _OUTPUTS

# This dictionary has keys output names, and values being a tuple of (type, value, onpower, BCM number)
# where type is one of 'text', 'boolean', 'integer'
# value is the default value to put in the database when first created
# onpower is True if the 'default value' is to be set on power up, or False if last recorded value is to be used
# BCM number is the appropriate BCM pin number, or None if not relevant

# Currently only one output 'output01' on BCM 24 is defined

_OUTPUTS = {"output01" : ('boolean', False, True, 24, "Output pin BCM 24")}


# _INPUTS

# This dictionary has keys inpuput names, and values being a tuple of (type, pud, BCM number)
# where type is one of 'text', 'boolean', 'integer', 'float'
# pud, pull up down is True for pull up, False for pull down, None if not relevant
# BCM number is the appropriate BCM pin number, or None if not relevant

# Currently two inputs are defined
# 'input01' is the server time
# 'input02' is the input on BCM 23

_INPUTS = {"input01" : ('boolean', True, 23, "Input pin BCM 23"),
           "input02" : ('text', None, None, "Server time")           
          }



import time

# import RPi.GPIO
_gpio_control = True
try:
    import RPi.GPIO as GPIO            # import RPi.GPIO module  
except:
    _gpio_control = False


def initial_setup_outputs():
    "Returns True if successfull, False if not"
    if not _gpio_control:
        return False
    GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD
    for bcm in _OUTPUTS.values():
        # set outputs
        if bcm[3] is not None: 
            GPIO.setup(bcm[3], GPIO.OUT)
    for bcm in _INPUTS.values():
        # set inputs
        if bcm[2] is not None:
            if bcm[1]:
                GPIO.setup(bcm[2], GPIO.IN, pull_up_down = GPIO.PUD_UP)
            else:
                GPIO.setup(bcm[2], GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


def get_output_names():
    "Returns list of output names, the list is sorted by boolean, integer and text items, and in name order within these categories"
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
    return _OUTPUTS.copy()


def get_output_description(name):
    "Given an output name, returns the output description, or None if the name is not found"
    if name in _OUTPUTS:
        return _OUTPUTS[name][4]


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


def set_boolean_output(name, value):
    "Given an output name, sets the output pin"
    if not _gpio_control:
        return
    if name not in _OUTPUTS:
        return
    if _OUTPUTS[name][0] != 'boolean':
        return
    if value:
        GPIO.output(_OUTPUTS[name][3], 1)
    else:
        GPIO.output(_OUTPUTS[name][3], 0)



def get_input_names():
    "Returns list of input names, the list is sorted by boolean, integer, float and text items, and in name order within these categories"
    bool_list = sorted(name for name in _INPUTS if _INPUTS[name][0] == 'boolean')
    int_list =  sorted(name for name in _INPUTS if _INPUTS[name][0] == 'integer')
    float_list =  sorted(name for name in _INPUTS if _INPUTS[name][0] == 'float')
    text_list = sorted(name for name in _INPUTS if _INPUTS[name][0] == 'text')
    sensors_list = []
    if bool_list:
        sensors_list.extend(bool_list)
    if int_list:
        sensors_list.extend(int_list)
    if float_list:
        sensors_list.extend(float_list)
    if text_list:
        sensors_list.extend(text_list)
    return sensors_list

def get_inputs():
    return _INPUTS.copy()


def get_input_description(name):
    "Given an input name, returns the input description, or None if the name is not found"
    if name in _INPUTS:
        return _INPUTS[name][3]


def get_input_type(name):
    "Given an input name, returns the input type, or None if the name is not found"
    if name in _INPUTS:
        return _INPUTS[name][0]


def get_boolean_input(name):
    "Given an input name, return True or False for the state of the input, or None if name not found, or not boolean, or _gpio_control is False"
    if not _gpio_control:
        return
    if name not in _INPUTS:
        return
    if _INPUTS[name][0] != 'boolean':
        return
    return bool(GPIO.input(_INPUTS[name][2]))


def get_text_input(name):
    "Returns text input for the appropriate input, or empty string if no text found"
    if name not in _INPUTS:
        return ''
    if _INPUTS[name][0] != 'text':
        return ''
    if name == "input02":
        # This input returns a time string
        return time.strftime("%c", time.gmtime())
    return ''


def get_input_name(bcm):
    "Given a bcm number, returns the name"
    if bcm is None:
        return
    for name, values in _INPUTS.items():
        if values[2] == bcm:
            return name


class Listen(object):
    """Listens for input pin changes. You should define a callback function
       mycallback(name, userdata)

       where name will be the input name triggered,
       and userdata will be the variable you pass to this Listen object. 

       useage
       listen = Listen(mycallback, userdata)
       listen.start_loop()

       This will then use the threaded interrupt facilities of RPi.GPIO
       to call the callback when one of the inputs falls (if pud True)
       or rises (if pud False), each with a 300ms bounce time
      
    """ 

    def __init__(self, callbackfunction, userdata):
        self.set_callback = callbackfunction
        self.userdata = userdata

    def input_state(self, name):
        return get_boolean_input(name)

    def input_description(self, name):
        return get_input_description(name)

    def _pincallback(self, channel):
        """This is the callback added to each pin, in turn it calls
           callbackfunction(name, userdata)"""
        name = get_input_name(channel)
        self.set_callback(name, self.userdata)

    def start_loop(self):
        "Sets up listenning threads"
        if not _gpio_control:
            return
        for name, values in _INPUTS.items():
            if (values[0] == 'boolean') and isinstance(values[2], int):
                if values[1]:
                    # True for pull up pin, therefore detect falling edge
                    GPIO.add_event_detect(values[2], GPIO.FALLING, callback=self._pincallback, bouncetime=300)
                else:
                    GPIO.add_event_detect(values[2], GPIO.RISING, callback=self._pincallback, bouncetime=300)



###  scheduled actions ###


def event1(*args):
    "event1 description"
    print('******1******')


def event2(*args):
    "event2 description"
    print('******2******')





### scheduled actions to occur at set times each hour ###

class ScheduledEvents(object):

    def __init__(self, *args):
        "Stores the mqtt_clent and rconn and creates the schedule of hourly events"
        # create a list of event callbacks and minutes past the hour for each event in turn
        self.event_list = [(event1, 2), (event2, 32)]
        self.args = args
        self.schedule = sched.scheduler(time.time, time.sleep)


    @property
    def queue(self):
        return self.schedule.queue


    def _create_next_hour_events(self):
        "Create a new set of events for the following hour"

        # On moving into the next hour, thishour timestamp is moved
        # forward by an hour 
        self.thishour = self.thishour + 3600

        # create scheduled events which are to occur
        # at interval minutes during thishour

        for evt_callback, mins in self.event_list:
            self.schedule.enterabs(time = self.thishour + mins*60,
                                   priority = 1,
                                   action = evt_callback,
                                   argument = self.args
                                   )

        # schedule a final event to occur 30 seconds after last event
        last_event = self.event_list[-1]
 
        final_event_time = self.thishour + last_event[1]*60 + 30
        self.schedule.enterabs(time = final_event_time,
                               priority = 1,
                               action = self._create_next_hour_events
                               )


    def __call__(self): 
        "Schedule Events, and run the scheduler, this is a blocking call, so run in a thread"
        # set the scheduled events for the current hour

        # get a time tuple for now
        ttnow = time.localtime()
        # get the timestamp of now
        rightnow = time.mktime(ttnow)

        # get the timestamp for the beginning of the current hour
        self.thishour = time.mktime((ttnow.tm_year,
                                     ttnow.tm_mon,
                                     ttnow.tm_mday,
                                     ttnow.tm_hour,
                                     0,                  # zero minutes
                                     0,                  # zero seconds
                                     ttnow.tm_wday,
                                     ttnow.tm_yday,
                                     ttnow.tm_isdst))

        # create times at which events are to occur
        # during the remaining part of this hour
        for evt_callback, mins in self.event_list:
            event_time = self.thishour + mins*60
            if event_time > rightnow:
                self.schedule.enterabs(time = event_time,
                                       priority = 1,
                                       action = evt_callback,
                                       argument = self.args
                                       )

        # schedule a final event to occur 30 seconds after last event
        last_event = self.event_list[-1]
        
        final_event_time = self.thishour + last_event[1]*60 + 30
        self.schedule.enterabs(time = final_event_time,
                               priority = 1,
                               action = self._create_next_hour_events
                               )


        # and run the schedule
        self.schedule.run()


# How to use

# create event callback functions
# add them in time order to the self.event_list attribute, as tuples of (event function, minutes after the hour)

# create a ScheduledEvents instance
# scheduled_events = ScheduledEvents(*args)
# this is a callable, use it as a thread target
# run_scheduled_events = threading.Thread(target=scheduled_events)
# and start the thread
# run_scheduled_events.start()

# the event callbacks should be set with whatever action is required



