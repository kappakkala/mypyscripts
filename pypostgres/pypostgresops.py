import os
import yaml
from datetime import datetime, timedelta
from dateutil.parser import parse
import psycopg2 as pg
import pandas as pd
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, schema

class Psyco(object):
    def __init__(self):
        # read db configuration from settings file
        self.read_settings()
        # creates a postgres connection
        self.create_connection()
        # get list of existing databases
        self.list_databases(display=True)

    def read_settings(self):
        # gets the current active location of the file
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        # read settings
        with open(__location__ + "\settings.yaml") as f:
            self.settings = yaml.safe_load(f)

    def create_connection(self, dbname=None, display=True):
        # establish a postgres database connection using a client
        settings = self.settings
        try:
            if dbname == None:
                self.conn = pg.connect(
                    host=settings["host"],
                    user=settings["username"],
                    password=settings["password"],
                )
            else:
                self.conn = pg.connect(
                    host=settings["host"],
                    user=settings["username"],
                    password=settings["password"],
                    database=dbname,
                )
            # suppresses cannot run inside a transaction block error
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            # create a cursor
            self.cur = self.conn.cursor()
            if display:
                if dbname == None:
                    print(f"Establishing connection to postgres databank.")
                else:
                    print(f"Establishing connection to postgres databank {dbname}.")
        except Exception:
            print("Error connecting to databank.")

    def list_databases(self, display=True):
        # lists all databases
        self.cur.execute("SELECT datname FROM pg_database;")
        # change tuple [('template1',), ('template0',)] to list
        self.list_db = [i[0] for i in self.cur.fetchall()]
        if display:
            print(self.list_db)

    def create_database(self, dbname):
        # creates a new database
        query = f"CREATE database {dbname};"
        try:
            self.cur.execute(query)
            print(f"Database {dbname} created successfully.")
        except Exception as e:
            print(f"No Database {dbname} is created : {e}")

    def create_schema(self, schema):
        query = f"CREATE SCHEMA IF NOT EXISTS {schema};"
        self.cur.execute(query)
        print(f"Schema {schema} is created")

    def prepare_schema(self, dbname, schema):
        # prepare a project schema in a specified database
        # create a new database
        self.create_database(dbname=dbname)
        # connect to the database
        self.create_connection(dbname=dbname)
        # create a schema
        self.create_schema(schema=schema)

    def drop_schema(self, schema):
        # drops an existing schema from the database
        query = f"DROP SCHEMA IF EXISTS {schema};"
        self.cur.execute(query)
        print(f"Schema {schema} is deleted")

    def empty_table(self, schema, tablename):
        # to prevent duplicate insertion using the same id, we delete all data from table
        query = f"TRUNCATE {schema}.{tablename}"
        self.cur.execute(query)
        print(f"Emptied data from table {schema}.{tablename}")

    def drop_table(self, schema, tablename):
        # delete table if it already exists
        query = f"DROP TABLE IF EXISTS {schema}.{tablename}"
        self.cur.execute(query)
        print(f"Table {tablename} deleted from schema {schema}")

    def drop_database(self, dbname):
        # disconnect the active database connection
        self.create_connection(display=False)
        # deletes an exisiting database
        query = f"DROP database {dbname};"
        try:
            self.cur.execute(query)
            print(f"Database {dbname} deleted successfully.")
        except Exception as e:
            print(f"No Database {dbname} is deleted : {e}")

    def close_connection(self):
        # closes the connection to postgres databank
        self.cur.close()
        self.conn.close()
        print("Database connection closed.")


class Alchemy(object):
    def __init__(self):
        # read db configuration from settings file
        self.read_settings()
        # establish database connection
        self.create_connection()
        # get list of existing databases
        self.list_databases(display=True)
    
    def read_settings(self):
        # gets the current active location of the file
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        # read settings
        with open(__location__ + "\settings.yaml") as f:
            self.settings = yaml.safe_load(f)

    def create_connection(self, dbname=None, display=True):
        try:
            if dbname == None:
                url = URL.create(**self.settings)
            else:
                self.settings['database'] = dbname
                url = URL.create(**self.settings)
            # start engine
            self.engine = create_engine(url)
            # connect engine
            self.conn = self.engine.connect()
            # set isolation/commit
            self.conn.execute("commit")
            if display:
                if dbname == None:
                    print(f"Establishing connection to postgres databank.")
                else:
                    print(f"Establishing connection to postgres databank {dbname}.")
        except Exception as e:
            print(f"Could not establish connection : {e}")
    
    def list_databases(self, display=True):
        # lists all databases
        list_db = self.engine.execute('SELECT datname FROM pg_database;').fetchall()
        # change tuple [('template1',), ('template0',)] to list
        self.list_db = [i[0] for i in list_db]
        if display:
            print(self.list_db)
        
    def create_database(self, dbname):
        # creates a new database
        query = f"CREATE database {dbname};"
        try:
            self.conn.execute(query)
            print(f"Database {dbname} created successfully.")
        except Exception as e:
            print(f"No Database {dbname} is created : {e}")
        
    def create_schema(self, schema_name):
        # create a new schema if it doesn't exist
        if not self.engine.dialect.has_schema(self.engine, schema_name):
            self.engine.execute(schema.CreateSchema(schema_name))
            print(f"Schema {schema_name} is created")
    
    def drop_schema(self, schema_name):
        # delete an already existing schema
        if self.engine.dialect.has_schema(self.engine, schema_name):
            self.engine.execute(schema.DropSchema(schema_name))
            print(f"Schema {schema_name} is deleted")

    def prepare_schema(self, dbname, schema):
        # prepare a project schema in a specified database
        # create a new database
        self.create_database(dbname=dbname)
        # connect to the database
        self.create_connection(dbname=dbname)
        # create a schema
        self.create_schema(schema_name=schema)

    def drop_database(self, dbname):
        # disconnect the active database connection
        self.create_connection(display=False)
        # deletes an exisiting database
        query = f"DROP database {dbname};"
        try:
            self.conn.execute(query)
            print(f"Database {dbname} deleted successfully.")
        except Exception as e:
            print(f"No Database {dbname} is deleted : {e}")

    def close_connection(self):
        self.conn.close()
        print("Database connection closed.")
