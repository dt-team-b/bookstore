import psycopg2
from sqlalchemy.orm import sessionmaker

from be.database import Book_pic, Book_tag
from be.model import error, sellerManager
from sqlalchemy import create_engine

book_info_column = ['book_info.id', 'book_info.store_id', 'title', 'author', 'publisher', 'original_title',
                    'translator',
                    'pub_year', 'pages', 'binding', 'isbn', 'author_intro', 'content', 'inventory_count', 'price']


class SearchManager():
    def __init__(self):
        engine = create_engine(
            'postgresql://root:123456@localhost:5432/bookstore')
        connection = engine.raw_connection()
        self.session = sessionmaker(bind=engine)()
        self.cursor = connection.cursor()

    def search(self, store_id: str, page_id: int, search_info: dict) -> (int, str, list):
        try:
            if not sellerManager.SellerManager().store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + ([],)

            sql: str = "select " + ','.join(book_info_column) + " from book_info "

            title = search_info.get("title", [])
            tags = search_info.get("tags", [])
            contents = search_info.get("contents", [])
            authors_or_translators = search_info.get("authors_or_translators", [])
            publishers = search_info.get("publishers", [])

            predicate = []
            if len(title) != 0:
                predicate.append(self.get_like_predicate('title', title))
            if len(contents) != 0:
                predicate.append(self.get_like_predicate('contents', contents))
            if len(authors_or_translators) != 0:
                predicate.append('(' + self.get_like_predicate('author', authors_or_translators) + ' or ' +
                                 self.get_like_predicate('translator', authors_or_translators) + ')')
            if len(publishers) != 0:
                predicate.append(self.get_like_predicate('publisher', publishers))
            if len(tags) != 0:
                sql += ",book_tag "
                predicate.append(self.get_tag_predicate('tags', tags))

            while None in predicate:
                predicate.remove(None)
            if len(predicate) != 0:
                sql += 'where ' + ' and '.join(predicate) + ";"
            print(sql)
            self.cursor.execute(sql)
            self.cursor.scroll(page_id * 30)
            result = [self.trans_result(x) for x in self.cursor.fetchmany(30)]

            for book in result:
                pictures = []
                tags = []
                for pic in self.session.query(Book_pic).filter(Book_pic.store_id == book['store_id'],
                                                               Book_pic.book_id == book['id']):
                    pictures.append(pic.picture)
                for tag in self.session.query(Book_tag).filter(Book_tag.store_id == book['store_id'],
                                                               Book_tag.id == book['id']):
                    tags.append(tag.tag)
                book['pictures'] = pictures
                book['tags'] = tags



        except psycopg2.ProgrammingError as e:
            return 531, "{}".format("page id not exists."), []
        except BaseException as e:
            return str(e), "{}".format(repr(e)), []

        return 200, "ok", result

    def trans_result(self, result):
        cnt = 0
        ans = {}
        for column in book_info_column:
            ans[column.split('.')[-1]] = result[cnt]
            cnt += 1
        return ans

    def get_like_predicate(self, attribute, keywords):
        ans = []
        for kw in keywords:
            ans.append(attribute + " like '%" + kw + "%'")

        return '(' + ' or '.join(ans) + ')'

    def get_tag_predicate(self, attribute, keywords):
        ans = []
        for kw in keywords:
            ans.append("tag = '{}'".format(kw))

        return 'book_tag.id = book_info.id and (' + ' or '.join(ans) + ')'
