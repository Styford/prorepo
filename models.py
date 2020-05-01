# -*- coding:utf-8 -*-
import datetime
from app import db

#__table_args__ = {'extend_existing': True}
#https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/table_config.html?highlight=__table_args__


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
  fkPeople = db.Column(db.Integer, db.ForeignKey("People.id"))
  dtAdded = db.Column(db.DateTime, default = datetime.datetime.utcnow)
  dtExpired = db.Column(db.DateTime, default = datetime.datetime.utcnow)
  sNrProtocol = db.Column(db.String(50), nullable = True)
  sNrCert = db.Column(db.String(50), nullable = True)
  __table_args__ = {'extend_existing': True}
  
class Files(db.Model):
  iId = db.Column(db.Integer, primary_key = True)
  fkPeople = db.Column(db.Integer, db.ForeignKey("People.id"))
  fkProject = db.Column(db.Integer, db.ForeignKey("Project.id"))
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
  fkPeople = db.Column(db.Integer, db.ForeignKey("People.id"))
  fkSkillName = db.Column(db.Integer, db.ForeignKey("SkillName.id"))
  __table_args__ = {'extend_existing': True}
  
class SkillName(db.Model):
  iId = db.Column(db.Integer, primary_key = True)
  sName = db.Column(db.String(255), nullable = False)
  __table_args__ = {'extend_existing': True}
  
class PeopleInProject(db.Model):
  iId = db.Column(db.Integer, primary_key = True)
  fkSkillName = db.Column(db.Integer, db.ForeignKey("SkillName.id"))
  fkPeople = db.Column(db.Integer, db.ForeignKey("People.id"))
  fkProject = db.Column(db.Integer, db.ForeignKey("Project.id"))
  __table_args__ = {'extend_existing': True}
 