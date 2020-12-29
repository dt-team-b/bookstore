import psycopg2
from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from be.database import User, Store, Order_status, Order, Order_info, Book_info
import datetime
import uuid
import json
import logging
from be.model import error


class BuyerManager():
    def __init__(self):
        engine = create_engine('postgresql://root:123456@localhost:5432/bookstore')
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if self.session.query(User).filter_by(user_id=user_id).first() is None:
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if self.session.query(Store).filter_by(store_id=store_id).first() is None:
                return error.error_non_exist_store_id(store_id) + (order_id, )
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            pt = datetime.datetime.now()

            new_order = Order(id=uid, status=Order_status.pending, buyer_id=user_id, store_id=store_id, pt=pt)
            self.session.add(new_order)

            for book_id, count in id_and_count:
                cursor = self.session.query(Book_info).filter_by(id=book_id, store_id=store_id)
                row = cursor.first()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                inventory_count = row.inventory_count
                price = row.price

                if inventory_count < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor = self.session.query(Book_info).filter(Book_info.id==book_id, Book_info.store_id==store_id, Book_info.inventory_count >= count)
                rowcount = cursor.update({Book_info.inventory_count: Book_info.inventory_count - count})
                if rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                new_order_info = Order_info(order_id=uid, book_id=book_id, count=count, price=price)
                self.session.add(new_order_info)
            
            self.session.commit()
            order_id = uid
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            cursor = self.session.query(Order).filter_by(id=order_id, status=Order_status.pending)
            row = cursor.first()
            if row is None:
                return error.error_invalid_order_id(order_id)

            
            buyer_id = row.buyer_id
            store_id = row.store_id

            if buyer_id != user_id:
                return error.error_authorization_fail()

            cursor = self.session.query(User).filter_by(user_id=buyer_id)
            row = cursor.first()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row.balance
            if password != row.password:
                return error.error_authorization_fail()

            cursor = self.session.query(Store).filter_by(store_id=store_id)
            row = cursor.first()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row.owner

            if self.session.query(User).filter_by(user_id=seller_id).first() is None:
                return error.error_non_exist_user_id(seller_id)

            cursor = self.session.query(Order_info).filter_by(order_id=order_id)
            total_price = 0
            for row in cursor.all():
                count = row.count
                price = row.price
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor = self.session.query(User).filter(User.user_id==buyer_id, User.balance>=total_price)
            rowcount = cursor.update({User.balance: User.balance - total_price})
            if rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            cursor = self.session.query(User).filter(User.user_id==seller_id)
            rowcount = cursor.update({User.balance: User.balance + total_price})
            if rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

            cursor = self.session.query(Order).filter(Order.id==order_id)
            rowcount = cursor.update({Order.status: Order_status.paid, Order.pt: datetime.datetime.now()})
            if rowcount == 0:
                return error.error_invalid_order_id(order_id)

            self.session.commit()

        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.session.query(User).filter_by(user_id=user_id)
            row = cursor.first()
            if row is None:
                return error.error_authorization_fail()

            if row.password != password:
                return error.error_authorization_fail()

            cursor = self.session.query(User).filter(User.user_id==user_id)
            rowcount = cursor.update({User.balance: User.balance + add_value})
            if rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.session.commit()
            
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
