<<<<<<< HEAD
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    priority = db.Column(db.String(20))
    duration = db.Column(db.Integer)
    deadline = db.Column(db.DateTime)
    category = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Pending")
=======
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    priority = db.Column(db.String(20))
    duration = db.Column(db.Integer)
    deadline = db.Column(db.DateTime)
    category = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Pending")
>>>>>>> fa706b1b96a925328b3b1aff641e7b0d1fcd484d
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))