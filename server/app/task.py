# -*- coding:utf-8 -*-
import MySQLdb
import os
import time
import sys
import xlrd
from flask import make_response
from flask import render_template, flash, redirect, jsonify, Response
from app import app
from threading import Thread
from flask import request
from bs4 import BeautifulSoup
from app.database_config import *

# 狗跨域
def cors_response(res):
    response = make_response(jsonify(res))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

def LongToInt(value):
    assert isinstance(value, (int, long))
    return int(value & sys.maxint)

@app.route('/gettaskdetail', methods=['GET', 'POST'])
def get_task_detail():
    if request.values.get("userID"):
        userID = request.values.get("userID")
    else:
        userID = 0
    entry = request.values.get("entry")
    # 连接
    db = MySQLdb.connect(database_host,database_username,database_password,database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select distinct project_id from case_list where entry = %s'
    dbc.execute(sql,(entry,))
    project_ids = dbc.fetchall()
    if len(project_ids) == 0:
        dbc.close()
        db.close()
        response = cors_response({"code": 10001, "msg": "还没有任务"})
        return response
    relnewResult = []
    for project_id in project_ids:
        sql = 'select * from case_list where project_id = %s'
        #mysqldb版本兼容
        try:
            dbc.execute(sql, (project_id))
        except:
            dbc.execute(sql, (project_id,))
        sz = dbc.fetchall()
        order_user = sz[0][3]
        totalCount = LongToInt(dbc.execute('select * from case_list where project_id = %s AND id > 1' % project_id))
        doneCount = LongToInt(dbc.execute('select * from case_list where project_id = %s AND status = 1' % project_id))
        failedCount = LongToInt(dbc.execute('select * from case_list where project_id = %s AND status = 2' % project_id))
        def getchild(pid):
            result = []
            for obj in sz:
                if obj[2] == pid:
                    result.append({
                        "id": obj[0],
                        "title": obj[1].replace('$',''),
                        "pid": obj[2],
                        "entry": obj[7],
                        "status": obj[5],
                        "updateUser": obj[8],
                        "updateTime": obj[9],
                        "children": getchild(obj[0]),
                    })
            return result
        newResult = getchild(0)
        for item in range(1, len(newResult)):
            newResult[0]["children"].append(newResult[item])
        for item in range(1,len(newResult)):
            newResult.pop()
        newResult[0]['totalCount']=totalCount
        newResult[0]['doneCount']=doneCount
        newResult[0]['failedCount']=failedCount
        newResult[0]['order_user']=order_user
        relnewResult.append(newResult[0])
    _result = {
        "code": 0,
        "content": relnewResult
    }
    response = cors_response(_result)
    dbc.close()
    db.close()
    return response

@app.route('/gettasklist', methods=['GET', 'POST'])
def get_task_list():
    if request.values.get("userID"):
        userID = request.values.get("userID")
    else:
        userID = 0

    # 连接
    db = MySQLdb.connect(database_host,database_username,database_password,database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select distinct project_id from case_list where user_id = %s or user_id = 0'
    dbc.execute(sql,(userID,))
    project_ids = dbc.fetchall()
    if len(project_ids) == 0:
        dbc.close()
        db.close()
        response = cors_response({"code": 10001, "msg": "还没有任务"})
        return response
    relnewResult = []
    for project_id in project_ids:
        sql = 'select * from case_list where project_id = %s and id = 1'
        #mysqldb版本兼容
        try:
            dbc.execute(sql, (project_id))
        except:
            dbc.execute(sql, (project_id,))
        sz = dbc.fetchall()
        order_user = sz[0][3]
        totalCount = LongToInt(dbc.execute('select * from case_list where project_id = %s AND id > 1' % project_id))
        doneCount = LongToInt(dbc.execute('select * from case_list where project_id = %s AND status = 1' % project_id))
        failedCount = LongToInt(dbc.execute('select * from case_list where project_id = %s AND status = 2' % project_id))
        def getchild(pid):
            result = []
            for obj in sz:
                if obj[2] == pid:
                    result.append({
                        "id": obj[0],
                        "title": obj[1].replace('$',''),
                        "pid": obj[2],
                        "entry": obj[7],
                        "status": obj[5],
                    })
            return result
        newResult = getchild(0)
        for item in range(1, len(newResult)):
            newResult[0]["children"].append(newResult[item])
        for item in range(1,len(newResult)):
            newResult.pop()
        newResult[0]['totalCount']=totalCount
        newResult[0]['doneCount']=doneCount
        newResult[0]['failedCount']=failedCount
        newResult[0]['order_user']=order_user
        relnewResult.append(newResult[0])
    _result = {
        "code": 0,
        "content": relnewResult
    }
    response = cors_response(_result)
    dbc.close()
    db.close()
    return response

@app.route('/addcase', methods=['GET', 'POST'])
def addcase():
    entry = request.values.get("entry")
    title = request.values.get("newCase")
    # 连接
    db = MySQLdb.connect(database_host,database_username,database_password,database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    need_value_sql = 'select * from case_list WHERE entry = %s' % entry
    dbc.execute(need_value_sql)
    list = dbc.fetchone()
    pid = list[0]
    user_id = list[3]
    project_id = list[6]
    id_sql = "select max(id) from case_list where case_list.project_id = %s"
    dbc.execute(id_sql,(project_id,))
    ids = dbc.fetchone()
    id = ids[0]+1

    sql = 'insert into case_list (id,title,pid,user_id,status,project_id) VALUES (%s,%s,%s,%s,%s,%s)'
    state = dbc.execute(sql, (id,title,pid,user_id,0,project_id))
    if state:
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '新建成功'})
        return response
    else:
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 10001, 'msg': '新建失败'})
        return response

