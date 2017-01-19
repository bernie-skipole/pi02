
import os, sqlite3, hashlib, random

from ...skilift import FailPage, GoTo, ValidateError, ServerError, get_projectfiles_dir

from . import factory_defaults

_OUTPUTS = factory_defaults.get_outputs()

_DATABASE_DIR_NAME =  'setup'
_DATABASE_NAME = 'setup.db'
_DATABASE_DIR = ''
_DATABASE_PATH = ''
_DATABASE_EXISTS = False

# This is the default access username
_USERNAME = "astro"
# This is the default  access password
_PASSWORD = "station"
# The project name
_PROJECT = ''


def get_access_user():
    return _USERNAME

def get_default_password():
    return _PASSWORD

def hash_password(password, seed=None):
    "Return (hashed_password, seed) if no seed given, create a random one"
    if not seed:
        # create seed
        seed = str(random.SystemRandom().randint(1000000, 9999999))
    seed_password = seed +  password
    hashed_password = hashlib.sha512(   seed_password.encode('utf-8')  ).digest()
    return hashed_password, seed

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


def start_database(project, projectfiles):
    """Must be called first, before any other database operation to set globals"""
    global _DATABASE_DIR, _DATABASE_PATH, _DATABASE_EXISTS, _PROJECT, _OUTPUTS
    if _DATABASE_EXISTS:
        return
    # Set global variables
    _PROJECT = project
    _DATABASE_DIR =   database_directory(projectfiles)
    _DATABASE_PATH  = database_path(_DATABASE_DIR)
    _DATABASE_EXISTS = os.path.isfile(_DATABASE_PATH)
    if _DATABASE_EXISTS:
        return
    # make directory
    if not os.path.isdir(_DATABASE_DIR):
        os.mkdir(_DATABASE_DIR)
    _DATABASE_EXISTS = True
   # create the database
    con = open_database()
    try:
        # make access user password
        con.execute("create table users (username TEXT PRIMARY KEY, seed TEXT, password BLOB)")
        # make a table for each output type, text, integer ande boolean
        con.execute("create table text_outputs (outputname TEXT PRIMARY KEY, value TEXT, default_on_pwr TEXT, onpower INTEGER)")
        con.execute("create table integer_outputs (outputname TEXT PRIMARY KEY, value INTEGER, default_on_pwr INTEGER, onpower INTEGER)")
        con.execute("create table boolean_outputs (outputname TEXT PRIMARY KEY, value INTEGER, default_on_pwr INTEGER, onpower INTEGER)")
        # insert default values
        hashed_password, seed = hash_password(_PASSWORD)
        con.execute("insert into users (username, seed, password) values (?, ?, ?)", (_USERNAME, seed, hashed_password))
        for name in _OUTPUTS:
            outputtype, outputvalue, onpower = _OUTPUTS[name]
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
    "Return (hashed_password, seed) for user, return None on failure"
    if (not  _DATABASE_EXISTS) or (not user):
        return
    if con is None:
        con = open_database()
        result = get_password(user, con)
        con.close()
    else:
        cur = con.cursor()
        cur.execute("select password, seed from users where username = ?", (user,))
        result = cur.fetchone()
    return result


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
        hashed_password, seed = hash_password(password)
        try:
            con.execute("update users set password = ?, seed=? where username = ?", (hashed_password, seed, user))
            con.commit()
        except:
            return False
    return True


def get_output(name, con=None):
    "Return output value for given name, return None on failure"
    global _OUTPUTS, _DATABASE_EXISTS
    if name not in _OUTPUTS:
        return
    if not  _DATABASE_EXISTS:
        return
    if con is None:
        con = open_database()
        outputvalue = get_output(name, con)
        con.close()
    else:
        outputtype = _OUTPUTS[name][0]
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
    global _OUTPUTS, _DATABASE_EXISTS
    if name not in _OUTPUTS:
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
        outputtype = _OUTPUTS[name][0]
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
    global _DATABASE_EXISTS, _OUTPUTS
    if not _DATABASE_EXISTS:
        return {}
    # so database exists, for each output, get its value
    bool_tuple = (name for name in _OUTPUTS if _OUTPUTS[name][0] == 'boolean')
    int_tuple =  (name for name in _OUTPUTS if _OUTPUTS[name][0] == 'integer')
    text_tuple = (name for name in _OUTPUTS if _OUTPUTS[name][0] == 'text')
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


def get_power_values(name):
    """Check database exists, if not, return an empty tuple.
        If it does, return a tuple of (default_on_pwr, onpower) from
        the database for the given outputname
"""
    global _DATABASE_EXISTS, _OUTPUTS
    if name not in _OUTPUTS:
        return ()
    if not _DATABASE_EXISTS:
        return ()
    # so database exists
    con = open_database()
    cur = con.cursor()
    if _OUTPUTS[name][0] == 'boolean':
        cur.execute("select default_on_pwr, onpower from boolean_outputs where outputname = ?", (name,))
        result = cur.fetchone()
        if result is None:
            out = ()
        else:
            out = (bool(result[0]), bool(result[1]))
    elif _OUTPUTS[name][0] == 'integer':
        cur.execute("select default_on_pwr, onpower from integer_outputs where outputname = ?", (name,))
        result = cur.fetchone()
        if result is None:
            out = ()
        else:
            out = (result[0], bool(result[1]))
    elif _OUTPUTS[name][0] == 'text':
        cur.execute("select default_on_pwr, onpower from text_outputs where outputname = ?", (name,))
        result = cur.fetchone()
        if result is None:
            out = ()
        else:
            out = (result[0], bool(result[1]))
    else:
        out = ()
    con.close()
    return out


def set_power_values(name, default_on_pwr, onpower, con=None):
    "Return True on success, False on failure, this updates a name output power-up values"
    global _DATABASE_EXISTS, _OUTPUTS
    if name not in _OUTPUTS:
        return False
    if not  _DATABASE_EXISTS:
        return False
    if con is None:
        try:
            con = open_database()
            result = set_power_values(name, default_on_pwr, onpower, con)
            con.close()
            return result
        except:
            return False
    else:
        try:
            if onpower:
                onpower = 1
            else:
                onpower = 0
            if _OUTPUTS[name][0] == 'boolean':
                if default_on_pwr:
                    default_on_pwr = 1
                else:
                    default_on_pwr = 0
                con.execute("update boolean_outputs set default_on_pwr = ?,  onpower = ? where outputname= ?", (default_on_pwr, onpower, name))
            elif _OUTPUTS[name][0] == 'integer':
                con.execute("update integer_outputs set default_on_pwr = ?,  onpower = ? where outputname= ?", (default_on_pwr, onpower, name))
            elif _OUTPUTS[name][0] == 'text':
                con.execute("update text_outputs set default_on_pwr = ?,  onpower = ? where outputname= ?", (default_on_pwr, onpower, name))
            con.commit()
        except:
            return False
    return True
