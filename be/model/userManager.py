import jwt
import time
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from be.database import User
from be.model import error

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class UserManager():
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        engine = create_engine('postgresql://root:123456@localhost:5432/bookstore')
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            new_gamer = User(
                user_id=user_id,
                password = password,
                balance = 0,
                token = token,
                terminal = terminal
            )
            self.session.add(new_gamer)
            self.session.commit()
        except BaseException:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        get_token = self.session.query(User).filter(User.user_id==user_id).first()

        if get_token is None:
            return error.error_authorization_fail()
        db_token = get_token.token
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        get_passwd = self.session.query(User).filter(User.user_id==user_id).first()
        
        if get_passwd is None:
            return error.error_authorization_fail()

        if password != get_passwd.password:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            user_ = self.session.query(User).filter(User.user_id == user_id).first()
            if user_ is None:
                return error.error_authorization_fail() + ("", )
            user_.token = token
            user_.terminal = terminal
            self.session.commit()
            
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> (int,str):
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            user_ = self.session.query(User).filter(User.user_id == user_id).first()

            if user_ is None:
                return error.error_authorization_fail()
            user_.token = dummy_token
            user_.terminal = terminal
            self.session.commit()
            
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message
            query = self.session.query(User).filter(User.user_id == user_id)
            query.delete()

            if query.first() is None:
                self.session.commit()
            else:
                return error.error_authorization_fail()
            
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> (int,str):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            user_ = self.session.query(User).filter(User.user_id == user_id).first()
            user_.password = new_password
            user_.token = token
            user_.terminal = terminal
            
            if user_ is None:
                return error.error_authorization_fail()
            user_.password = new_password
            user_.token = token
            user_.terminal = terminal
            self.session.commit()
            
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