from werkzeug.utils import secure_filename
import os

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload():
    upload_file = request.files["file"]
    userID = request.values.get("userID")
    if upload_file:
        if allowed_file(upload_file.filename):
            # 连接
            db = MySQLdb.connect(database_host,database_username,database_password,database1)
            dbc = db.cursor()
            # 编码问题
            db.set_character_set('utf8')
            dbc.execute('SET NAMES utf8;')
            dbc.execute('SET CHARACTER SET utf8;')
            dbc.execute('SET character_set_connection=utf8;')

            projectID = int(round(time.time() * 1000))
            filename = secure_filename(upload_file.filename)
            #保存文件
            upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            if "html" in filename:
                try:
                    #读取文件信息
                    file = open('app/static/uploads/'+filename).read()
                    soup = BeautifulSoup(file)
                    allData = []
                    count = 1
                    for k in soup.find_all('a'):
                        value = k.text.replace(u'\xa0', u'$')
                        allData.append([count, value])
                        count += 1
                    sz = []
                    allData[0].append(0)
                    allData[1].append(0)
                    sz.append(allData[0])
                    sz.append(allData[1])
                    #理出父子关系
                    for i in range(len(allData)):
                        if i > 1:
                            prew_index = len(allData[i - 1][1]) - len(allData[i - 1][1].replace('$', ''))
                            now_index = len(allData[i][1]) - len(allData[i][1].replace('$', ''))
                            if now_index - prew_index == 1:
                                allData[i].append(allData[i - 1][0])
                            elif now_index - prew_index == 0:
                                try:
                                    allData[i].append(allData[i - 1][2])
                                except:
                                    print allData[i - 1]
                            elif now_index - prew_index < 0:
                                for l in range(0, len(sz)):
                                    # 找新数组
                                    _prew_index = len(sz[(len(sz) - 1) - l][1]) - len(sz[(len(sz) - 1) - l][1].replace('$', ''))
                                    if now_index - _prew_index == 0:
                                        allData[i].append(sz[(len(sz) - 1) - l][2])
                                        break
                            sz.append(allData[i])
                    for data in sz:
                        try:
                            sql = 'insert into case_list (id,title,pid,user_id,status,project_id) VALUES (%s,%s,%s,%s,%s,%s)'
                            dbc.execute(sql, (data[0],data[1].replace('$',''),data[2],userID,0,projectID))
                        except:
                            print (data[0])
                    db.commit()
                    dbc.close()
                    db.close()
                    response = cors_response({'code': 0, 'msg': '上传成功'})
                    return response
                except:
                    response = cors_response({'code': 10002, 'msg': '文件解析失败！只支持xmind导入出的纯html文件'})
                    return response
            if "xlsx" in filename:
                try:
                    def get_data(file_path):
                        """获取excel数据源"""
                        try:
                            data = xlrd.open_workbook(file_path)
                            return data
                        except Exception, e:
                            print u'excel表格读取失败：%s' % e
                            return None
                    file_path = 'app/static/uploads/'+filename
                    book = get_data(file_path)
                    # 抓取所有sheet页的名称
                    worksheets = book.sheet_names()
                    print "该Excel包含的表单列表为：\n"
                    for sheet in worksheets:
                        print ('%s,%s' % (worksheets.index(sheet), sheet))
                    # inp = raw_input(u'请输入表单名对应的编号，对应表单将自动转为json:\n')
                    # sheet = book.sheet_by_index(int(inp))
                    sheet = book.sheet_by_index(int(1))
                    row_0 = sheet.row(0)  # 第一行是表单标题
                    nrows = sheet.nrows  # 行号
                    ncols = sheet.ncols  # 列号

                    result = {}  # 定义json对象
                    result["title"] = file_path  # 表单标题
                    result["rows"] = nrows  # 行号
                    result["children"] = []  # 每一行作为数组的一项
                    # 遍历所有行，将excel转化为json对象
                    for i in range(nrows):
                        if i == 0:
                            continue
                        tmp = []
                        # 遍历当前行所有列
                        for j in range(1, ncols):
                            value = sheet.row_values(i)[j]
                            value = value.replace('\n', ' ')
                            tmp.append(value)
                        result["children"].append(tmp)

                    new_result = []
                    projects = []
                    for data in result["children"]:
                        project_data = []
                        project_data.append("1")
                        project_data.append(data[0])
                        project_data.append("0")
                        if project_data not in projects:
                            projects.append(project_data)
                    for i in range(len(projects)):
                        projectID = int(round(time.time() * 1000)) + i * 10
                        projects[i].append(projectID)

                    moduels = []
                    for data in result["children"]:
                        moduels_data = []
                        moduels_data.append(data[0])
                        moduels_data.append(data[1])
                        if moduels_data not in moduels:
                            moduels.append(moduels_data)
                    new_moduels = []
                    for project in projects:
                        for moduel_index in range(len(moduels)):
                            new_moduel_data = []
                            if project[1] == moduels[moduel_index][0]:
                                new_moduel_data.append(str(moduel_index + 2))
                                new_moduel_data.append(moduels[moduel_index][1])
                                new_moduel_data.append("1")
                                new_moduel_data.append(project[3])
                                new_moduels.append(new_moduel_data)

                    case_tiles = []
                    for data in result["children"]:
                        case_tiles_data = []
                        case_tiles_data.append(data[0])
                        case_tiles_data.append(data[1])
                        case_tiles_data.append(data[2])
                        if case_tiles_data not in case_tiles:
                            case_tiles.append(case_tiles_data)
                    new_case_tiles = []
                    for project in projects:
                        for moduels_data in new_moduels:
                            for case_tiles_index in range(len(case_tiles)):
                                new_case_data = []
                                if moduels_data[1] == case_tiles[case_tiles_index][1] and project[1] == \
                                        case_tiles[case_tiles_index][0]:
                                    new_case_data.append(str(len(new_case_tiles) + len(new_moduels) + 2))
                                    new_case_data.append(case_tiles[case_tiles_index][2])
                                    new_case_data.append(moduels_data[0])
                                    new_case_data.append(project[3])
                                    new_case_tiles.append(new_case_data)


                    case_points = []
                    for data in result["children"]:
                        case_points_data = []
                        case_points_data.append(data[0])
                        case_points_data.append(data[1])
                        case_points_data.append(data[2])
                        case_points_data.append(data[3])
                        if case_points_data not in case_points:
                            case_points.append(case_points_data)
                    new_case_points = []
                    for project in projects:
                        for moduels_data in new_moduels:
                            for case_data in new_case_tiles:
                                for case_points_index in range(len(case_points)):
                                    new_case_points_data = []
                                    if case_data[1] == case_points[case_points_index][2] and project[1] == \
                                            case_points[case_points_index][0] and moduels_data[1] == \
                                            case_points[case_points_index][1]:
                                        new_case_points_data.append(
                                            str(len(new_case_tiles) + len(new_moduels) + len(new_case_points) + 2))
                                        new_case_points_data.append(case_points[case_points_index][3])
                                        new_case_points_data.append(case_data[0])
                                        new_case_points_data.append(project[3])
                                        new_case_points.append(new_case_points_data)


                    case_details = []
                    for data in result["children"]:
                        case_details_data = []
                        case_details_data.append(data[0])
                        case_details_data.append(data[1])
                        case_details_data.append(data[2])
                        case_details_data.append(data[3])
                        case_details_data.append(data[4])
                        if case_details_data not in case_details:
                            case_details.append(case_details_data)
                    new_case_details = []
                    for project in projects:
                        for moduels_data in new_moduels:
                            for case_data in new_case_tiles:
                                for case_point_data in new_case_points:
                                    for case_details_index in range(len(case_details)):
                                        new_case_details_data = []
                                        if case_details[case_details_index][0] == project[1] and \
                                                case_details[case_details_index][1] == moduels_data[1] and \
                                                case_details[case_details_index][2] == case_data[1] and \
                                                case_details[case_details_index][3] == case_point_data[1]:
                                            new_case_details_data.append(str(
                                                len(new_case_tiles) + len(new_moduels) + len(new_case_points) + len(
                                                    new_case_details) + 2))
                                            new_case_details_data.append(case_details[case_details_index][4])
                                            new_case_details_data.append(case_point_data[0])
                                            new_case_details_data.append(project[3])
                                            new_case_details.append(new_case_details_data)

                    new_result = projects + new_moduels + new_case_tiles + new_case_points + new_case_details

                    for data in new_result:
                        try:
                            sql = 'insert into case_list (id,title,pid,user_id,status,project_id) VALUES (%s,%s,%s,%s,%s,%s)'
                            dbc.execute(sql, (data[0], data[1], data[2], userID, 0, data[3]))
                        except:
                            print (data)
                    detele_empty_sql = "delete from case_list where title =  ''"
                    dbc.execute(detele_empty_sql)
                    db.commit()
                    dbc.close()
                    db.close()
                    response = cors_response({'code': 0, 'msg': '上传成功'})
                    return response
                except:
                    response = cors_response({'code': 10002, 'msg': '文件解析失败！请检查表格格式是否正确'})
                    return response
        else:
            response = cors_response({'code': 10002, 'msg': '不支持的文件格式'})
            return response
    else:
        response = cors_response({'code': 10001, 'msg': '上传失败'})
        return response

