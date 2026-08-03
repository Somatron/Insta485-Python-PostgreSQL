"""Insta485 model (database) API."""
import sqlite3
import flask
import insta485
import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv

def grab_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if 'psql_db' not in flask.g:
        load_dotenv()
        
        env_db_url = os.environ.get("POSTGRESQL_URL_CONNECTION")
        #get a proper postgreSQL connect URI from config or enviroment var
        db_url = insta485.app.config.get('DATABASE_URL', f"{env_db_url}")
        #dont FORGET .GET USES () not []

        #Connect and attack the built in dictionary row_factory
        flask.g.psql_db = psycopg.connect(db_url, row_factory=dict_row)
        #PostgreSQL handles PRAGMA foreign keys naturally 

    return flask.g.psql_db #this transfers a PostgreSQL database into a real python dictionary, like Python dict: {'id': 1, 'name': 'obama'} etc

"""
example = flask.g.psql_db.cursor()

example.execute("SELECT id, name FROM users;")
returning us with {'id': 1, 'name': 'obama'}

user = example.fetch()
print(user["name"]) 
"""

@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    psql_db = flask.g.pop('psql_db', None)
    if psql_db is not None:
        if error is None:
          psql_db.commit()
        else:
          psql_db.rollback() #Incase our Flask route crashes mid request, rollback
        psql_db.close()
