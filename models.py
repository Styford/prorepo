# -*- coding:utf-8 -*-


#__table_args__ = {'extend_existing': True}
#https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/table_config.html?highlight=__table_args__

from flask_cors import CORS
from werkzeug.security import generate_password_hash,  check_password_hash
from datetime import datetime
from config import *
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager, UserMixin

app = Flask(__name__, static_folder='static/dist')
app.config.from_object(DevelopmentConfig)
#app.secret_key = 'some secret key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' +  DB_LOGIN + ':' + DB_PASSWORD + '@localhost/' + DATABASE_NAME
db = SQLAlchemy(app)
CORS(app)

login = LoginManager(app)

@login.user_loader
def load_user(id):
    return People.query.get(int(id))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sPlan = db.Column(db.String(20), unique=True, nullable=False)
    sDescription = db.Column(db.String(255), nullable=False)
    bActive = db.Column(db.Boolean)
    sPath = db.Column(db.String(255), nullable=False)
    bArchived = db.Column(db.Boolean, default=False)
    dtAdded = db.Column(db.DateTime(), default = datetime.utcnow)
    dtUpdate = db.Column(db.DateTime(), default = datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = {'extend_existing': True}
    def __repr__(self):
        return ("<Project %s>" % self.sTitle)



class Certs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fkPeople = db.Column(db.Integer, db.ForeignKey("people.id"))
    fkCertsDesc = db.Column(db.Integer, db.ForeignKey("certs_desc.id"))
    dtAdded = db.Column(db.DateTime(), default = datetime.utcnow)
    dtExpired = db.Column(db.DateTime(), default = datetime.utcnow)
    sNrProtocol = db.Column(db.String(50))
    sNrCert = db.Column(db.String(50))
    __table_args__ = {'extend_existing': True}



class CertsDesc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sDescription = db.Column(db.String(255))
    __table_args__ = {'extend_existing': True}
  


class Files(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fkPeople = db.Column(db.Integer, db.ForeignKey("people.id"))
    fkProject = db.Column(db.Integer, db.ForeignKey("project.id"))
    sDescription = db.Column(db.String(255))
    dtAdded = db.Column(db.DateTime(), default = datetime.utcnow)
    dtUpdate = db.Column(db.DateTime(), default = datetime.utcnow, onupdate=datetime.utcnow)
    sFullPath = db.Column(db.String(255))
    __table_args__ = {'extend_existing': True}
  

    
class People(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    iRole = db.Column(db.Integer)                   # 1 - Admin, 2 - User, 3 - Guest
    sPostion = db.Column(db.String(255))            # TODO: Перевести в справочник должностей
    sFirstName = db.Column(db.String(255))          # Имя
    sMiddleName = db.Column(db.String(255))         # Отчество 
    sLastName = db.Column(db.String(255))           # Фамилия
    sEmail = db.Column(db.String(255))              # Почта
    sPasswordHash = db.Column(db.String(255))       # Хеш пароля
    fkGroup = db.Column(db.Integer, db.ForeignKey("group.id"))  # Группа, отдел, сектор
    dtAdded = db.Column(db.DateTime(), default = datetime.utcnow) 
    dtUpdate = db.Column(db.DateTime(), default = datetime.utcnow, onupdate=datetime.utcnow)
    skills = db.relationship('Skill', backref = 'people', lazy = 'dynamic') # навыки
    inProjects = db.relationship('PeopleInProject', backref = 'people', lazy = 'dynamic') # участие в проектах
    __table_args__ = {'extend_existing': True}
  
    def __repr__(self):
        return ("<{} {}>".format(self.sFirstName, self.sLastName))
    
    def set_password(self, password):
        self.sPasswordHash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.sPasswordHash, password)

    def get_skills(self):
        dict_skills = {}
        for skill in self.skills:
            key = skill.fkSkillName
            dict_skills[key] = SkillName.query.get(key).sArea + " " + SkillName.query.get(key).sDescription
        return dict_skills
    
    def get_projects(self):
        dict_projects = {}
        for project in self.inProjects:
            dict_projects[project.fkProject] = Project.query.get(project.fkProject).sPlan
        return dict_projects


class Group(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sGroupName = db.Column(db.String(255))
    __table_args__ = {'extend_existing': True}
  


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fkPeople = db.Column(db.Integer, db.ForeignKey("people.id"))
    fkSkillName = db.Column(db.Integer, db.ForeignKey("skill_name.id"))
    __table_args__ = {'extend_existing': True}
  


class SkillName(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sDescription = db.Column(db.String(255), nullable=False)
    sArea = db.Column(db.String(255), nullable=False)
    __table_args__ = {'extend_existing': True}
  


class PeopleInProject(db.Model):
    fkSkillName = db.Column(db.Integer, db.ForeignKey("skill_name.id"), primary_key = True)
    fkPeople = db.Column(db.Integer, db.ForeignKey("people.id"), primary_key = True)
    fkProject = db.Column(db.Integer, db.ForeignKey("project.id"), primary_key = True)
    __table_args__ = {'extend_existing': True}
