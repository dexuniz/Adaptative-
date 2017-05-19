from flask import Flask
from pylti.flask import lti
from flask import render_template, flash, redirect
import urllib


from flask import request
import MySQLdb
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,BooleanField
from wtforms.validators import Required
import numpy

from flask.ext.sqlalchemy import SQLAlchemy   #import sql module
import os

from get_exo import get_exo

#mysql:host=localhost;dbname=moodle31;charset=utf8', 'moodle', 'moodle'

app = Flask(__name__)

VERSION = '0.0.5'
app.config.from_object('config')

#configure the list sheet
app.config['SECRET_KEY'] = 'hard to guess string'
#configure the database
basedir = os.path.abspath(os.path.dirname(__file__))    #root path
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'database.sqlite')     #sql document name
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

# define the class of roles and Users
class Role(db.Model):
    __tablename__ = 'roles'     #define table name, if not it'll be defined by system
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')
    # connection, param: backref add a role attribute
    # db.relationship define which foreign key is connected
    # this is for the cas one-to-multiple, if we want to one-to-one connection we have to change the param:uselist turn to False
    def __repr__(self):
        return '<Role %r>' % self.name             #return a readable string


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    competance=db.Column(db.Integer)
    Stu_Comp_id=db.Column(db.Integer,db.ForeignKey('competance.id'),unique=True)
    # connection with the table named roles and db.ForeignKey return "id" in roles
    # role_id is defined for the foreign key
    def __repr__(self):
        return '<User %r>' % self.username

class Stu_Comp(db.Model):
    __tablename__='competance'
    id = db.Column(db.Integer, primary_key=True)
    def __repr__(self):
        return '<Stu_Com %r>' % self.id

db.create_all()
admin_role = Role(name='Admin')
teacher_role = Role(name='Teacher')
student_role = Role(name='Student')



class Form_doexo(Form):
    gotoexo = SubmitField('do exercises')

class Form_checkexo(Form):
    muticheck=BooleanField()
    submit=SubmitField('finish and submit')




def error(exception=None):
    """ Page d'erreur """
    return render_template('error.html')


@app.route('/is_up', methods=['GET'])
def hello_world(lti=lti):
    """ Test pour debug de l'application
    :param lti: the `lti` object from `pylti`
    :return: simple page that indicates the request was processed by the lti
        provider
    """
    return render_template('up.html', lti=lti)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/lti/', methods=['GET', 'POST'])
@lti(request='initial', error=error, app=app)
def index(lti=lti):
    """ Page d'acceuil, permet d'authentifier l'utilisateur.
    :param lti: the `lti` object from `pylti`
    :return: index page for lti provider
    """
    #print 1
    print "\
    hahaha"
    return render_template('index.html', lti=lti)


@app.route('/index_staff', methods=['GET', 'POST'])
@lti(request='session', error=error, role='staff', app=app)
def index_staff(lti=lti):
    """ render the contents of the staff.html template
    :param lti: the `lti` object from `pylti`
    :return: the staff.html template rendered
    """
    return render_template('staff.html', lti=lti)


@app.route('/teacher',methods=['GET','POST'])
@lti(request='session', error=error, app=app)
def teachers_class(lti=lti):
    user_id=lti.user_id
    print user_id
    myDB = MySQLdb.connect(host="127.0.0.1",port=8889,user="moodle",passwd="moodle",db="moodle31")
    cHandler=myDB.cursor()
    #cHandler.execute('SELECT user.firstname, user.lastname, user.email enrol.enrolid FROM mdl_user AS user WHERE mdl_user.id=%s',user_id)

    cHandler.execute('SELECT ue.enrolid, e.courseid, c.fullname, q.name, q.sumgrades, qa.sumgrades \
                      FROM mdl_user_enrolments AS ue \
                      JOIN mdl_enrol AS e ON e.id=ue.enrolid \
                      JOIN mdl_course AS c ON c.id=e.courseid \
                      JOIN mdl_quiz AS q ON q.course=e.courseid \
                      JOIN mdl_quiz_attempts AS qa ON qa.quiz=q.id \
                      WHERE ue.userid=%s',user_id)
    results = cHandler.fetchall()
    '''
    cHandler.execute('SELECT ue.enrolid FROM mdl_user_enrolments AS ue WHERE ue.userid=%s ', user_id)
    user_enrol_id=cHandler.fetchall()
    print user_enrol_id
    cHandler.execute('SELECT e.courseid FROM mdl_enrol AS e WHERE ')
    results=user_enrol_id
    '''
    return render_template('photo.html', results=results)


