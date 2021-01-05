from be.model import error
from be.database import User, Store, Book_info, Book_pic, Book_tag
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class SellerManager():
    def __init__(self):
        engine = create_engine(
            'postgresql://root:123456@localhost:5432/bookstore')
        self.session = sessionmaker(bind=engine)()

    def add_book(self, user_id: str, store_id: str, book_info: dict, stock_level: int):
        try:
            book_id = book_info.get("id")

            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            book = Book_info()
            book.id = book_id
            book.title = book_info.get("title")
            book.store_id = store_id

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

            book.inventory_count = stock_level

            book.price = book_info.get("price", 0)

            self.session.add(book)

            book.tags = book_info.get("tags", [])
            for tag in book.tags:
                book_tag = Book_tag()
                book_tag.id = book.id
                book_tag.store_id = store_id
                book_tag.tag = tag
                self.session.add(book_tag)

            pictures = book_info.get("pictures", [])
            for pic in pictures:
                book_pic = Book_pic()
                book_pic.book_id = book.id
                book_pic.store_id = store_id
                book_pic.picture = pic.encode('ascii')
                self.session.add(book_pic)

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

            book_info = self.session.query(Book_info).filter(store_id == store_id
                                                             , book_id == book_id).first()
            book_info.inventory_count += add_stock_level
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
            
            store = Store()
            store.store_id = store_id
            store.owner = user_id
            self.session.add(store)
            self.session.commit()
            self.session.close()

        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def deliver(self, store_id: str, order_id: str) -> (int, str):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)

            cursor = self.session.query(Order).filter_by(id=order_id, store_id=store_id, status=Order_status.paid)
            rowcount = cursor.update({Order.status: Order_status.delivering})
            if rowcount == 0:
                return error.error_invalid_order_id(order_id)

            self.session.commit()
            self.session.close()
            
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
        

    def user_id_exist(self, user_id):
        return self.session.query(User).filter(User.user_id == user_id).first() is not None

    def book_id_exist(self, store_id, book_id):
        return self.session.query(Book_info).filter(Book_info.store_id == store_id,
                                                    Book_info.id == book_id).first() is not None

    def store_id_exist(self, store_id):
        return self.session.query(Store).filter(Store.store_id == store_id).first() is not None
