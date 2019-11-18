import json

from flask_restful import Resource, reqparse

from utils.sys_token import sys_token


class edit_info(Resource):
    def __init__(self):
        self.parse = reqparse.RequestParser()
        self.parse.add_argument('user')
        self.parse.add_argument('user_token')
        self.parse.add_argument('csrf_token')
        self.parse.add_argument('first')
        self.parse.add_argument('last')
        self.parse.add_argument('salary')

    def get(self):
        s = sys_token()
        data = self.parse.parse_args()
        response = dict()
        response['csrf'] = 'None'
        print(data['user_token'], data['user'])
        ret = s.check_login_token(data['user_token'], data['user'])
        print("get", ret)
        if ret == 0:
            response['csrf'] = s.generate_csrf_token(data['user'])
        return json.dumps(response)
        # return render_template('edit.html',user_token=data['user_token'],csrf_token=response["csrf"],user=data["user"])

    def post(self):
        data = self.parse.parse_args()
        print(data)
        s = sys_token()
        response = dict()
        if s.check_login_token(data['user_token'], data['user']) == 0:
            if s.check_csrf_token(data['csrf_token'], data['user']) == 0:
                response['code'] = 1
                response['message'] = 'update personal info successful'
            else:
                response['code'] = 0
                response['message'] = 'CSRF attack!'
        else:
            response['code'] = 0
            response['message'] = 'You have No right to edit info'
        return json.dumps(response)
