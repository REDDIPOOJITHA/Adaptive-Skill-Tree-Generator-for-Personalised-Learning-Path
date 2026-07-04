from django.shortcuts import render
from AdminApp import Database
from django.middleware.csrf import get_token
import matplotlib.pyplot as plt
import pandas as pd
import os
from django.db import connection
from django.conf import settings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import os
from django.conf import settings

# Create your views here.
def RegAction(request):
    n=request.POST['name']
    e=request.POST['email']
    m=request.POST['mobile']
    a=request.POST['address']
    u=request.POST['username']
    p=request.POST['password']

    con=Database.connection()
    cur=con.cursor()
    cur.execute("select * from student where email='"+e+"' or mobile='"+m+"'")
    data=cur.fetchone()
    if data is not None:
        context={'msg':'EmailId or Mobile Number Already Exist..!!'}
        return render(request,'index.html', context)
    else:
        cur1=con.cursor()
        cur1.execute("insert into student values(null,'"+n+"','"+e+"','"+m+"','"+a+"','"+u+"','"+p+"')")
        con.commit()
        context={'msg':'Registration Successfully Completed..!!'}
        return render(request,'index.html', context)

def UserLogAction(request):
    u=request.POST['username']
    p=request.POST['password']

    con=Database.connection()
    cur=con.cursor()
    cur.execute("select * from student where username='"+u+"' and password='"+p+"'")
    data=cur.fetchone()
    if data is not None:
        request.session['id']=data[0]
        request.session['email']=data[2]

        cur.execute("delete from result")
        con.commit()
        return render(request,'StudentApp/Home.html')
    else:
        context={'msg':'login Failed Please Check Username and Password..!!'}
        return render(request,'index.html', context)

def home(request):
    return render(request,'StudentApp/Home.html')

def viewprofile(request):
    id=str(request.session['id'])
    email=request.session['email']


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
    cur.execute("select * from student where id='"+id+"'")
    data=cur.fetchall()
    for d in data:
        strdata += "<tbody><tr><td>"+str(d[1])+"</td><td>"+str(d[2])+"</td>" \
                                     "<td>"+str(d[3])+"</td><td>"+str(d[4])+"</td><td>"+str(d[5])+"</td>" \
                                      "</tr></tbody>"
    strdata+="</table>"

    context={'data':strdata}
    return render(request,'StudentApp/ViewProfile.html', context)

def gotoquiz(request):
    strdata=""

    df = pd.read_csv('Dataset/Quize.csv')

    for i in df['subject'].unique():
        strdata+="<option>"+str(i)+"</option>"
    strdata+=""

    context={'option':strdata}
    return render(request,'StudentApp/ViewSubject.html',context)


def MyTableData(request,subject):
    u_id = str(request.session['id'])

    con = Database.connection()
    cur_perf = con.cursor()
    cur_perf.execute("""
        SELECT 
            SUM(CASE WHEN ans_status='valid' THEN 1 ELSE 0 END) AS correct,
            COUNT(*) AS total
        FROM result
        WHERE u_id=%s AND subject=%s
    """, (u_id, subject))

    perf_data = cur_perf.fetchone()
    correct = perf_data[0] if perf_data[0] else 0
    total = perf_data[1] if perf_data[1] else 0
    accuracy = (correct / total) * 100 if total > 0 else 0



    # Decide difficulty
    if accuracy >= 80:
        difficulty = 'hard'
    elif accuracy >= 50:
        difficulty = 'average'
    else:
        difficulty = 'easy'

    print(difficulty)
    strdata = "<table class='table'><thead  class='thead-dark'>" \
            "<tr>" \
            "<th scope='col' style='width:300px;'  colspace='4'>Subject: "+subject+"</th>" \
            "<th scope='col'></th>" \
            "<th scope='col' style='color:gold';>Skill Performance is "+ str(accuracy)+"% </th>" \
            "<th scope='col' style='color:gold';>Recommended Question type is: "+difficulty+"</th>" \
            "</tr></thead>"
    # Fetch questions based on difficulty
    cur = con.cursor()
    cur.execute("SELECT * FROM qa WHERE subject=%s AND Q_type=%s", (subject, difficulty))
    data=cur.fetchall()
    csrf_token = get_token(request)
    strdata+="<form action='/user/QizeAction' method='post' id='quizform'>"
    a=0
    for d in data:
        a+=1
        strdata += "<table><tbody>" \
                   "<tr><th scope='col'></th>" \
                    "<th><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf_token + "'></th></tr>" \
                    "<tr><td><b>" + str(a) + " .<input type='hidden' name='qid' value='" + str(d[0]) + "'>" + str(d[2]) + "</b></th></tr> " \
                    "<tr><td><input type='radio' name='answer_" + str(d[0]) + "' value='A'> " + str(d[3]) + "</td></tr>" \
                    "<tr><td><input type='radio' name='answer_" + str(d[0]) + "' value='B'> " + str(d[4]) + "</td></tr>" \
                     "<tr><td><input type='radio' name='answer_" + str(d[0]) + "' value='C'> " + str(d[5]) + "</td></tr>" \
                     "</tbody><hr></table>"

    strdata+="<td><input type='submit' value='submit'  style='color:white;background:orange;'></td></tr>"
    strdata+="<hr><tr><th><a href='/user/ViewResult?subject="+subject+"'><input type='button' value='VIEW RESULT' style='color:white;background:navy;'></a></th></tr></table>"
    return strdata


