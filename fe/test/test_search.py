import uuid
import pytest
from fe import conf
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.test.gen_book_data import GenBook
from fe.access import search
from fe.access import book as b
from fe.access import auth
from fe.access import seller



class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_search_user_id_".format(str(uuid.uuid1()))
        self.password = "test_search_password_".format(str(uuid.uuid1()))
        self.store_id = "test_search_store_id_".format(str(uuid.uuid1()))
        self.search = search.Search(conf.URL)
        self.auth = auth.Auth(conf.URL)
        code = self.auth.register(self.user_id, self.password)
        assert code == 200

        self.seller = seller.Seller(conf.URL, self.user_id, self.password)
        code = self.seller.create_store(self.store_id)
        assert code == 200

        book_db = b.BookDB()
        books = book_db.get_book_info(0, 5)
        self.search_info = {'title': [], 'tags': [], 'contents': [], 'authors_or_translators': [], 'publishers': []}
        for book in books:
            self.search_info['title'].append(book.title)
            self.search_info['tags'].append(book.title)
            self.seller.add_book(self.store_id, 0, book)
        yield


    def test_search(self):
        code = self.search.search_info(0,self.store_id,self.search_info)
        assert code == 200

        code = self.search.search_info(1000, self.store_id, self.search_info)
        assert code == 531



