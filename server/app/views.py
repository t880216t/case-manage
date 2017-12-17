# -*-coding:utf-8-*-
from app import app
import MySQLdb
from flask import request, jsonify
from flask import make_response
from database_config import *

@app.route('/')
@app.route('/index')
def index():
    return "Hello , Flask!"

# 狗日的跨域
def cors_response(res):
    response = make_response(jsonify(res))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

# 转型数字
import sys
def LongToInt(value):
    assert isinstance(value, (int, long))
    return int(value & sys.maxint)

# 简单的错误处理
class loginError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# 加密存储密码
import os
import hashlib

def encrypt_password(password, salt=None, encryptlop=30):
    if not salt:
        salt = os.urandom(16).encode('hex')  # length 32
    for i in range(encryptlop):
        password = hashlib.sha256(password + salt).hexdigest()  # length 64
    return password, salt


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        response = cors_response({'code': 10001, 'msg': '插入失败'})
        return response
    if request.method == 'POST':
        # 这里最好需要验证用户输入
        # 获取上传参数
        username = request.values.get("username")
        password = request.values.get("password")
        email = request.values.get("email")

        # 入库
        db = MySQLdb.connect(database_host,database_username,database_password,database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')

        hash_password, salt = encrypt_password(password)
        dbc.execute('INSERT INTO users (username,hash_password,salt,email) VALUES (%s,%s,%s,%s)',
                    (username, hash_password, salt, email))
        db.commit()
        response = cors_response({'code': 0, 'msg': '注册成功'})
        dbc.close()
        db.close()
        return response


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        response = cors_response({'code': 10001, 'msg': '插入失败'})
        return response
    if request.method == 'POST':
        # 这里最好需要验证用户输入
        # 获取上传参数
        username = request.values.get("username")
        password = request.values.get("password")

        # 入库
        db = MySQLdb.connect(database_host,database_username,database_password,database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')

        try:
            dbc.execute('SELECT `username` FROM users WHERE username = %s', (username,))
            if not dbc.fetchone():
                raise loginError(u'错误的用户名或者密码!')
            dbc.execute('SELECT `id`,`salt`,`hash_password` FROM users WHERE username = %s', (username,))
            id,salt, hash_password = dbc.fetchone()
            if encrypt_password(password, salt)[0] == hash_password:

                response = make_response(jsonify({'code': 0, 'msg': '登录成功','userID':id,'userName':username}))
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'POST'
                response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
                response.set_cookie('userName', username)
                dbc.close()
                db.close()
                return response
            else:
                raise loginError('错误的用户名或者密码!')
        except loginError as e:
            dbc.close()
            db.close()
            response = cors_response({'code': 10001, 'msg': e.value})
            return response



@app.route('/signout', methods=['POST'])
def signout():
    response = make_response(jsonify({'code': 0, 'msg': '登出成功'}))
    response.set_cookie('username', '')
    return response
