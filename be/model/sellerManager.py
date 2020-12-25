from be.model import error
from be.model.database import User, Inventory_info, Store, Book_info
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class SellerManager():
    def __init__(self):
        engine = create_engine(
            'postgresql://root:123456@localhost:5432/bookstore')
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

            book = Book_info(
                id = book_info["id"],
                title = book_info["title"],
                author = book_info.get("author", ""),
                publisher = book_info.get("publisher", ""),
                original_title = book_info.get("original_title", ""),
                translator = book_info.get("translator", ""),
                pub_year = book_info.get("pub_year", ""),
                pages = book_info.get("pages", 0),
                binding = book_info.get("binding", ""),
                isbn = book_info.get("isbn", ""),
                author_intro = book_info.get("author_intro", ""),
                book_intro = book_info.get("book_intro", ""),
                content = book_info.get("content", "")
            )

            self.session.add(book)

            pictures = book_info.get("pictures", [])
            for pic in pictures:
                book_pic = book_pic(
                    book_id = book.id,
                    store_id = store_id,
                    picture = pic
                )
                self.session.add(book_pic)
            

            self.session.commit()
            self.session.close()
            
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_inventory(self, user_id: str, store_id: str, book_info: dict,
                      stock_level: int):
        try:
            inventory_info = Inventory_info(
                store_id = store_id,
                book_id = book_info['id'],
                inventory_count = stock_level,
                price = book_info['price'],
                tag = book_info.get("tags", "")
            )
            self.session.add(inventory_info)

            self.session.commit()
            self.session.close()
            
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

            inventory_info = self.session.query(Inventory_info).filter(Inventory_info.store_id == store_id,
                                                                       Inventory_info.book_id == book_id).first()
            #print(inventory_info.inventory_count)
            inventory_info.inventory_count += add_stock_level
            
            self.session.commit()
            self.session.close()
            
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            store = Store(
                store_id = store_id,
                owner = user_id
            )
            self.session.add(store)
            
            self.session.commit()
            self.session.close()
            
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
            Inventory_info.store_id == store_id,
            Inventory_info.book_id == book_id).all()
        if len(book) == 0:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        store = self.session.query(Store).filter(Store.store_id == store_id).all()
        if len(store) == 0:
            return False
        else:
            return True
