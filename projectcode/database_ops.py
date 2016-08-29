
import os, sqlite3, hashlib

from ...skilift import FailPage, GoTo, ValidateError, ServerError, get_projectfiles_dir

_DATABASE_DIR_NAME =  'setup'
_DATABASE_NAME = 'setup.db'
_DATABASE_DIR = ''
_DATABASE_PATH = ''
_DATABASE_EXISTS = False

# This is the default access username
_USERNAME = "astro"
# This is the default  access password
_PASSWORD = "station"

# The password is stored hashed, with the username as a salt
_HASHED_PASSWORD =  hashlib.sha512(   _PASSWORD.encode('utf-8')  ).digest()


# default output values
# This dictionary has keys output names, and values being a tuple of (type, value, onpower)
# where type is one of 'text', 'boolean', 'integer'
# value is the default value to put in the database when first created
# onpower is True if the 'default value' is to be set on power up, or False if last recorded value is to be used

_CONTROLS = {"output01" : ('boolean', False, True)}


def get_control_names():
    "Returns list of control names, the list is sorted by boolean, integer and text items, and in name order within these categories"
    global _CONTROLS
    bool_list = sorted(name for name in _CONTROLS if _CONTROLS[name][0] == 'boolean')
    int_list =  sorted(name for name in _CONTROLS if _CONTROLS[name][0] == 'integer')
    text_list = sorted(name for name in _CONTROLS if _CONTROLS[name][0] == 'text')
    controls_list = []
    if bool_list:
        controls_list.extend(bool_list)
    if int_list:
        controls_list.extend(int_list)
    if text_list:
        controls_list.extend(text_list)
    return controls_list

def get_access_user():
    return _USERNAME

def get_default_password():
    return _PASSWORD

def check_database_exists(project):
    "Return True if database exists, must be called first, before any other database operation to set globals"
    global _DATABASE_DIR, _DATABASE_PATH, _DATABASE_EXISTS
    if _DATABASE_EXISTS:
        return True
    if not _DATABASE_PATH:
        _DATABASE_DIR =   database_directory(project)
        _DATABASE_PATH  = database_path(_DATABASE_DIR)
    _DATABASE_EXISTS = os.path.isdir(_DATABASE_DIR)
    return _DATABASE_EXISTS


def database_directory(project):
    "Returns database directory"
    global _DATABASE_DIR_NAME, _DATABASE_DIR
    if _DATABASE_DIR:
        return _DATABASE_DIR
    projectfiles = get_projectfiles_dir(project)
    return os.path.join(projectfiles, _DATABASE_DIR_NAME)


def database_path(database_dir):
    global _DATABASE_NAME, _DATABASE_PATH
    if _DATABASE_PATH:
        return _DATABASE_PATH
    return os.path.join(database_dir, _DATABASE_NAME)


def create_database():
    "Create a new database"
    global _DATABASE_DIR, _DATABASE_EXISTS, _DATABASE_PATH, _CONTROLS
    if _DATABASE_EXISTS:
        raise ServerError(message="Database directory exists, must be deleted first then reboot.")
    # make directory
    os.mkdir(_DATABASE_DIR)
    _DATABASE_EXISTS = True
    if not _DATABASE_PATH:
       raise ServerError(message="Unknown database path.")
    # make database
    con = sqlite3.connect(_DATABASE_PATH)
    try:
        # make access user password
        con.execute("create table users (username TEXT PRIMARY KEY, password BLOB)")
        # make a table for each output type, text, integer ande boolean
        con.execute("create table text_outputs (outputname TEXT PRIMARY KEY, value TEXT, default_on_pwr TEXT, onpower INTEGER)")
        con.execute("create table integer_outputs (outputname TEXT PRIMARY KEY, value INTEGER, default_on_pwr INTEGER, onpower INTEGER)")
        con.execute("create table boolean_outputs (outputname TEXT PRIMARY KEY, value INTEGER, default_on_pwr INTEGER, onpower INTEGER)")
        # After successful execute, con.commit() is called automatically afterwards
        # insert default values
        con.execute("insert into users (username, password) values (?, ?)", (_USERNAME, _HASHED_PASSWORD))
        for name in _CONTROLS:
            outputtype, outputvalue, onpower = _CONTROLS[name]
            if onpower:
                onpower = 1
            else:
                onpower = 0
            if outputtype == 'text':
                con.execute("insert into text_outputs (outputname, value, default_on_pwr, onpower) values (?, ?, ?, ?)", (name, outputvalue, outputvalue, onpower))
            elif outputtype == 'integer':
                con.execute("insert into integer_outputs (outputname, value, default_on_pwr, onpower) values (?, ?, ?, ?)", (name, outputvalue, outputvalue, onpower))
            elif outputtype == 'boolean':
                if outputvalue:
                    con.execute("insert into boolean_outputs (outputname, value, default_on_pwr, onpower) values (?, 1, 1, ?)", (name, onpower))
                else:
                    con.execute("insert into boolean_outputs (outputname, value, default_on_pwr, onpower) values (?, 0, 0, ?)", (name, onpower))
        con.commit()
    finally:
        con.close()


