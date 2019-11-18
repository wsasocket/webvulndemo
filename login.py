import base64
import hashlib
import json
import os
import sqlite3

import mysql.connector
from flask import Flask
from flask import send_file
from flask_restful import Api, Resource, reqparse

from edit import edit_info
from utils.sys_token import sys_token

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('user')
parser.add_argument('password')
parser.add_argument('init')
# From the request headers
parser.add_argument('Host', location='headers')


class root(Resource):
    def get(self):
        return send_file('login.html')
        # with open('login2.html','r') as fp:
        #     buf = fp.readlines()
        #     return buf


class LoginV1(Resource):
    def __init__(self):
        home = os.environ['HOME']
        try:
            self.conn = sqlite3.connect(os.path.join(home, 'test.db'))
            self.cur = self.conn.cursor()
        except:
            print('Connect to sqlite db Fail!')
            exit(0)

    def __init_db(self):
        home = os.environ['HOME']
        try:
            os.remove(os.path.join(home, 'test.db'))
            self.conn = sqlite3.connect(os.path.join(home, 'test.db'))
            self.cur = self.conn.cursor()
            print('Init sqlite3 database')
            self.__createDB()
        except:
            print('Init sqlite db Fail')
            exit(0)

    def __createDB(self):
        try:
            # db: sqlite3
            self.cur.execute(
                'CREATE TABLE USER (ID INTEGER PRIMARY KEY AUTOINCREMENT ,NAME TEXT NOT NULL,PASSWORD TEXT NOT NULL);'
            )
        except Exception as e:
            print(e)
        self.conn.commit()
        # password:helloworld
        insert_sql1 = "INSERT INTO USER(NAME,PASSWORD) VALUES('admin','/F4DjTilcDIIVEHn/nAQsA==')"  # helloworld
        # password:1234567
        insert_sql2 = "INSERT INTO USER(NAME,PASSWORD) VALUES('root','/OqSD3QStdp74M9CuMk3WQ==')"  # 1234567

        self.cur.execute(insert_sql1)
        self.cur.execute(insert_sql2)
        self.conn.commit()

    # def __del__(self):
    #     if self.cur:
    #         self.cur.close()
    #     if self.conn:
    #         self.conn.close()

    def _get_user_passwd(self, user):
        try:
            # sql injectable
            sql = "SELECT PASSWORD FROM USER WHERE NAME='{}'".format(user)
            self.cur.execute(sql)

            # immutable queries
            # mysql success
            # self.cur.execute("SELECT PASSWORD FROM USER WHERE NAME=%s",(user,))
            # sqlite ok mysql fail
            # self.cur.execute("SELECT PASSWORD FROM USER WHERE NAME=:1",[user])
            # self.cur.execute("SELECT PASSWORD FROM USER WHERE NAME=:xx",{'xx':user})
        except Exception as e:
            print(e)
            return "ERROR"
        res = self.cur.fetchone()
        # print(type(res))
        if isinstance(res, tuple) and len(res) > 0:
            return res[0]
        else:
            return None

    def processRequest(self):
        response = dict()
        response['code'] = 1
        response['msg'] = 'ok'
        response['token'] = ''
        data = parser.parse_args()
        print(data)
        if data['password'] is None:
            response['code'] = 0
            response['msg'] = 'password is empty'
            return json.dumps(response)

        if data['user'] is None:
            response['code'] = 0
            response['msg'] = 'user is empty'
            return json.dumps(response)

        md5 = hashlib.md5()
        md5.update(data['password'].encode())
        passwd = self._get_user_passwd(data['user'])

        if passwd is None:
            response['code'] = 0
            response['msg'] = 'user is NOT exits'
            return json.dumps(response)

        if passwd == 'ERROR':
            response['code'] = 0
            response['msg'] = 'invalidate sql'
            return json.dumps(response)

        if passwd.encode() == base64.b64encode(md5.digest()):
            response['code'] = 1
            response['msg'] = 'user login success'
            t = sys_token()
            print(data['Host'], data['user'])
            response['token'] = str(t.generate_login_token(data['user']))
        else:
            response['code'] = 0
            response['msg'] = 'user password is NOT corrcet'

        return json.dumps(response)

    def get(self):
        print('Method: GET')
        data = parser.parse_args()
        if data['init'] == '1':
            self.__init_db()
        else:
            with open('login2.html', 'r') as fp:
                buf = fp.readlines()
                return buf
        return 'Done'

    def put(self):
        pass

    def post(self):
        print('Method: POST')
        return self.processRequest()

    def delete(self):
        pass


class LoginV2(LoginV1):
    # mysql
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='192.168.99.121',
            user='sqltest',
            password='123456',
            database='sqltest')
        try:
            self.cur = self.conn.cursor()
        except:
            print('Connect MariaDB database Fail!')

    def __init_db(self):
        self.conn = mysql.connector.connect(
            host='192.168.99.121',
            user='sqltest',
            password='123456',
            database='sqltest')
        self.cur = self.conn.cursor()
        print('Init MariaDB database!')
        self.__createDB()

    def __createDB(self):
        try:
            print("DROP TABLE USER;")
            self.cur.execute("DROP TABLE USER;")
        except Exception as e:
            print(e)
        try:
            # db: mysql
            print(
                'CREATE TABLE USER (ID INT PRIMARY KEY AUTO_INCREMENT ,NAME VARCHAR(32) NOT NULL,PASSWORD VARCHAR(32) NOT NULL);'
            )
            self.cur.execute(
                'CREATE TABLE USER (ID INT PRIMARY KEY AUTO_INCREMENT ,NAME VARCHAR(32) NOT NULL,PASSWORD VARCHAR(32) NOT NULL);'
            )
        except Exception as e:
            print(e)
        self.conn.commit()
        # password:helloworld
        insert_sql1 = "INSERT INTO USER(NAME,PASSWORD) VALUES('admin','/F4DjTilcDIIVEHn/nAQsA==');"
        # password:1234567
        insert_sql2 = "INSERT INTO USER(NAME,PASSWORD) VALUES('root','/OqSD3QStdp74M9CuMk3WQ==');"

        self.cur.execute(insert_sql1)
        self.cur.execute(insert_sql2)
        self.conn.commit()


class LoginV3(LoginV2):
    def _get_user_passwd(self, user):
        try:
            # sql injectable
            # sql = "SELECT PASSWORD FROM USER WHERE NAME='{}'".format(user)
            # self.cur.execute(sql)

            # immutable queries
            # mysql success
            self.cur.execute("SELECT PASSWORD FROM USER WHERE NAME=%s",
                             (user,))
            # sqlite ok mysql fail
            # self.cur.execute("SELECT PASSWORD FROM USER WHERE NAME=:1",[user])
            # self.cur.execute("SELECT PASSWORD FROM USER WHERE NAME=:xx",{'xx':user})
        except Exception as e:
            print(e)
            return "ERROR"
        res = self.cur.fetchone()
        # print(type(res))
        if isinstance(res, tuple) and len(res) > 0:
            return res[0]
        else:
            return None


api.add_resource(root, '/')
api.add_resource(LoginV1, '/v1/login')
api.add_resource(LoginV2, '/v2/login')
api.add_resource(LoginV3, '/v3/login')
api.add_resource(edit_info, '/v1/edit')
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
