from be.model import error, database
from be.model.database import User, Inventory_info, Store, Book_info
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError


class SellerManager():
    def __init__(self):
        engine = create_engine(
            'postgresql+psycopg2://postgres:wengsy@localhost:5432/bookstore')
        self.session = sessionmaker(bind=engine)()

    def add_book(self, user_id: str, store_id: str, book_info: dict):
        try:
            book_id = book_info['id']

            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            book = database.Book_info()
            book.id = book_info["id"]
            book.title = book_info["title"]

            book.author = book_info.get("author", None)
            book.publisher = book_info.get("publisher", None)
            book.original_title = book_info.get("original_title", None)
            book.translator = book_info.get("translator", None)
            book.pub_year = book_info.get("pub_year", None)
            book.pages = book_info.get("pages", 0)
            book.binding = book_info.get("binding", None)
            book.isbn = book_info.get("isbn", None)
            book.author_intro = book_info.get("author_intro", None)
            book.book_intro = book_info.get("book_intro", None)
            book.content = book_info.get("content", None)

            self.session.add(book)

            pictures = book_info.get("pictures", [])
            for pic in pictures:
                book_pic = database.book_pic()
                book_pic.book_id = book.id
                book_pic.store_id = store_id
                book_pic.picture = pic
                self.session.add(book_pic)

            self.session.commit()
            self.session.close()
        except IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_inventory(self, user_id: str, store_id: str, book_info: dict,
                      stock_level: int):
        try:
            book_id = book_info['id']

            inventory_info = database.Inventory_info()
            inventory_info.store_id = store_id
            inventory_info.book_id = book_id
            inventory_info.inventory_count = stock_level

            inventory_info.price = book_info['price']
            inventory_info.tag = book_info.get("tags", None)
            self.session.add(inventory_info)

            self.session.commit()
            self.session.close()
        except IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str,
                        add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            inventory_info = self.session.query(Inventory_info).filter(Inventory_info.store_id == store_id
                                                                       , Inventory_info.book_id == book_id).first()
            print(inventory_info.inventory_count)
            inventory_info.inventory_count += add_stock_level
            self.session.commit()
            self.session.close()

        except IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            store = database.Store()
            store.store_id = store_id
            store.owner = user_id
            self.session.add(store)
            self.session.commit()
            self.session.close()
        except IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def user_id_exist(self, user_id):
        user = self.session.query(User).filter(User.user_id == user_id).all()
        if len(user) == 0:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        book = self.session.query(Inventory_info).filter(
            Inventory_info.store_id == store_id
            , Inventory_info.book_id == book_id).all()
        if len(book) == 0:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        store = self.session.query(Store).filter(
            Store.store_id == store_id).all()
        if len(store) == 0:
            return False
        else:
            return True