@app.route('/information',methods=['GET','POST'])
@lti(request='session', error=error, app=app)
def userinformation(lti=lti):

    form_doexo=Form_doexo()
    if form_doexo.validate_on_submit():
        print "button validate"


    user_id=lti.user_id
    print user_id
    myDB = MySQLdb.connect(host="127.0.0.1",port=8889,user="moodle",passwd="moodle",db="moodle31")
    cHandler=myDB.cursor()
    #cHandler.execute('SELECT user.firstname, user.lastname, user.email enrol.enrolid FROM mdl_user AS user WHERE mdl_user.id=%s',user_id)

    cHandler.execute('SELECT firstname, lastname ,email FROM mdl_user WHERE id=%s',user_id)
    userinfo=cHandler.fetchall()
    print userinfo[0][2]

    cHandler.execute('SELECT enrolid FROM mdl_user_enrolments WHERE userid=%s ',user_id)
    enrolinfo=cHandler.fetchall()
    courseinfo=[]
    for i in range(0,len(enrolinfo)):
        print enrolinfo[i]
        cHandler.execute('SELECT e.courseid, c.fullname FROM mdl_enrol AS e JOIN mdl_course AS c ON c.id=e.courseid WHERE e.id=%s',enrolinfo[i])
        temp=cHandler.fetchall()
        courseinfo.append(temp)
        print courseinfo[i]

    cHandler.execute('SELECT q.name, q.sumgrades, qa.sumgrades FROM mdl_quiz AS q JOIN mdl_quiz_attempts AS qa ON q.id=qa.quiz WHERE qa.userid=%s',user_id)
    quizinfo=cHandler.fetchall()
    print quizinfo

    '''
    cHandler.execute('SELECT ue.enrolid, e.courseid, c.fullname, q.name, q.sumgrades, qa.sumgrades \
                      FROM mdl_user_enrolments AS ue \
                      JOIN mdl_enrol AS e ON e.id=ue.enrolid \
                      JOIN mdl_course AS c ON c.id=e.courseid \
                      JOIN mdl_quiz AS q ON q.course=e.courseid \
                      JOIN mdl_quiz_attempts AS qa ON qa.quiz=q.id \
                      WHERE ue.userid=%s',user_id)
    results = cHandler.fetchall()

    cHandler.execute('SELECT ue.enrolid FROM mdl_user_enrolments AS ue WHERE ue.userid=%s ', user_id)
    user_enrol_id=cHandler.fetchall()
    print user_enrol_id
    cHandler.execute('SELECT e.courseid FROM mdl_enrol AS e WHERE ')
    results=user_enrol_id
    '''
    return render_template('information.html',  userinfo=userinfo,enrolinfo=enrolinfo,courseinfo=courseinfo,quizinfo=quizinfo,form_doexo=form_doexo)


@app.route('/doexo', methods=['GET', 'POST'])
@lti(request='session', error=error, app=app)
def do_exo(lti=lti):
    """ render the contents of the staff.html template
    :param lti: the `lti` object from `pylti`
    :return: the staff.html template rendered
    """
    courseid = request.form.get('courseid')
    print courseid

    current_nlevel=[3,3,4]
    nA_level=current_nlevel[0]
    nB_level=current_nlevel[1]
    nC_level=current_nlevel[2]
    print nA_level,nB_level,nC_level

    user_id=lti.user_id
    print user_id
    myDB = MySQLdb.connect(host="127.0.0.1",port=8889,user="moodle",passwd="moodle",db="moodle31")
    cHandler=myDB.cursor()
    cHandler.execute('SELECT q.name, q.sumgrades, qa.sumgrades FROM mdl_quiz AS q JOIN mdl_quiz_attempts AS qa ON q.id=qa.quiz WHERE (qa.userid=%s AND q.course=%s)',(user_id, courseid))
    quizinfo=cHandler.fetchall()
    print quizinfo

    cHandler.execute('SELECT roleid FROM mdl_role_assignments WHERE (userid=%s AND contextid=90)', user_id)
    user_role=cHandler.fetchall()
    print user_role

    cHandler.execute('SELECT ques.id, ques.questiontext, ques_a.answer,ques_a.fraction FROM mdl_question AS ques JOIN mdl_question_answers AS ques_a ON ques_a.question=ques.id WHERE ques.category=14')
    A_level_question_text =cHandler.fetchall()
    print  A_level_question_text
    print len(A_level_question_text)

    label=numpy.random.random((len(A_level_question_text),))
    print label

    #finalquestion=[]
    #finalquestion=func_finalexo(current_nlevel)
    #print finalquestion
    for i in range(0,len(A_level_question_text),4):
        print A_level_question_text[i][0],A_level_question_text[i][1]
        print "    ",A_level_question_text[i][2],A_level_question_text[i][3]
        print "    ",A_level_question_text[i+1][2],A_level_question_text[i+1][3]
        print "    ",A_level_question_text[i+2][2],A_level_question_text[i+2][3]
        print "    ",A_level_question_text[i+3][2],A_level_question_text[i+3][3]

    form_checkexo=Form_checkexo()
    if form_checkexo.validate_on_submit():
        print "button validate"

    return render_template('doexo.html', lti=lti,courseid=courseid,user_role=user_role,questions=A_level_question_text,label=label, form_checkexo=form_checkexo)


@app.route('/checkexo', methods=['GET', 'POST'])
@lti(request='session', error=error, app=app)
def check_exo(lti=lti):
    """ render the contents of the staff.html template
    :param lti: the `lti` object from `pylti`
    :return: the staff.html template rendered
    """

    qid=[]
    for i in range(0,10,1):
        qid.append(request.form.get((str(i)+".0")))
        print i,qid[i],"q"+str(i)
    print '45',request.values.get("45")
    #courseid = request.form.get('courseid')
    #print courseid

    notes={}
    i=0
    for id in qid:
        notes[id]=request.values.get(qid[i])
        i=i+1
    print notes

    myDB = MySQLdb.connect(host="127.0.0.1",port=8889,user="moodle",passwd="moodle",db="moodle31")
    cHandler=myDB.cursor()
    questions=[]
    for id in qid:

        cHandler.execute('SELECT ques.id, ques.questiontext, ques_a.answer,ques_a.fraction FROM mdl_question AS ques JOIN mdl_question_answers AS ques_a ON ques_a.question=ques.id WHERE ques.id=%s',id)
        result = cHandler.fetchall()
        questions.append(result)

    print questions

    return render_template('checkexo.html',notes=notes,qid=qid,questions=questions)


@app.route('/exos', methods=['GET', 'POST'])
@lti(request='session', error=error, app=app)
def tex_exos(lti=lti):
    #text = get_exo('123')
    #print text
    return render_template('tex_exos.html')




def func_finalexo(currnent_nlevel):
    pass



if __name__ == '__main__':
    app.run()