def SubAction(request):
    sub=request.POST['subject']

    request.session['subject']=sub



    strdata=MyTableData(request,sub)
    context={'data':strdata}
    return render(request,'StudentApp/StartQuiz.html', context)


def QizeAction(request):
    if request.method == "POST":
        subject = request.session.get('subject', '')

        # Get all question IDs and answers submitted
        qid_list = request.POST.getlist('qid')
        submitted_answers = {}

        for key, value in request.POST.items():
            if key.startswith("answer_"):
                qid = key.split("_")[1]  # Extract question ID
                submitted_answers[qid] = value

        if not submitted_answers:
            return render(request, 'StudentApp/Home.html',{'output': "No answers were submitted."})

        con = Database.connection()
        try:
            with con.cursor() as cursor:
                # Check for already answered questions
                cursor.execute("SELECT q_id FROM result WHERE q_id IN %s", [tuple(submitted_answers.keys())])
                already_answered = {str(row[0]) for row in cursor.fetchall()}

                if already_answered:
                    return render(request, 'StudentApp/StartQuiz.html', {
                        'data': MyTableData(request, subject),
                        'msg': "You have already answered some questions."
                    })

                # Fetch correct answers for submitted questions
                cursor.execute("SELECT id, c_ans FROM qa WHERE id IN %s", [tuple(submitted_answers.keys())])
                correct_answers = {str(row[0]): row[1] for row in cursor.fetchall()}

                results_to_insert = []

                for qid, answer in submitted_answers.items():
                    status = 'valid' if correct_answers.get(qid) == answer else 'invalid'
                    id = str(request.session['id'])
                    results_to_insert.append((qid,id, subject, status))

                # Bulk insert answers into the result table
                if results_to_insert:
                    cursor.executemany("INSERT INTO result (q_id,u_id, subject, ans_status) VALUES (%s, %s, %s, %s)",
                                       results_to_insert)
                    con.commit()  # Commit changes

        finally:
            con.close()  # Close DB connection

        return render(request, 'StudentApp/StartQuiz.html', {
            'data': MyTableData(request, subject),
            'msg': "Your answers have been submitted successfully."
        })
        #return render(request,'StudentApp/StartQuiz.html', context)

def ViewResult(request):
    subject=request.GET['subject']



    strdata = "<table class='table'><thead  class='thead-dark'>" \
            "<tr>" \
            "<th scope='col' colspan=3>subject: "+subject+"</th>" \
            "<th scope='col'></th>" \
            "<th scope='col'></th>" \
            "</tr>" \
              "<tr>" \
            "<th scope='col' colspan='1'>TOTAL QUESTIONS ATTEMPTED</th>" \
            "<th scope='col'></th>" \
            "<th scope='col' colspan='1'>CORRECT ANSWERS</th>" \
            "<th scope='col'></th>" \
            "<th scope='col'>WRONG ANSWERS</th>" \
            "</tr></thead>"
    con=Database.connection()
    cur1=con.cursor()
    cur1.execute("select count(*) from result where subject='"+subject+"'")
    data1=cur1.fetchone()
    total_qa=data1[0]
    cur2=con.cursor()
    cur2.execute("select count(ans_status) from result where subject='"+subject+"'and ans_status='valid'")
    data2=cur2.fetchone()
    print(data2[0])
    cur3=con.cursor()
    cur3.execute("select count(ans_status) from result where subject='"+subject+"' and ans_status='invalid'")
    data3=cur3.fetchone()
    print(data3[0])

    strdata += "<tbody><tr><td>"+str(total_qa)+"</td><td></td>" \
                                     "<td>"+str(data2[0])+"</td><td></td><td>"+str(data3[0])+"</td>" \
                                      "</tr></tbody>"
    strdata+="</table>"

    context={'data':strdata}
    return render(request,'StudentApp/ViewResult.html', context)

def TimeUp(request):
    return render(request,'StudentApp/TimeUp.html')

def back(request):
    con=Database.connection()
    cur1=con.cursor()
    cur1.execute("delete from result")
    con.commit()
    return render(request,'StudentApp/Home.html')


