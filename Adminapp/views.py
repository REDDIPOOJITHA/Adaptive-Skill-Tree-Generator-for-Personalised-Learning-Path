from django.shortcuts import render
from AdminApp import Database
import pandas as pd

# Create your views here.
def index(request):
    return render(request,'index.html')
def ALogAction(request):
    username=request.POST['uname']
    password=request.POST['password']

    if username =='Admin' and password == 'Admin':
        return render(request,'AdminApp/AdminHome.html')
    else:
        context={'data':'Login Failed..!!'}
        return render(request,'index.html',context)
def home(request):
    return render(request,'AdminApp/AdminHome.html')

def addsubject(request):
    return render(request,'AdminApp/AddSubject.html')

def AddSubAction(request):
    subject=request.POST['sub_nane']

    con=Database.connection()
    cur=con.cursor()
    cur.execute("select * from subject where subject='"+subject+"'")
    data=cur.fetchone()
    if data is not None:
        context={'msg':'Subject Already Exist..!!'}
        return render(request,'AdminApp/AddSubject.html', context)
    else:
        cur1=con.cursor()
        cur1.execute("insert into subject values(null,'"+subject+"')")
        con.commit()
        context={'msg':'Subject Added Successfully..!!'}
        return render(request,'AdminApp/AddSubject.html', context)

# def AddQAnw(request):
#     strdata=""
#
#     con=Database.connection()
#     cur=con.cursor()
#     cur.execute("select * from subject")
#     data=cur.fetchall()
#     for i in data:
#         strdata+="<option>"+str(i[1])+"</option>"
#     strdata+=""
#
#     context={'option':strdata}
#     return render(request,'AdminApp/AddQuestions.html',context)

# def AddQAAction(request):
#     subject=request.POST['subject']
#     topic=request.POST['topic']
#     question=request.POST['question']
#     ans_one=request.POST['ans_one']
#     ans_two=request.POST['ans_two']
#     ans_three=request.POST['ans_three']
#     c_ans=request.POST['c_ans']
#     q_type=request.POST['q_type']
#
#     con=Database.connection()
#     cur=con.cursor()
#     cur.execute("select * from qa where subject='"+subject+"' and topic='"+topic+"' and question='"+question+"'")
#     data=cur.fetchone()
#     if data is not None:
#         strdata=""
#
#         con=Database.connection()
#         cur=con.cursor()
#         cur.execute("select * from subject")
#         data=cur.fetchall()
#         for i in data:
#             strdata+="<option>"+str(i[1])+"</option>"
#         strdata+=""
#
#         context={'option':strdata,'msg':'Question and Answers Already Exist..!!'}
#         return render(request,'AdminApp/AddQuestions.html', context)
#     else:
#         cur1=con.cursor()
#         cur1.execute("insert into qa values(null,'"+subject+"','"+topic+"','"+question+"','"+ans_one+"','"+ans_two+"','"+ans_three+"','"+c_ans+"','"+q_type+"')")
#         con.commit()
#         strdata=""
#
#         con=Database.connection()
#         cur=con.cursor()
#         cur.execute("select * from subject")
#         data=cur.fetchall()
#         for i in data:
#             strdata+="<option>"+str(i[1])+"</option>"
#         strdata+=""
#         context={'option':strdata,'msg':'Question and Answers Added Successfully..!!'}
#         return render(request,'AdminApp/AddQuestions.html', context)

def ViewQAnw(request):
    df = pd.read_csv('Dataset/Quize.csv')

    # Start table
    strdata = "<table id='example' class='table table-striped table-bordered'>"

    # Add header
    strdata += "<thead><tr>"
    for col in df.columns:
        strdata += f"<th>{col}</th>"
    strdata += "</tr></thead>"

    # Add rows

    for _, row in df.iterrows():  # iterate over rows
        strdata += "<tbody><tr>"
        for value in row:  # iterate over columns dynamically
            strdata += f"<td>{value}</td>"
        strdata += "</tr></tbody>"


    strdata += "</table>"

    context = {'data': strdata}
    return render(request, 'AdminApp/ViewQA.html', context)


def ViewStudents(request):
    strdata = "<table class='table'><thead  class='thead-dark'>" \
            "<tr>" \
            "<th scope='col'>NAME</th>" \
            "<th scope='col'>EMAIL</th>" \
            "<th scope='col'>MOBILE</th>" \
            "<th scope='col'>ADDRESS</th>" \
            "<th scope='col'>USERNAME</th>" \
            "</tr></thead>"
    con=Database.connection()
    cur=con.cursor()
    cur.execute("select * from student")
    data=cur.fetchall()
    for d in data:
        strdata += "<tbody><tr><td>"+str(d[1])+"</td><td>"+str(d[2])+"</td>" \
                                     "<td>"+str(d[3])+"</td><td>"+str(d[4])+"</td><td>"+str(d[5])+"</td>" \
                                      "</tr></tbody>"
    strdata+="</table>"

    context={'data':strdata}
    return render(request,'AdminApp/ViewStudents.html', context)

def AddCareerSkills(request):
    return render(request, 'AdminApp/AddCareerSkills.html')

def AddCareerAction(request):
    c_role = request.POST['c_role']
    skills = request.POST['skills']

    con = Database.connection()
    cur = con.cursor()
    cur.execute(
        "select * from career_skills where c_role='" + c_role+"'")
    data = cur.fetchone()
    if data is not None:
        context = {'option': strdata, 'msg': 'Career Skill Already Exist..!!'}
        return render(request, 'AdminApp/AddCareerSkills.html', context)
    else:
        cur1 = con.cursor()
        cur1.execute(
            "insert into career_skills values(null,'" + c_role + "','" + skills + "')")
        con.commit()

        context = {'msg': 'Career Skill Added Successfully..!!'}
        return render(request, 'AdminApp/AddCareerSkills.html', context)

def Addguidance(request):
    return render(request, 'AdminApp/AddCareerGuidance.html')

def AddCAction(request):
    c_role = request.POST['c_role']
    skills = request.POST['skills']

    con = Database.connection()
    cur = con.cursor()
    cur.execute(
        "select * from b_techno where b_tech='" + c_role + "'")
    data = cur.fetchone()
    if data is not None:
        context = {'option': strdata, 'msg': 'Details Already Exist..!!'}
        return render(request, 'AdminApp/AddCareerGuidance.html', context)
    else:
        cur1 = con.cursor()
        cur1.execute(
            "insert into b_techno values(null,'" + c_role + "','" + skills + "')")
        con.commit()

        context = {'msg': 'Career Guidance Successfully..!!'}
        return render(request, 'AdminApp/AddCareerGuidance.html', context)