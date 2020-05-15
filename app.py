# -*- coding:utf-8 -*-


#import configparsers
import os
from flask import Flask, jsonify, send_from_directory, request, redirect, url_for
from models import *
from flask_login import login_required, LoginManager, current_user, login_user
from config import PATHS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime

jwt = JWTManager(app)

def auth(email, password):
    user = People.query.filter_by(sEmail = email).first()
    if user:
        if user.check_password(password):
            return user

def identity(payload):
    email = payload['identity']
    return People.query.filter_by(sEmail = email).first()
        
        



@app.route('/admin/')
@login_required
def admin():
    return render_template('admin.html')


@app.route('/user/getcurrentuser', methods=['GET'])
def get_current_user():
    response_object = {'status': 'success'}
    print (current_user)
    if current_user.is_authenticated:
        response_object['current_user'] = current_user.sEmail;
    else:
        response_object['current_user'] = "Anonymous";
    return jsonify(response_object)
    
       
@app.route('/user/login', methods=['GET', 'POST'])
def login():    
    response_object = {'status': 'success'}
    if current_user.is_authenticated and 0:
        response_object['message'] = 'Allready authorized'
        return jsonify(response_object)
    if request.method == 'POST':
        post_data = request.get_json()
        user = auth(post_data.get('email'), post_data.get('password'))
        if user is None:
            response_object['status'] = 'error!'
            response_object['message'] = 'User not found or invalid password!'
            return jsonify(response_object)
        login_user(user, remember = True)
        access_token = create_access_token(identity = user.sEmail)
        response_object['current_user'] = user.sEmail;
        return jsonify(response_object)

@app.route('/user/registration', methods=['POST'])
def registration():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        user = People.query.filter_by(sEmail=post_data.get('email')).first()
        if user is None:
            user = People(sEmail = post_data.get('email'))
            user.set_password(post_data.get('password'))
            db.session.add(user)
            db.session.commit()
            response_object['message'] = 'Регистрация прошла успешно'
            login_user(user, remember = True)
            response_object['current_user'] = user.sEmail;
            return jsonify(response_object)
        else:
            response_object['status'] = 'error!'
            response_object['message'] = 'Пользователь с таким адресом уже существуюет'
            return jsonify(response_object)

@app.route('/user/update_myself', methods=['POST'])
@login_required
def update_myself():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if current_user.is_authenticated:
            if post_data.get('position'):
                current_user.sPosition = post_data.get('position')
            if post_data.get('firstName'):
                current_user.sFirstName = post_data.get('firstName')
            if post_data.get('middleName'):
                current_user.sMiddleName = post_data.get('middleName')
            if post_data.get('lastName'):
                current_user.sLastName = post_data.get('lastName')
            if post_data.get('group'):
                current_user.fkGroup = post_data.get('group')
            db.session.commit()    
            response_object['message'] = 'Обноваление прошло успешно'
            return jsonify(response_object)
        else:
            response_object['status'] = 'error!'
            response_object['message'] = 'Пройдите авторизацию'
            return jsonify(response_object)

@app.route('/')
def index():
    # тут просто пробрасываем файлик, без всякого препроцессинга
    print("we are there")
    return app.send_static_file("index.html")

@app.route('/dist/<path:path>')
def static_dist(path):
    # тут пробрасываем статику  
    return send_from_directory("../../proclient/dist", path)


@app.route("/api/skills/addname", methods=['POST'])
def add_skill_name():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if SkillName.query.filter_by(sDescription=post_data.get('description'), sArea=post_data.get('baseSoftware')).first():
            response_object['status'] = 'error!'
            response_object['message'] = 'Такой навык уже существует'
            return jsonify(response_object)
        else:
            newSkillName = SkillName(
                sDescription = post_data.get('description'), 
                sArea = post_data.get('area'),
                sBaseSoftware = post_data.get('baseSoftware')
                )
            db.session.add(newSkillName)
            db.session.commit()
            response_object['message'] = 'Новый навык добавлен'
            return jsonify(response_object)

@app.route("/api/skills/addskill", methods=['POST'])
def add_skill():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if Skill.query.filter_by(fkPeople=post_data.get('user_id'), fkSkillName=post_data.get('skill_id')):
            response_object['status'] = 'error!'
            response_object['message'] = 'Такой навык уже существует'
            return jsonify(response_object)
        newSkill = Skill(fkPeople = post_data.get('user_id'), fkSkillName = post_data.get('skill_id'))
        db.session.add(newSkill)
        db.session.commit()
        response_object['message'] = 'Новый навык добавлен'
        return jsonify(response_object)


@app.route("/api/certs/addname/", methods=['POST'])
def add_certs_name():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if CertsDesc.query.filter_by(sDescription=post_data.get('description')).first():
            response_object['status'] = 'error!'
            response_object['message'] = 'Такое удостоверение уже существует'
            return jsonify(response_object)
        else:
            newCertsDesc = CertsDesc(sDescription = post_data.get('description'))
            db.session.add(newCertsDesc)
            db.session.commit()
            response_object['message'] = 'Новое удостоверение добавлено'
            return jsonify(response_object)
        

