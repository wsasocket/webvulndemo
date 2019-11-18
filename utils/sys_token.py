import base64
import hashlib
import threading
import uuid
from datetime import datetime

TOKEN_VALIDATE = 0
TOKEN_TIME_OUT = -1
TOKEN_INVALIDATE = -2


class sys_token(object):
    _instance_lock = threading.Lock()
    data_user = dict()
    data_csrf = dict()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(sys_token, "_instance"):
            with sys_token._instance_lock:
                if not hasattr(sys_token, "_instance"):
                    sys_token._instance = object.__new__(cls)
        return sys_token._instance

    def generate_login_token(self, username):
        uuid_string = str(uuid.uuid4())
        md5 = hashlib.md5()
        md5.update(username.encode())
        self.data_user[uuid_string] = [datetime.now(), base64.b64encode(md5.digest()).decode()]
        return uuid_string

    def check_login_token(self, login_token, username):
        if login_token in self.data_user.keys():
            delta_time = datetime.now() - self.data_user[login_token][0]
            if delta_time.total_seconds() // 60 > 30:
                # great than 30 miniuts drop it
                self.data_user.pop(login_token)
                return TOKEN_TIME_OUT
            md5 = hashlib.md5()
            md5.update(username.encode())
            if base64.b64encode(md5.digest()).decode() == self.data_user[login_token][1]:
                # validate and update time
                self.data_user[login_token][0] = datetime.now()
                return TOKEN_VALIDATE
        return TOKEN_INVALIDATE

    def generate_csrf_token(self):
        uuid_string = str(uuid.uuid4())
        self.data_csrf[uuid_string] = datetime.now()
        return uuid_string

    def check_csrf_token(self, csrf_token):

        if csrf_token in self.data_csrf.keys():
            print('find key', csrf_token)
            delta_time = datetime.now() - self.data_csrf[csrf_token]
            if delta_time.total_seconds() // 60 > 30:
                # great than 30 miniuts drop it
                self.data_csrf.pop(csrf_token)
                return TOKEN_TIME_OUT
            else:
                return TOKEN_VALIDATE
        return TOKEN_INVALIDATE
