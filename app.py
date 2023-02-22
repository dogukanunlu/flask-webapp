from flask import Flask, request, jsonify, render_template, make_response, session, redirect
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import re
import uuid
import hashlib
import os
import subprocess
import json
import random

app = Flask(__name__, template_folder="/home/labris/myproject/templates", static_folder="/home/labris/myproject/static")
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://dogukan:labris@localhost:5432/mydb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
db = SQLAlchemy(app)
ma = Marshmallow(app)
db.init_app(app)
patternForMail = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
patternForPassword = re.compile('^(?=.*[A-Za-z])(?=.*[0-9])[A-Za-z0-9]{8,}$')

class userInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    firstname = db.Column(db.String(400), nullable=False)
    middlename = db.Column(db.String(400), nullable=True)
    lastname = db.Column(db.String(400), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    email = db.Column(db.String(400), nullable=False)
    password = db.Column(db.String(400), nullable=False)

    def __repr__(self):
        return self.id


class onlineUserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    ipaddress = db.Column(db.String(400), nullable=False)
    logindatetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return self.id


class userInfoSchema(ma.Schema):
    class Meta:
        model = userInfo
        fields = ('id', 'username', 'firstname', 'middlename', 'lastname', 'birthdate', 'email', 'password')

class onlineUserInfoSchema(ma.Schema):
    class Meta:
        model = onlineUserInfo
        fields = ('id', 'username', 'ipaddress', 'password', 'logindatetime')


userInfo_schema = userInfoSchema(many=False)
userInfos_schema = userInfoSchema(many=True)
onlineUserInfos_schema = onlineUserInfoSchema(many=True)

class log(Resource):
    def get(self):
        try:
            log = ""
            with open('/var/log/nginx/access.log', "r") as file:
                log += file.read()
            return jsonify({'logs': log})
        except:
            return jsonify({'error': 'error'})

class base(Resource):
    def get(self):
        header = {'Content-Type': "text/html"}
        return make_response(render_template('home.html'), 200)

class admin(Resource):
    def get(self):
        if(session.get("onlineusername")!="admin"):
            print(session.get("onlineusername"))
            return redirect(f"/user/home")
        header = {'Content-Type': "text/html"}
        return make_response(render_template('admin.html'), 200)

class upPage(Resource):
    def get(self):

        if not session.get('onlineusername'):
            return redirect(f"/")
        header = {'Content-Type': "text/html"}
        return make_response(render_template('update.html'), 200)


class userPage(Resource):
    def get(self):
        if not session.get('onlineusername'):
            return redirect(f"/")
        header = {'Content-Type': "text/html"}
        return make_response(render_template('user.html'), 200)

class signup(Resource):
    def get(self):
        header = {'Content-Type': "text/html"}
        return make_response(render_template('signup.html'), 200)

class onlineusers(Resource):
    def get(self):
        if(session.get("onlineusername")!="admin"):
            return redirect(f"/")
        users = db.session.query(onlineUserInfo).all()
        result_set = onlineUserInfos_schema.dump(users)
        return jsonify(result_set)

class login(Resource):
    def post(self):
        try:
            onlineusername = request.json['username']
            password = request.json['password']
            ip = request.remote_addr
            userLogin= userInfo.query.filter_by(username=onlineusername).first()
            userId=userLogin.id
            checkLogin = onlineUserInfo.query.filter_by(username=onlineusername).first()
            if(matchHashedPassword(userLogin.password,password)):
                session['onlineusername']=onlineusername
                if (checkLogin is not None):
                    print(userId)
                    return {"Succes": "User Login","userId":userId}, 200
                else:
                    new_online_user = onlineUserInfo(id=userId, username=onlineusername, ipaddress=ip, logindatetime=datetime.now())
                    db.session.add(new_online_user)
                    db.session.commit()
                    print(userId)
                    return {"message":"succes","userId":userId,"userName":onlineusername},200
        except Exception as e:
            print(password)
            print(userLogin.password)
            return {"Error": "Invalid user info."},404


class logout(Resource):
    def delete(self, id):
        session.clear()
        userLogin = onlineUserInfo.query.get_or_404(int(id))
        print(id)
        db.session.delete(userLogin)
        db.session.commit()
        return {"Succes": "User Deleted"},200



class user(Resource):
    def get(self):

        if(session.get("onlineusername")!="admin"):
            return redirect(f"/")
        users = db.session.query(userInfo).all()
        result_set = userInfos_schema.dump(users)
        return jsonify(result_set)


class update(Resource):
    def put(self, id):
        if not session.get('onlineusername'):
            return redirect(f"/")
        userUpdate = db.session.query(userInfo).get_or_404(int(id))
        password = request.json['password']
        email = request.json['email']
        passMatch = patternForPassword.search(password)
        password = hashPassword(password)
        mailMatch = patternForMail.search(email)
        if (mailMatch is not None and passMatch is not None):
            userUpdate.username = request.json['username']
            userUpdate.firstname = request.json['firstname']
            userUpdate.middlename = request.json['middlename']
            userUpdate.lastname = request.json['lastname']
            userUpdate.birthdate = request.json['birthdate']
            userUpdate.email = email
            userUpdate.password = password
            db.session.commit()
            return {"message":"success"}
        else:
            if (mailMatch is None):
                return jsonify({"Error": "Invalid email."})
            if (passMatch is None):
                return jsonify({"Error": "Invalid password."})

class delete(Resource):
    def delete(self, id):
        if not session.get('onlineusername'):
            return redirect(f"/")
        userDelete = userInfo.query.get_or_404(int(id))
        db.session.delete(userDelete)
        db.session.commit()
        return jsonify({"Succes": "User Deleted"})


def hashPassword(text):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + text.encode()).hexdigest() + ':' + salt

def matchHashedPassword(hashedText, providedText):
    _hashedText, salt = hashedText.split(':')
    return _hashedText == hashlib.sha256(salt.encode() + providedText.encode()).hexdigest()


class create(Resource):
    def post(self):
        print(request.json)
        try:
            username = request.json['username']
            firstname = request.json['firstname']
            middlename = request.json['middlename']
            lastname = request.json['lastname']
            birthdate = request.json['birthdate']
            email = request.json['email']
            password = request.json['password']
            passMatch = patternForPassword.search(password)
            password=hashPassword(password)
            mailMatch = patternForMail.search(email)
            if(mailMatch is not None and passMatch is not None):
                new_user = userInfo(username=username, firstname=firstname, middlename=middlename, lastname=lastname,
                                    birthdate=birthdate, email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                return userInfo_schema.jsonify(new_user)
            else:
                if(mailMatch is None):
                    return jsonify({"Error": "Invalid email."})
                if(passMatch is None):
                    return jsonify({"Error": "Invalid password."})
        except Exception as e:
            return jsonify({"Error": "Invalid request."})



api.add_resource(onlineusers, '/onlineusers')
api.add_resource(base, '/')
api.add_resource(admin, '/admin')
api.add_resource(upPage, '/user/update')
api.add_resource(signup, '/signup')
api.add_resource(login, '/login')
api.add_resource(user, '/user/list')
api.add_resource(userPage, '/user/home')
api.add_resource(update, '/user/update/<int:id>')
api.add_resource(logout, '/logout/<int:id>')
api.add_resource(create, '/user/create')
api.add_resource(delete, '/user/delete/<int:id>')
api.add_resource(log, '/log')
if __name__ == "__main__":
    app.run(debug=True,host ="0.0.0.0")



