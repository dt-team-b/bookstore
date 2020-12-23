import psycopg2
# import
from sqlalchemy import create_engine, BigInteger
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres:@localhost:5432/bookstore')

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer,primary_key=True,autoincrement=1)
    username = Column(String(256), nullable=False,unique=True, index=True)
    password = Column(String(256), nullable=False)
    balance = Column(Integer, nullable=False)
    token = Column(String(400), nullable=False)
    terminal = Column(String(256), nullable=False)

class Store(Base):
    __tablename__ = 'store'
    store_id = Column(Integer,nullable=False,primary_key=True,autoincrement=1)
    store_name = Column(String(256),nullable=False,index=True,unique=True)
    # store_id = Column(String(128), ForeignKey('open_store.store_id'), nullable=False, index = True)
    owner = Column(Integer, ForeignKey('user.user_id'), nullable=False, index = True)
    # stock_level = Column(Integer, nullable=False)
    # price = Column(Integer, nullable=False)  # 售价

class Book(Base):
    __tablename__ = 'book'
    book_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text)
    publisher = Column(Text)
    original_title = Column(Text)
    translator = Column(Text)
    pub_year = Column(Text)
    pages = Column(Integer)
    original_price = Column(Integer)  # 原价
    currency_unit = Column(Text)
    binding = Column(Text)
    isbn = Column(Text)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)
    tags = Column(Text)
    picture = Column(LargeBinary)

# 用户商店关系表
# class Open_store(Base):
#     __tablename__ = 'open_store'
#     user_id = Column(Integer, ForeignKey('user.username'), nullable=False, index = True)
#     store_id = Column(String(128), nullable=False, unique=True, index = True) # 这里的store不可能重复
#     __table_args__ = (
#         PrimaryKeyConstraint('user_id', 'store_id'),
#         {},
#     )


# 未付款订单
class New_order_pend(Base):
    __tablename__ = 'new_order_pend'
    order_id = Column(Integer, primary_key=True,autoincrement=1)
    buyer_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    store_id = Column(Integer, ForeignKey('store.store_id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    pt = Column(DateTime, nullable=False)


# 已取消订单
class New_order_cancel(Base):
    __tablename__ = 'new_order_cancel'
    order_id = Column(Integer, primary_key=True, autoincrement=1)
    buyer_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    store_id = Column(Integer, ForeignKey('store.store_id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    pt = Column(DateTime, nullable=False)


# 已付款订单
class New_order_paid(Base):
    __tablename__ = 'new_order_paid'
    order_id = Column(Integer, primary_key=True, autoincrement=1)
    buyer_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    store_id = Column(Integer, ForeignKey('store.store_id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    pt = Column(DateTime, nullable=False)
    status = Column(Integer, nullable=False)  # 0为待发货，1为已发货，2为已收货


# 订单中的书本信息
# class Order_content(Base):
#     __tablename__ = 'order_content'
#     order_id = Column(Integer, primary_key=True)
#     book_id = Column(Integer,ForeignKey('book.book_id'),nullable=False)
#     count = Column(Integer, nullable=False)
#     price = Column(Integer, nullable=False)
#     __table_args__ = (
#         PrimaryKeyConstraint('order_id', 'book_id'),
#         {},
#     )

#库存信息
class Inventory_info(Base):
    __tablename__ = 'inventory_info'
    store_id = Column(Integer, ForeignKey('store.store_id'),primary_key=True)
    book_id = Column(Integer,ForeignKey('book.book_id'),primary_key=True)
    inventory_count = Column(Integer,nullable=False)

#书籍图片
class book_pic(Base):
    __tablename__ = 'book_pic'
    store_id = Column(Integer, ForeignKey('store.store_id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), primary_key=True)
    picture = Column(LargeBinary,nullable=False)
    # pic_id = Column(Integer, ForeignKey('pic.pic_id'), primary_key=True)

if __name__ == "__main__":
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all(engine)
    # 提交即保存到数据库
    session.commit()
    print("finish")
    # 关闭session
    session.close()