@app.route('/settaskstatus', methods=['GET', 'POST'])
def settaskstatus():
    if request.values.get("entry"):
        entry = request.values.get("entry")
        status = request.values.get("status")
        updateUser = request.values.get("updateUser")
        updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if entry.isdigit() == False:
            response = cors_response({'code': 10002, 'msg': '呵呵呵呵呵呵呵呵'})
            return response
    else:
        response = cors_response({'code': 10002, 'msg': '未获取到行数据'})
        return response

    # 入库
    db = MySQLdb.connect(database_host,database_username,database_password,database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'update case_list set status = %s ,updateUser= %s , updateTime = %s where entry = %s'
    state = dbc.execute(sql,(status,updateUser,updateTime,entry))
    db.commit()
    need_value_sql = 'select * from case_list WHERE entry = %s' % entry
    dbc.execute(need_value_sql)
    list = dbc.fetchone()
    pid = list[2]
    project_id = list[6]
    if status == u'2':
        def updateFather(id):
            fasql = 'update case_list set status = 2  ,updateUser= %s , updateTime = %s where id = %s and project_id = %s'
            dbc.execute(fasql,(updateUser,updateTime,id,project_id))
            db.commit()
            se_fasql = 'select * from case_list where id = %s and project_id = %s'
            dbc.execute(se_fasql, (id, project_id))
            se_list = dbc.fetchone()
            if id != 0:
                if se_list[2] != 0:
                    updateFather(se_list[2])
        updateFather(pid)
    if status == u'1':
        def updateFather(id):
            son_fail_sql = 'select * from case_list where pid = %s and project_id = %s  and status = 2'
            dbc.execute(son_fail_sql, (id,project_id))
            son_fail_list = dbc.fetchall()
            son_new_sql = 'select * from case_list where pid = %s and project_id = %s  and status = 0'
            dbc.execute(son_new_sql, (id, project_id))
            son_new_list = dbc.fetchall()
            if len(son_fail_list) == 0 and len(son_new_list) == 0:
                fasql = 'update case_list set status = 1 ,updateUser= %s , updateTime = %s where id = %s and project_id = %s'
                dbc.execute(fasql,(updateUser,updateTime,id,project_id))
                db.commit()
                se_fasql = 'select * from case_list where id = %s and project_id = %s'
                dbc.execute(se_fasql, (id, project_id))
                se_list = dbc.fetchone()
                if id != 0:
                    if se_list[2] != 0:
                        updateFather(se_list[2])
            if len(son_fail_list) == 0 and len(son_new_list) > 0:
                fasql = 'update case_list set status = 0 ,updateUser= %s , updateTime = %s where id = %s and project_id = %s'
                dbc.execute(fasql, (updateUser,updateTime,id, project_id))
                db.commit()
                se_fasql = 'select * from case_list where id = %s and project_id = %s'
                dbc.execute(se_fasql, (id, project_id))
                se_list = dbc.fetchone()
                if id != 0:
                    if se_list[2] != 0:
                        updateFather(se_list[2])
        updateFather(pid)
    if state:
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '成功'})
        return response
    else:
        dbc.close()
        db.close()
        response = cors_response({'code': 10001, 'msg': '更新更新失败'})
        return response

