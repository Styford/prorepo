# -*- coding:utf-8 -*-


import configparser
import os
from models import app, db
from flask import Flask, jsonify, send_from_directory, request, redirect, url_for
from models import People
from flask_login import login_required, LoginManager
from flask_login import current_user, login_user




@app.route('/admin/')
@login_required
def admin():
    return render_template('admin.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    
    response_object = {'status': 'success'}
    if current_user.is_authenticated:
        response_object['message'] = 'Allready authorized'
        return jsonify(response_object)
    if request.method == 'POST':
        post_data = request.get_json()
        user = People.query.filter_by(sEmail=post_data.get('email')).first()
        if user is None or not user.check_password(post_data.get('password')):
            response_object['status'] = 'error!'
            response_object['message'] = 'User not found or invalid password!'
            return jsonify(response_object)
        login_user(user, remember = True)
        return jsonify(response_object)

@app.route('/registration/', methods=['POST'])
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
            return jsonify(response_object)
        else:
            response_object['status'] = 'error!'
            response_object['message'] = 'Пользователь с таким адресом уже существуюет'
            return jsonify(response_object)

@app.route('/update_myself/', methods=['POST'])
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

