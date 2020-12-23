import logging
import os
import psycopg2
from sqlalchemy import create_engine


class Store:
    database: str
    user: str
    password: str
    host: str
    port: str

    def __init__(self):
        self.engine = create_engine('postgresql://postgres:@localhost:5432/bookstore')
    
    def get_engine(self):
        return self.engine


database_instance: Store = None


def init_database(database="bookstore",
                  user="root",
                  password="123456",
                  host="localhost",
                  port="5432"):
    global database_instance
    database_instance = Store(database, user, password, host, port)


def get_engine():
    global database_instance
    return database_instance.get_engine()
