#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
from sre_constants import IN
from flask import Flask, request
import MySQLdb

def cont_slot(slot):#'1-4' ==  [1, 2, 3, 4]
    start, end = map(int, slot.split('-'))
    cont_slot_result = list(range(start, end+1))
    return cont_slot_result

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    form = """
    <form method="post" action="/action" >
        輸入學號:<input name="my_head">
        <input type="submit" value="送出">
    </form>
    """
    return form


@app.route('/action', methods=['POST'])
def action():
    

    # 取得輸入的文字
    my_head = request.form.get("my_head")
    my_course = request.form.get("my_course")
    # 建立資料庫連線
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="course_registration")
    
    ###########確認學號存在
    results = """
    <p><a href="/">Back to Query Interface</a></p>
    """
    query = "SELECT student_name FROM `student` WHERE student_id='{}';".format(my_head)
    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)
    Sname=cursor.fetchall()
    try:
        print(Sname[0])
        results+=Sname[0][0]
    except:
        return results+"學號不存在"
    #########確認學號存在


    ###############已選課單A
    query = "SELECT * FROM course JOIN enrollments ON course.course_id = enrollments.course_id WHERE enrollments.student_id = '{}';".format(my_head)
    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)

  
    
    results += "<table border=\"1\">"
    results+="<th>已選課程</th>"
    results += "<tr>"
    results += "<th>課程代碼</th>"
    results += "<th>課程名稱</th>"
    results += "<th>開課系所</th>"
    results += "<th>必/選修</th>"
    results += "<th>年級</th>"
    results += "<th>學分數</th>"
    results += "<th>開課時段</th>"
    results += "<th>修課人數上限</th>"
    
    
    for t in cursor.fetchall():
        results += "<tr>"
        for i in t[:8]:
            results += "<td>{}</td>".format(i)

        results += "<form method='post' action='/delete'>"
        results += "<input type='hidden' name='student_id' value='{}'>".format(my_head)
        results += "<td><button type='submit' name='course_id' value='{}'>DELETE</button></td>".format(t[0])
        results += "</form>"

        results += "</tr>"
      
    ###############已選課單A


    ###################查詢可選課單B
    query = "SELECT course.Slot FROM course JOIN enrollments ON course.course_id = enrollments.course_id WHERE enrollments.student_id = '{}';".format(my_head)
    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)

    
    #cursor.fetchall()
    slected_list=[]
    # 取得並列出所有已選課單 的slot
    for (description, ) in cursor.fetchall():
        for t in cont_slot(description):
            slected_list.append(t)
            #results += "<p>{}</p>".format(t)
    
    query = "SELECT * FROM course; "
    # 執行查詢
    unslected_list=[]
    unslected_list_detail=[]
    unslected_temp=0
    cursor = conn.cursor()
    cursor.execute(query)
    for (cid,cname,department,grade,compulsory,ccredit,slot,limit,) in cursor.fetchall():
        unslected_list.append(cont_slot(slot))
        #所有課堂[(123),(34),(56)]裡有和已選課(1278)衝堂的課則不顯示
        unslected_list_detail.append([cid,cname,department,grade,compulsory,ccredit,slot,limit])

    ctemp=0
    final__list_detail=[]
    
    
    for c in unslected_list:
        flag=True
        #print(c,slected_list)

        for i in slected_list:
            if ((i in c) == True):
                #print(c,i)
                flag=False

        if flag :
            final__list_detail.append(unslected_list_detail[ctemp])
            #results += "<p>{}</p>".format(unslected_list_detail[ctemp])
        ctemp+=1
    print(final__list_detail)
    if (final__list_detail == []):
            results+="<th>無可選課程</th>"
    else:
        results+="<th>可選課程</th>"
        results += "<table border=\"1\">"
        results += "<tr>"
        results += "<th>課程代碼</th>"
        results += "<th>課程名稱</th>"
        results += "<th>開課系所</th>"
        results += "<th>必/選修</th>"
        results += "<th>年級</th>"
        results += "<th>學分數</th>"
        results += "<th>開課時段</th>"
        results += "<th>修課人數上限</th>"
        results += "<th>目前選修人數</th>"
        results += "</th>"


        for c in final__list_detail:
            
            query = "SELECT COUNT(*) AS enrollment_count FROM enrollments WHERE course_id = '{}';".format(c[0])# 執行查詢選課人數
            cursor = conn.cursor()
            cursor.execute(query)
            c.append(cursor.fetchall()[0][0])
            results += "<tr>"
            for i in c:
                results += "<td>{}</td>".format(i)
            results += "<form method='post' action='/register'>"
            results += "<input type='hidden' name='student_id' value='{}'>".format(my_head)
            results += "<td><button type='submit' name='course_id' value='{}'>Register</button></td>".format(c[0])
            results += "</form>"
            results += "</tr>"
            print(c)

    ###################查詢可選課單B

    
    
    
    
    return results
@app.route('/register', methods=['POST'])
def register():
    student_id = request.form.get("student_id")
    course_id = request.form.get("course_id")
    results =""
    results += "<form method='post' action='/action'>"
    results += "<td><button type='submit' name='my_head' value='{}'>back</button></td>".format(student_id)
    results += "</form>"
    results += "</tr>"
    try:
        # Call the stored procedure to register the course
        conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="course_registration")
        cursor = conn.cursor()
        cursor.callproc('register_course', (student_id, course_id))
        conn.commit()

        return results+"Registration successful"
    except MySQLdb.Error as e:
        results =""
        results += "<form method='post' action='/action'>"
        results += "<td><button type='submit' name='my_head' value='{}'>back</button></td>".format(student_id)
        results += "</form>"
        results += "</tr>"
        return results+"選課失敗"+"Error: {}".format(e)
    
@app.route('/delete', methods=['POST'])
def delete():
    student_id = request.form.get("student_id")
    course_id = request.form.get("course_id")
    results =""
    results += "<form method='post' action='/action'>"
    results += "<td><button type='submit' name='my_head' value='{}'>back</button></td>".format(student_id)
    results += "</form>"
    results += "</tr>"
    try:
        # Call the stored procedure to register the course
        conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="course_registration")
        cursor = conn.cursor()

        # Check if the student is enrolled in the course
        cursor = conn.cursor()
        cursor.callproc('delete_course', (student_id, course_id))
        conn.commit()

        return results+"DELETE successful"
    except MySQLdb.Error as e:
        return "Error: {}".format(e)