@app.route("/api/certs/addcert/", methods=['POST'])
def add_cert():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if Certs.query.filter_by(fkPeople=post_data.get('user_id'), fkCertsDesc=post_data.get('description_id'), iProcessed=1).first():
            response_object['status'] = 'error!'
            response_object['message'] = 'Такое удостоверение уже существует'
            return jsonify(response_object)
        newCert = Certs(fkPeople = post_data.get('user_id'), fkCertsDesc = post_data.get('description_id'), iProcessed=1)
        db.session.add(newCert)
        db.session.commit()
        response_object['message'] = 'Новое удостоверение добавлено'
        return jsonify(response_object)

        
@app.route("/api/projects/pip/", methods=['POST'])
def people_in_project():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if PeopleInProject.query.filter_by(
        fkPeople=post_data.get('user_id'), 
        fkSkillName=post_data.get('skill_id'), 
        fkProject=post_data.get('project_id')
        ).first():
            response_object['status'] = 'error!'
            response_object['message'] = 'Такой навык уже существует'
            return jsonify(response_object)
        newPIP = PeopleInProject(
        fkSkillName = post_data.get('skill_id'),
        fkPeople = post_data.get('people_id'),
        fkProject = post_data.get('project_id')
        )
        db.session.add(newPIP)
        db.session.commit()
        response_object['message'] = 'Связь "Разработчик - Проект - Навык" добавлена'
        return jsonify(response_object)


########## Спека на вход функции create_project
#{
#"plan": "DDD.DD",
#"description": "Описание проекта",
#"folders": ["VU", "SU", "SUPPORT", "IO"],
#"developer": {
#    "1" : {	
#        "skill_id" : [8,9,10,11],
#        "developer_id" : 1
#  	},
#    "2" : {
#        "skill_id" : [12,13],
#        "developer_id" : 2
#	}
#}
#}

@app.route("/api/projects/create", methods=['POST'])
def create_project():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if Project.query.filter_by(sPlan=post_data.get('plan')).first():
            response_object['status'] = 'error!'
            response_object['message'] = 'Проект с таким планом уже существует'
            return jsonify(response_object)
        project_path = PATHS['repo'] + post_data.get('plan')
        newPrj = Project(
            sPlan = post_data.get('plan'),
            sDescription = post_data.get('description'),
            sPath = project_path
        )
        db.session.add(newPrj)
        db.session.flush()
        os.system("mkdir " + project_path)
        if post_data.get('folders'):
            for folder in post_data.get('folders'):
                print (folder)
                os.system("mkdir " + project_path + FD + folder)
                text = u'echo "Файл для пояснений работы/разворачивания ПО" >> ' + project_path + FD + folder + FD + "README.TXT"
                print(text)
                os.system(text)
        os.system("hg init " + project_path)
        os.system('echo "[trusted]" >>  ' + project_path + FD + ".hg" + FD + "hgrc")
        os.system('echo "users = root" >>  ' + project_path + FD + ".hg" + FD + "hgrc")
        os.system('echo "[ui]" >>  ' + project_path + FD + ".hg" + FD + "hgrc")        
        os.system('echo "username = ' + current_user.sEmail +  '" >> ' + project_path + '/.hg/hgrc')
        os.system('echo "[web]" >>  ' + project_path + FD + ".hg" + FD + "hgrc")
        os.system('echo "description = ' + post_data.get('description') +  '" >> ' + project_path + FD +'.hg' + FD + 'hgrc')
        os.system('echo "push_ssl = false" >> ' + project_path + '/.hg/hgrc')
        os.system('echo "allow_push = *" >> ' + project_path + '/.hg/hgrc')
        os.system('hg add ' + project_path)
        os.system('hg commit -u "syzsi" -m "init commit" ' + project_path)
        if post_data['developer']:
            for dev in post_data['developer'].values():
                for sk in dev['skill_id']:
                    newPIP = PeopleInProject(fkSkillName = sk, fkPeople = dev['developer_id'], fkProject = newPrj.id)
                    db.session.add(newPIP)
                    if not Skill.query.filter_by(fkPeople = dev['developer_id'], fkSkillName = sk).first():
                        db.session.add(Skill(fkPeople = dev['developer_id'], fkSkillName = sk))
                    db.session.flush()
        db.session.commit()
        response_object['message'] = 'Repo created!'
        return jsonify(response_object)


@app.route("/api/projects/get", methods=['GET'])
@login_required
def get_projects():
    response_object = {'status': 'success'}
    for prj in Project.query.all():
        response_object[prj.sPlan] = prj.get_object()
    return jsonify(response_object)  
    

@app.route("/api/projects/update", methods=['POST'])
def update_project():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if post_data.get('plan'):
            prj = Project.query.filter_by(sPlan = post_data.get('plan')).first()
            if post_data.get('description'): prj.sDescription = post_data.get('description')
            if post_data.get('active'): prj.bActive = post_data.get('active')
            if post_data.get('archived'): prj.bArchived = post_data.get('archived')
            for p in prj.PIP:
                db.session.delete(p)
            if post_data['developer']:
                for dev in post_data['developer'].values():
                    for sk in dev['skill_id']:
                        newPIP = PeopleInProject(fkSkillName = sk, fkPeople = dev['developer_id'], fkProject = prj.id)
                        db.session.add(newPIP)
                        if not Skill.query.filter_by(fkPeople = dev['developer_id'], fkSkillName = sk).first():
                            db.session.add(Skill(fkPeople = dev['developer_id'], fkSkillName = sk))
                        db.session.flush()
            db.session.commit()
            return jsonify(response_object)
            

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