@app.route('/deletecase', methods=['GET', 'POST'])
def deletecase():
    entry = request.values.get("entry")
    # 入库
    db = MySQLdb.connect(database_host,database_username,database_password,database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select * from case_list WHERE entry = %s' % entry
    dbc.execute(sql)
    list = dbc.fetchone()
    id = list[0]
    project_id = list[6]
    if id == 1:
        project_sql = 'delete from case_list where project_id = %s'
        state = dbc.execute(project_sql,(project_id,))
        db.commit()
    else:
        son_sql = 'select * from case_list where pid = %s and project_id = %s '
        dbc.execute(son_sql, (id, project_id))
        son_list = dbc.fetchall()
        if len(son_list) > 0:
            dbc.close()
            db.close()
            response = cors_response({'code': 10002, 'msg': '请先其删除子用例'})
            return response
        else:
            delete_son_sql = 'delete from case_list WHERE entry = %s' % entry
            state = dbc.execute(delete_son_sql)
            db.commit()
    if state:
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '删除成功'})
        return response
    else:
        dbc.close()
        db.close()
        response = cors_response({'code': 10001, 'msg': '删除失败'})
        return response

@app.route('/openproject', methods=['GET', 'POST'])
def openproject():
    entry = request.values.get("entry")
    userID = request.values.get("userID")
    # 入库
    db = MySQLdb.connect(database_host,database_username,database_password,database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select * from case_list WHERE entry = %s' % entry
    dbc.execute(sql)
    list = dbc.fetchone()
    project_id = list[6]
    update_sql = 'update case_list set user_id = 0 WHERE project_id = %s'
    state = dbc.execute(update_sql, (project_id,))
    db.commit()
    if state:
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '公开项目成功'})
        return response
    else:
        dbc.close()
        db.close()
        response = cors_response({'code': 10001, 'msg': '公开项目失败'})
        return response

@app.route('/initProjectStatus', methods=['GET', 'POST'])
def initProjectStatus():
    entry = request.values.get("entry")
    userID = request.values.get("userID")
    # 入库
    db = MySQLdb.connect(database_host,database_username,database_password,database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select * from case_list WHERE entry = %s' % entry
    dbc.execute(sql)
    list = dbc.fetchone()
    project_id = list[6]
    update_sql = 'update case_list set status = 0 , updateUser = "" , updateTime = "" WHERE project_id = %s'
    state = dbc.execute(update_sql, (project_id,))
    db.commit()
    if state:
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '重置项目状态成功'})
        return response
    else:
        dbc.close()
        db.close()
        response = cors_response({'code': 10001, 'msg': '重置项目状态失败'})
        return response