def generate_result_graph(id):

    con = Database.connection()

    query = "SELECT subject, ans_status FROM result WHERE u_id = %s"
    df = pd.read_sql(query, con, params=[id])

    if df.empty:
        return None

    grouped = df.groupby('subject').agg(
        attempted=('ans_status', 'count'),
        valid=('ans_status', lambda x: (x == 'valid').sum()),
        invalid=('ans_status', lambda x: (x == 'invalid').sum())
    ).reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    bar_width = 0.25

    r1 = range(len(grouped))
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]

    ax.bar(r1, grouped['attempted'], width=bar_width, label='Attempted')
    ax.bar(r2, grouped['valid'], width=bar_width, label='Valid')
    ax.bar(r3, grouped['invalid'], width=bar_width, label='Invalid')

    ax.set_xlabel('Subject')
    ax.set_ylabel('Count')
    ax.set_title('Skill Performance by Subject')
    ax.set_xticks([r + bar_width for r in r1])
    ax.set_xticklabels(grouped['subject'], rotation=30)

    ax.legend()
    plt.tight_layout()

    filename = f"result_graph_{id}.png"
    save_path = os.path.join(settings.BASE_DIR, 'static', filename)

    plt.savefig(save_path)
    plt.close()

    return filename

def skillassessment(request):
    id = request.session['id']
    con = Database.connection()
    cur = con.cursor()
    cur.execute("select count(*) from result where u_id='"+str(id)+"'")
    d= cur.fetchone()
    print(d[0])
    if d[0] !=0:
        graph_file = generate_result_graph(id)
        return render(request, 'StudentApp/ViewGraph.html', {'graph_file': graph_file})
    else:
        return render(request, 'StudentApp/ViewGraph.html')



def skill_tree_view(request):
    u_id = str(request.session['id'])
    con = Database.connection()

    # 1️⃣ Get performance per subject
    cur_perf = con.cursor()
    cur_perf.execute("""
        SELECT subject,
               SUM(CASE WHEN ans_status='valid' THEN 1 ELSE 0 END) AS correct,
               COUNT(*) AS total
        FROM result
        WHERE u_id=%s
        GROUP BY subject
    """, (u_id,))
    subject_perf = cur_perf.fetchall()

    # Create performance dictionary
    performance_dict = {}
    for subject, correct, total in subject_perf:
        accuracy = (correct / total) * 100 if total > 0 else 0
        performance_dict[subject.lower()] = accuracy

    # 2️⃣ Get career roles and skills
    cur_role = con.cursor()
    cur_role.execute("SELECT c_role, key_skills FROM career_skills")
    roles = cur_role.fetchall()

    # ✅ Helper: hierarchy layout
    def hierarchy_pos(G, root=None, width=1., vert_gap=0.3, vert_loc=0, xcenter=0.5):
        if root is None:
            root = list(G.nodes)[0]

        def _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter, pos=None, parent=None):
            if pos is None:
                pos = {root: (xcenter, vert_loc)}
            else:
                pos[root] = (xcenter, vert_loc)
            children = list(G.successors(root))
            if len(children) != 0:
                dx = width / len(children)
                nextx = xcenter - width/2 - dx/2
                for child in children:
                    nextx += dx
                    pos = _hierarchy_pos(G, child, dx, vert_gap, vert_loc-vert_gap, nextx, pos, root)
            return pos

        return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

    # 3️⃣ Generate subplot per role
    n_roles = len(roles)
    cols = 2
    rows = (n_roles + 1) // cols

    plt.figure(figsize=(14, rows * 5))

    for i, (role, skills) in enumerate(roles, start=1):
        G = nx.DiGraph()
        G.add_node(role, color='lightblue', size=2500)

        for skill in skills.split(','):
            skill = skill.strip()
            perf = performance_dict.get(skill.lower(), None)
            label = f"{skill} ({perf:.0f}%)" if perf is not None else skill
            color = 'lightgreen' if perf is not None and perf >= 60 else 'salmon' if perf is not None else 'lightgray'
            G.add_node(label, color=color, size=2000)
            G.add_edge(role, label)

        colors = [G.nodes[n]['color'] for n in G.nodes]
        sizes = [G.nodes[n]['size'] for n in G.nodes]
        pos = hierarchy_pos(G, root=role)

        plt.subplot(rows, cols, i)
        nx.draw(G, pos, with_labels=True,
                node_color=colors,
                node_size=sizes,
                font_size=8, font_weight='bold',
                arrows=False)
        plt.title(role, fontsize=12)

    plt.suptitle("Skill Trees Based on Performance", fontsize=16)

    static_path = os.path.join(settings.BASE_DIR, 'static', 'skilltree.png')
    plt.savefig(static_path, format='png', bbox_inches="tight")
    plt.close()

    return render(request, 'StudentApp/ViewSkillTree.html')

def guidance(request):

    strdata = "<table class='table'><thead  class='thead-dark'>" \
              "<tr>" \
              "<th scope='col'>Booming Technology</th>" \
              "<th scope='col'>Refer Websites</th>" \
              "</tr></thead>"
    con = Database.connection()
    cur = con.cursor()
    cur.execute("select * from b_techno")
    data = cur.fetchall()
    for d in data:
        websites = str(d[2]).split(",")  # split by comma
        links = ""
        for site in websites:
            site = site.strip()  # remove spaces
            links += f"<a href='{site}' target='_blank'>{site}</a><br>"  # add <br> for line break

        strdata += f"<tbody><tr><td>{d[1]}</td><td>{links}</td></tr></tbody>"

    strdata += "</table>"

    context = {'data': strdata}
    return render(request, 'StudentApp/ViewGuidance.html', context)