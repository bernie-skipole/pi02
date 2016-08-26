
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
_HASHED_PASSWORD =  hashlib.sha512(   (_USERNAME + _PASSWORD).encode('utf-8')  ).digest()


def get_access_user():
    return _USERNAME

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
    global _DATABASE_DIR, _DATABASE_EXISTS, _DATABASE_PATH
    if _DATABASE_EXISTS:
        raise ServerError(message="Database directory exists, must be deleted first then reboot.")
    # make directory
    os.mkdir(_DATABASE_DIR)
    _DATABASE_EXISTS = True
    if not _DATABASE_PATH:
       raise ServerError(message="Unknown database path.")
    # make database
    con = sqlite3.connect(_DATABASE_PATH)
    # make access user password
    con.execute("create table users (username TEXT PRIMARY KEY, password BLOB)")
    # After successful execute, con.commit() is called automatically afterwards
    with con:
        con.execute("insert into users (username, password) values (?, ?)", (_USERNAME, _HASHED_PASSWORD))
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
            with con:
                con.execute("update users set password = ? where username = ?", (password, user))
        except:
            return False
    return True
