import pymysql

def connection():
    con=pymysql.connect(host='localhost', user='root',password='root',database='skill_tree',charset='utf8')
    return con
