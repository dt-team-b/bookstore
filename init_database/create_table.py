import enum

import psycopg2
from sqlalchemy import create_engine, BigInteger
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, Boolean, LargeBinary, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://root:123456@localhost:5432/bookstore')
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    user_id = Column(String,primary_key=True,autoincrement=1)
    password = Column(String, nullable=False)
    balance = Column(Integer, nullable=False)
    token = Column(String, nullable=False)
    terminal = Column(String, nullable=False)

class Store(Base):
    __tablename__ = 'store'
    store_id = Column(String,nullable=False,primary_key=True,autoincrement=1)
    owner = Column(String, ForeignKey('user.user_id'), nullable=False, index = True)

class Book_info(Base):
    __tablename__ = 'book_info'
    id = Column(String, primary_key=True,autoincrement=1)
    title = Column(String, nullable=False)
    author = Column(String)
    publisher = Column(Text)
    original_title = Column(Text)
    translator = Column(Text)
    pub_year = Column(Text)
    pages = Column(Integer)
    binding = Column(Text)
    isbn = Column(Text)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)

#订单状态
class Order_status(enum.Enum):
    pending = 0     #等待付款
    cancelled = 1   #已取消
    paid = 2        #已付款等待发货
    delivering = 3  #已发货
    received = 4    #已确认收货

# 订单概要
class Order(Base):
    __tablename__ = 'order'
    id = Column(String, primary_key=True)
    status = Column(Enum(Order_status), nullable=False)
    buyer_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    store_id = Column(String, ForeignKey('store.store_id'), nullable=False)
    pt = Column(DateTime, nullable=False)

# 订单详情
class Order_info(Base):
    __tablename__ = 'order_info'
    order_id = Column(String, ForeignKey('order.id'), primary_key=True, nullable=False)
    book_id = Column(String, ForeignKey('book_info.id'), primary_key=True, nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    

#库存信息
class Inventory_info(Base):
    __tablename__ = 'inventory_info'
    store_id = Column(String, ForeignKey('store.store_id'),primary_key=True)
    book_id = Column(String,ForeignKey('book_info.id'),primary_key=True)
    inventory_count = Column(Integer,nullable=False)
    price = Column(Integer,nullable=False)  # 原价
    tags = Column(String,index=True)

#书籍图片
class book_pic(Base):
    __tablename__ = 'book_pic'
    store_id = Column(String, ForeignKey('store.store_id'), primary_key=True)
    book_id = Column(String, ForeignKey('book_info.id'), primary_key=True)
    picture = Column(LargeBinary,nullable=False)

if __name__ == "__main__":
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session.commit()
    print("finish")
    session.close()
