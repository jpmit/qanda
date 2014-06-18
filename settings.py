"""Settings for the server."""

# print messages received and sent
DEBUG = False

# string date format used for DB storage
DATE_FORMAT = '%d %B %Y %H:%M'

# DB_TYPE can be one of:
# DB_FILE     - data is stored in flat files
# DB_POSTGRES - postgreSQL database
# DB_DUMMY    - fake data store, nothing stored
DB_FILE = 'file'
DB_POSTGRES = 'postgres'
DB_DUMMY = 'dummy'
DB_TYPE = DB_POSTGRES

# if DB_DROP = True, we will *DELETE* all tables from the DB when we
# start the server.
DB_DROP = False
