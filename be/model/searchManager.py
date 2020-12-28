from be.model import error, sellerManager
from be.database import User, Store, Book_info, Book_pic
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class SearchManager():
    def __init__(self):
        engine = create_engine(
            'postgresql://root:123456@localhost:5432/bookstore')
        connection = engine.raw_connection()
        self.cursor = connection.cursor()

    def search(self, store_id: str, page_id: int, search_info: dict) -> (int, str, list):
        try:
            if not sellerManager.SellerManager().store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + ([],)

            """
            search code
            """

        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok", [{"title": "The man who changed China"}]
