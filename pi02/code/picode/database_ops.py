#######################################################
#
# database_ops.py
# creates sqlite database to hold username and password
# and to store output values
#
#######################################################



import os, sqlite3, hashlib, random

from datetime import date, timedelta, datetime

from skipole import FailPage, GoTo, ValidateError, ServerError

from . import hardware

_OUTPUTS = hardware.get_outputs()

# If it does not already exist, a database will be created in a directory
# beneath the projectfiles directory
_DATABASE_DIR_NAME =  'setup'
_DATABASE_NAME = 'setup.db'

# the following two values are set by the initial call to start_database
_DATABASE_PATH = ''
_DATABASE_EXISTS = False

# This is the access username
_USERNAME = "admin"
# This is the default access password, set when the database is first created
_PASSWORD = "password"


# The number of log messages to retain
_N_MESSAGES = 50


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
    hashed_password = hashlib.sha512( seed_password.encode('utf-8') ).digest()
    return hashed_password, seed


def start_database(project, projectfiles):
    """Must be called first, before any other database operation, to check if database
       exists, and if not, to create it, and to set globals _DATABASE_PATH and _DATABASE_EXISTS"""
    global _DATABASE_PATH, _DATABASE_EXISTS
    if _DATABASE_EXISTS:
        return
    database_dir = os.path.join(projectfiles, project, _DATABASE_DIR_NAME)
    # Set global variables
    _DATABASE_PATH = os.path.join(database_dir, _DATABASE_NAME)
    _DATABASE_EXISTS = True
    # make directory for database
    try:
        os.mkdir(database_dir)
    except FileExistsError:
        return
    # create the database
    con = open_database()
    try:
        # make access user password
        con.execute("create table users (username TEXT PRIMARY KEY, seed TEXT, password BLOB, cookie TEXT, last_connect TIMESTAMP)")
        # make a table for each output type, text, integer and boolean
        con.execute("create table text_outputs (outputname TEXT PRIMARY KEY, value TEXT, default_on_pwr TEXT, onpower INTEGER)")
        con.execute("create table integer_outputs (outputname TEXT PRIMARY KEY, value INTEGER, default_on_pwr INTEGER, onpower INTEGER)")
        con.execute("create table boolean_outputs (outputname TEXT PRIMARY KEY, value INTEGER, default_on_pwr INTEGER, onpower INTEGER)")
        # create table of log message
        con.execute("create table messages (mess_id integer primary key autoincrement, message TEXT, time timestamp)")
        # Create trigger to maintain only n messages
        n_messages = """CREATE TRIGGER n_messages_only AFTER INSERT ON messages
   BEGIN
     DELETE FROM messages WHERE mess_id <= (SELECT mess_id FROM messages ORDER BY mess_id DESC LIMIT 1 OFFSET %s);
   END;""" % (_N_MESSAGES,)
        con.execute(n_messages)

        # insert default values
        now = datetime.utcnow()
        hashed_password, seed = hash_password(_PASSWORD)
        con.execute("insert into users (username, seed, password, cookie, last_connect) values (?, ?, ?, ?, ?)", (_USERNAME, seed, hashed_password, "000", now))
        for name in _OUTPUTS:
            outputtype, outputvalue, onpower, bcm, description = _OUTPUTS[name]
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

        # set first log message
        set_message("New database created", con)

        con.commit()
    finally:
        con.close()


def open_database():
    "Opens the database, and returns the database connection"
    if not _DATABASE_EXISTS:
        raise ServerError(message="Database does not exist.")
    if not _DATABASE_PATH:
       raise ServerError(message="Unknown database path.")
    # connect to database
    try:
        con = sqlite3.connect(_DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        con.execute("PRAGMA foreign_keys = 1")
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


def get_cookie(user, con=None):
    "Return cookie for user, return None on failure"
    if (not  _DATABASE_EXISTS) or (not user):
        return
    if con is None:
        con = open_database()
        cookie = get_cookie(user, con)
        con.close()
    else:
        cur = con.cursor()
        cur.execute("select cookie from users where username = ?", (user,))
        result = cur.fetchone()
        if result is None:
            return
        cookie = result[0]
    return cookie


def set_cookie(user, cookie, con=None):
    """Return True on success, False on failure, this updates both the cookie and 
       the last_connect timestamp for an existing user. last_connect is updated because inevitably
       if a user cookie is set (implying the user has just logged in) then the last_connect should
       start from that moment. A log message is also created."""
    if not  _DATABASE_EXISTS:
        return False
    if con is None:
        try:
            con = open_database()
            result = set_cookie(user, cookie, con)
            con.close()
            return result
        except:
            return False
    else:
        try:
            if cookie == "000":
                # this logs the user out
                con.execute("update users set cookie = ? where username = ?", (cookie, user))
            else:
                now = datetime.utcnow()
                con.execute("update users set cookie = ?, last_connect = ? where username = ?", (cookie, now, user))
                set_message("%s logged in" % (user,), con)
            con.commit()
        except:
            return False
    return True


def get_last_connect(user, con=None):
    "Return last connection time for user, return None on failure"
    if (not  _DATABASE_EXISTS) or (not user):
        return
    if con is None:
        con = open_database()
        last_connect = get_last_connect(user, con)
        con.close()
    else:
        cur = con.cursor()
        cur.execute("select last_connect from users where username = ?", (user,))
        result = cur.fetchone()
        if result is None:
            return
        last_connect = result[0]
    return last_connect


def set_last_connect(user, last_connect, con=None):
    "Return True on success, False on failure, this updates an existing user"
    if not  _DATABASE_EXISTS:
        return False
    if con is None:
        try:
            con = open_database()
            result = set_last_connect(user, cookie, con)
            con.close()
            return result
        except:
            return False
    else:
        try:
            con.execute("update users set last_connect = ? where username = ?", (last_connect, user))
            con.commit()
        except:
            return False
    return True


def update_last_connect(user, con=None):
    "Return True on success, False on failure, this updates an existing user"
    if not  _DATABASE_EXISTS:
        return False
    if con is None:
        try:
            con = open_database()
            result = update_last_connect(user, con)
            con.close()
            return result
        except:
            return False
    else:
        try:
            now = datetime.utcnow()
            con.execute("update users set last_connect = ? where username = ?", (now, user))
            con.commit()
        except:
            return False
    return True


# log messages

def set_message(message, con=None):
    "Return True on success, False on failure, this inserts the message, if con given, does not commit"
    if (not  _DATABASE_EXISTS) or (not message):
        return False
    if con is None:
        try:
            con = open_database()
            result = set_message(message, con)
            if result:
                con.commit()
            con.close()
        except:
            return False
    else:
        try:
            con.execute("insert into messages (message, time) values (?,?)", (message, datetime.utcnow()))
        except:
            return False
    return True


def get_all_messages(con=None):
    "Return string containing all messages return None on failure"
    if not  _DATABASE_EXISTS:
        return
    if con is None:
        con = open_database()
        m_string = get_all_messages(con)
        con.close()
    else:
        cur = con.cursor()
        cur.execute("select message, time from messages order by mess_id DESC")
        m_string = ''
        for m in cur:
            m_string += m[1].strftime("%d %b %Y %H:%M:%S") + "\n" + m[0] + "\n\n"
    return m_string


# controlling outputs


def get_output(name, con=None):
    "Return output value for given name, return None on failure"
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


