# -*- coding:utf-8 -*-

import datetime
import configparser
import os

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


DEBUG = True
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
IPADDRESS = "http://10.99.0.103/"
DATABASE_NAME = "postgres"
DB_LOGIN = 'postgres'
DB_PASSWORD = '123456'
PATHS = {
    'repo': '/var/lib/mercurial-server/repos/',
}

app = Flask(__name__, static_folder='static/dist')
app.config.from_object(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' +  DB_LOGIN + ':' + DB_PASSWORD + '@localhost/' + DATABASE_NAME
db = SQLAlchemy(app)
CORS(app)


class Project(db.Model):
  iId = db.Column(db.Integer, primary_key=True)
  sPlan = db.Column(db.String(20), unique=True, nullable=False)
  sTitle = db.Column(db.String(255), nullable=False)
  bActive = db.Column(db.Boolean)
  sPath = db.Column(db.String(255), nullable=False)
  __table_args__ = {'extend_existing': True}
  def __repr__(self):
    return ("<Project %s>" % self.sTitle)

class Certs(db.Model):
  iId = db.Column(db.Integer, primary_key=True)
  fkPeople = db.Column(db.Integer, db.ForeignKey("people.iId"))
  dtAdded = db.Column(db.DateTime, default = datetime.datetime.utcnow)
  dtExpired = db.Column(db.DateTime, default = datetime.datetime.utcnow)
  sNrProtocol = db.Column(db.String(50), nullable = True)
  sNrCert = db.Column(db.String(50), nullable = True)
  __table_args__ = {'extend_existing': True}
  
class Files(db.Model):
  iId = db.Column(db.Integer, primary_key = True)
  fkPeople = db.Column(db.Integer, db.ForeignKey("people.iId"))
  fkProject = db.Column(db.Integer, db.ForeignKey("project.iId"))
  sDescription = db.Column(db.String(255), nullable = False)
  dtAdded = db.Column(db.DateTime, default = datetime.datetime.utcnow)
  dtChanged = db.Column(db.DateTime)
  sFullPath = db.Column(db.String(255), nullable = False)
  __table_args__ = {'extend_existing': True}
  
class People(db.Model):
  iId = db.Column(db.Integer, primary_key = True)
  sPostion = db.Column(db.String(255), nullable = False)
  dtAdded = db.Column(db.DateTime, default = datetime.datetime.utcnow)
  __table_args__ = {'extend_existing': True}
  
class Skill(db.Model):
  iId = db.Column(db.Integer, primary_key = True)
  fkPeople = db.Column(db.Integer, db.ForeignKey("people.iId"))
  fkSkillName = db.Column(db.Integer, db.ForeignKey("skill_name.iId"))
  __table_args__ = {'extend_existing': True}
  
class SkillName(db.Model):
  iId = db.Column(db.Integer, primary_key = True)
  sName = db.Column(db.String(255), nullable = False)
  __table_args__ = {'extend_existing': True}
  
class PeopleInProject(db.Model):
  iId = db.Column(db.Integer, primary_key = True)
  fkSkillName = db.Column(db.Integer, db.ForeignKey("skill_name.iId"))
  fkPeople = db.Column(db.Integer, db.ForeignKey("people.iId"))
  fkProject = db.Column(db.Integer, db.ForeignKey("project.iId"))
  __table_args__ = {'extend_existing': True}



@app.route('/')
def index():
    # тут просто пробрасываем файлик, без всякого препроцессинга
    return app.send_static_file("index.html")

@app.route('/dist/<path:path>')
def static_dist(path):
    # тут пробрасываем статику  
    return send_from_directory("static/dist", path)

@app.route("/api/projects/create", methods=['POST'])
def create_project():
  response_object = {'status': 'success'}
  if request.method == 'POST':
    post_data = request.get_json()
    project_path = PATHS['repo'] + post_data.get('plan')
    newprj = Project(
      plan = post_data.get('plan'),
      title = post_data.get('description'),
      author = post_data.get('users'),
      path = project_path,
      active = True
    )
    db.session.add(newprj)
    db.session.commit()    
    os.system("mkdir " + project_path)
    if post_data.get('folders'):
        for folder in post_data.get('folders'):
            print (folder)
            os.system("mkdir " + project_path + "/" + folder)
            os.system('echo "Файл для пояснений работы/разворачивания ПО" >> ' + project_path + "/" + folder + "/README.TXT")
    os.system("hg init " + project_path)
    os.system('echo "[ui]" >>  ' + project_path + "/.hg/hgrc")
    os.system('echo "username = ' + post_data.get('users') +  '" >> ' + project_path + '/.hg/hgrc')
    os.system('hg commit -u "syzsi" -m "init commit" ' + project_path)
    response_object['message'] = 'Repo created!'
  return jsonify(response_object)

@app.route("/api/projects/get", methods=['GET'])
def get_projects():
  prjs = []
  for p in Project.query.all():
    prj = {}
    prj["description"] = p.title
    prj["plan"] = p.plan
    prj["users"] = p.author
    prjs.append(prj)
  return jsonify({'prjs' : prjs})  
    
@app.route("/api/projects/update", methods=['GET'])
def update_projects():
  config = configparser.ConfigParser()
  prjs = []
  for plan in os.listdir(PATHS['repo']):
    hgrc_file = PATHS['repo'] + plan + "/.hg/hgrc"
    if os.access(hgrc_file, os.F_OK):
      prj = {}
      config.read(hgrc_file)
      try:
        prj["plan"] = plan
        prj["users"] = config.get("ui","username")
        prj["description"] = config.get("web","description")
        prjs.append(prj)
        print("added")
        existPrj = Project.query.filter(Project.plan==plan).first()
        if existPrj:
          existPrj.author = config.get("ui","username")
          existPrj.title = config.get("web","description")
          existPrj.path = config.get("paths","default")
        else:
          newprj = Project(
            plan = plan,
            title = config.get("web","description"),
            author = config.get("ui","username"),
            active = True,
            path = IPADDRESS + plan)
          db.session.add(newprj)
        db.session.commit()
      except:
        print("Ошибка чтения конфигурации")       
  return jsonify({'prjs' : prjs})

@app.route("/api/projects/delete", methods=['GET'])
def delete_project():
  response_object = {'status': 'success'}
  if request.method == 'GET':
    get_data = request.get_json()
    prj = Project.query.filter(Project.plan == get_data.get('plan')).first()
    if prj:
      db.session.delete(prj)
      db.session.commit()
  response_object['message'] = 'Repo deleted!'
  return jsonify(response_object)
  
if __name__ == '__main__':
    app.run(host='0.0.0.0')