def open_database():
    "Opens the database, and returns the database connection"
    if not _DATABASE_EXISTS:
        raise ServerError(message="Database directory does not exist, call create_database.")
    if not _DATABASE_PATH:
       raise ServerError(message="Unknown database path.")
    # connect to database
    try:
        con = sqlite3.connect(_DATABASE_PATH)
    except:
        raise ServerError(message="Failed database connection.")
    return con


def close_database(con):
    "Closes database connection"
    con.close()


def get_password(user, con=None):
    "Return password for user, return None on failure"
    if not  _DATABASE_EXISTS:
        return
    if con is None:
        con = open_database()
        password = get_password(user, con)
        con.close()
    else:
        cur = con.cursor()
        cur.execute("select password from users where username = ?", (user,))
        result = cur.fetchone()
        if result is None:
            return
        password = result[0]
    return password


def set_password(user, password, con=None):
    "Return True on success, False on failure, this updates an existing user"
    if not  _DATABASE_EXISTS:
        return False
    if con is None:
        try:
            con = open_database()
            result = set_password(user, password, con)
            con.close()
            return result
        except:
            return False
    else:
        try:
            con.execute("update users set password = ? where username = ?", (password, user))
            con.commit()
        except:
            return False
    return True


def get_output(name, con=None):
    "Return output value for given name, return None on failure"
    global _CONTROLS, _DATABASE_EXISTS
    if name not in _CONTROLS:
        return
    if not  _DATABASE_EXISTS:
        return
    if con is None:
        con = open_database()
        outputvalue = get_output(name, con)
        con.close()
    else:
        outputtype = _CONTROLS[name][0]
        cur = con.cursor()
        if outputtype == 'text':
            cur.execute("select value from text_outputs where outputname = ?", (name,))
            result = cur.fetchone()
            if result is None:
                return
            outputvalue = result[0]
        elif outputtype == 'integer':
            cur.execute("select value from integer_outputs where outputname = ?", (name,))
            result = cur.fetchone()
            if result is None:
                return
            outputvalue = result[0]
        elif outputtype == 'boolean':
            cur.execute("select value from boolean_outputs where outputname = ?", (name,))
            result = cur.fetchone()
            if result is None:
                return
            outputvalue = bool(result[0])
        else:
            return
    return outputvalue


def set_output(name, value, con=None):
    "Return True on success, False on failure, this updates an existing output in the database"
    global _CONTROLS, _DATABASE_EXISTS
    if name not in _CONTROLS:
        return False
    if not  _DATABASE_EXISTS:
        return False
    if con is None:
        try:
            con = open_database()
            result = set_output(name, value, con)
            con.close()
            return result
        except:
            return False
    else:
        outputtype = _CONTROLS[name][0]
        try:
            if outputtype == 'text':
                con.execute("update text_outputs set value = ? where outputname = ?", (value, name))
            elif outputtype == 'integer':
                con.execute("update integer_outputs set value = ? where outputname = ?", (value, name))
            elif outputtype == 'boolean':
                if value:
                    con.execute("update boolean_outputs set value = 1 where outputname = ?", (name,))
                else:
                    con.execute("update boolean_outputs set value = 0 where outputname = ?", (name,))
            else:
                return False
            con.commit()
        except:
            return False
    return True


def power_up_values():
    """Check database exists, if not, return an empty dictionary.
        If it does, return a dictionary of outputnames:values from the database
        The values being either the default_on_pwr values for each output with onpower True
        or last saved values if onpower is False"""
    global _DATABASE_EXISTS, _CONTROLS
    if not _DATABASE_EXISTS:
        return {}
    # so database exists, for each output, get its value
    bool_tuple = (name for name in _CONTROLS if _CONTROLS[name][0] == 'boolean')
    int_tuple =  (name for name in _CONTROLS if _CONTROLS[name][0] == 'integer')
    text_tuple = (name for name in _CONTROLS if _CONTROLS[name][0] == 'text')
    outputdict = {}
    con = open_database()
    cur = con.cursor()
    # read values
    for name in bool_tuple:
        cur.execute("select value,  default_on_pwr, onpower from boolean_outputs where outputname = ?", (name,))
        result = cur.fetchone()
        if result is not None:
            if result[2]:
                outputdict[name] = bool(result[1])
            else:
                outputdict[name] = bool(result[0])
    for name in int_tuple:
        cur.execute("select value,  default_on_pwr, onpower from integer_outputs where outputname = ?", (name,))
        result = cur.fetchone()
        if result is not None:
            if result[2]:
                outputdict[name] = result[1]
            else:
                outputdict[name] = result[0]
    for name in text_tuple:
        cur.execute("select value,  default_on_pwr, onpower from text_outputs where outputname = ?", (name,))
        result = cur.fetchone()
        if result is not None:
            if result[2]:
                outputdict[name] = result[1]
            else:
                outputdict[name] = result[0]
    con.close()
    return outputdict
