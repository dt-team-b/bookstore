import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from init_database.create_table import User, Store, Book, Order_status, Order, Inventory_info, book_pic
import time
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        engine = create_engine('postgresql://postgres:@localhost:5432/bookstore')
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.session.query(User).filter_by(user_id=user_id).exists():
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.session.query(Store).filter_by(store_id=store_id).exists():
                return error.error_non_exist_store_id(store_id) + (order_id, )
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            pt = time.time()

            for book_id, count in id_and_count:
                cursor = self.session.query(Inventory_info).filter_by(store_id=store_id, book_id=book_id)
                row = cursor.first()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id, )

                inventory_count = row.inventory_count
                price = row.price

                if inventory_count < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                

                cursor = self.session.query(Inventory_info).filter(Inventory_info.store_id==store_id, Inventory_info.book_id==book_id, Inventory_info.inventory_count>=count)
                rowcount = cursor.update({Inventory_info.inventory_count: Inventory_info.inventory_count - count})
                if rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id, )

                new_order = Order(order_id=uid, buyer_id=buyer_id, store_id=store_id, book_id=book_id, count=count, price=price, pt=pt, status=Order_status.pending)
                session.add(new_order)
            
            self.session.commit()
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            cursor = self.session.query(Order).filter_by(order_id=order_id, status=Order_status.pending)
            rows = cursor.all()
            if len(rows) == 0:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            cursor = conn.execute("SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor = conn.execute("SELECT store_id, user_id FROM user_store WHERE store_id = ?;", (store_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor = conn.execute("SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;", (order_id,))
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute("UPDATE user set balance = balance - ?"
                                  "WHERE user_id = ? AND balance >= ?",
                                  (total_price, buyer_id, total_price))
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute("UPDATE user set balance = balance + ?"
                                  "WHERE user_id = ?",
                                  (total_price, buyer_id))

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

            cursor = conn.execute("DELETE FROM new_order WHERE order_id = ?", (order_id, ))
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            cursor = conn.execute("DELETE FROM new_order_detail where order_id = ?", (order_id, ))
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            conn.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.execute("SELECT password  from user where user_id=?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "UPDATE user SET balance = balance + ? WHERE user_id = ?",
                (add_value, user_id))
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
