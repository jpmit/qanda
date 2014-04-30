"""Settings for the server."""

# print debug messages
DEBUG = True

# if _PERSISTENCE is True, the backend will try to restore all
# existing messages when it starts up.
PERSISTENCE = True

# DB type (this only matters if PERSISTENCE = True)
DB_FILE = 'file'
DB_POSTGRES = 'postgres'
DB_DUMMY = 'dummy'
DB_TYPE = DB_POSTGRES
