import logging
import os
import psycopg2 as pg


class Store:
    database: str
    user: str
    password: str
    host: str
    port: str

    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS user ("
                "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
                " PRIMARY KEY(store_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            conn.commit()
        except pg.Error as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self) -> pg._psycopg.connection:
        return pg.connect(database=self.database,
                          user=self.user,
                          password=self.password,
                          host=self.host,
                          port=self.port)


database_instance: Store = None


def init_database(database="bookstore",
                  user="root",
                  password="123456",
                  host="localhost",
                  port="5432"):
    global database_instance
    database_instance = Store(database, user, password, host, port)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
