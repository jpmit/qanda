Q&A App
-------

Copyright (c) James Mithen 2014.

This is a Python webapp for running 'live Q&A sessions'.  On the
server side, it requires Tornado (web framework) and psycopg2
(database adaptor for PostgreSQL).  The browser on the client side
must support the Websockets protocol; in practice this is the case for
nearly all modern browsers at the time of writing.  The app is
currently deployed on Heroku at http://qandasession.herokuapp.com. It
can also be run locally.

Configuration is via the settings.py file.  In settings.py,
among other things, the backend can be configured to use as a database
either a flat file or PostgreSQL (PostgreSQL is required for Heroku
deployment).  Alternatively, data persistence on server restarts can
be disabled by selecting the 'dummy' database.

To run the server locally, type:

    $ python server.py

Then in navigate to localhost:9500 in a web browser.

TODO
----

* Add username to lobby page (?)
* Refactor backend, esp. sending of messages
* allow users to upload a photo
* a + and - expandable thing for each message
* better logging (?)
* message if not using a Websocket capable browser
